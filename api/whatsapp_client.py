# -*- coding: utf-8 -*-
"""
Client API WhatsApp avec support threading et gestion d'erreurs avancée
"""
import requests
import base64
import os
import time
from typing import Dict, List, Optional, Tuple, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from utils.logger import logger
from utils.validators import PhoneValidator


@dataclass
class MessageResult:
    """Résultat d'envoi de message"""
    phone: str
    success: bool
    error: Optional[str] = None
    response_data: Optional[Dict] = None
    message_type: str = "text"


class RateLimiter:
    """Gestionnaire de limitation de débit"""
    
    def __init__(self, calls_per_second: float = 1.0):
        self.min_interval = 1.0 / calls_per_second
        self.last_call_time = 0
    
    def wait_if_needed(self):
        """Attend si nécessaire pour respecter la limite"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.min_interval:
            sleep_time = self.min_interval - time_since_last_call
            time.sleep(sleep_time)
        
        self.last_call_time = time.time()


class WhatsAppClient:
    """Client API WhatsApp UltraMsg avec support avancé"""
    
    def __init__(self, instance_id: str, token: str, rate_limit: float = 1.0):
        self.instance_id = instance_id
        self.token = token
        self.rate_limiter = RateLimiter(rate_limit)
        self.base_url = f"https://api.ultramsg.com/{instance_id}"
        
        # Configuration des timeouts
        self.text_timeout = 30
        self.image_timeout = 90
        
        # Types MIME supportés
        self.mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp'
        }
    
    def test_connection(self, test_phone: str) -> Tuple[bool, str]:
        """Teste la connexion API avec un numéro"""
        try:
            # Valider le numéro
            if not PhoneValidator.is_valid_phone(test_phone):
                return False, "Numéro de téléphone invalide"
            
            formatted_phone = PhoneValidator.format_for_whatsapp(test_phone)
            
            # Message de test
            test_message = "🧪 Test de connexion API - Votre configuration fonctionne correctement !"
            
            result = self.send_text_message(formatted_phone, test_message)
            
            if result.success:
                logger.log_api_test(True, formatted_phone)
                return True, "Test réussi ! L'API est fonctionnelle."
            else:
                logger.log_api_test(False, formatted_phone, result.error)
                return False, f"Test échoué: {result.error}"
        
        except Exception as e:
            error_msg = f"Erreur lors du test: {str(e)}"
            logger.log_api_test(False, test_phone, error_msg)
            return False, error_msg
    
    def send_text_message(self, phone: str, message: str) -> MessageResult:
        """Envoie un message texte"""
        try:
            self.rate_limiter.wait_if_needed()
            
            url = f"{self.base_url}/messages/chat"
            payload = {
                'token': self.token,
                'to': phone,
                'body': message
            }
            
            response = requests.post(url, data=payload, timeout=self.text_timeout)
            
            if response.status_code == 200:
                result_data = response.json()
                success = result_data.get('sent', False)
                
                if success:
                    logger.log_message_sent(phone, True, "text")
                    return MessageResult(phone, True, response_data=result_data)
                else:
                    error = result_data.get('message', 'Échec d\'envoi inconnu')
                    logger.log_message_sent(phone, False, "text", error)
                    return MessageResult(phone, False, error=error, response_data=result_data)
            else:
                error = f"Erreur HTTP {response.status_code}: {response.text}"
                logger.log_message_sent(phone, False, "text", error)
                return MessageResult(phone, False, error=error)
        
        except requests.exceptions.Timeout:
            error = "Timeout lors de l'envoi"
            logger.log_message_sent(phone, False, "text", error)
            return MessageResult(phone, False, error=error)
        except requests.exceptions.RequestException as e:
            error = f"Erreur réseau: {str(e)}"
            logger.log_message_sent(phone, False, "text", error)
            return MessageResult(phone, False, error=error)
        except Exception as e:
            error = f"Erreur inattendue: {str(e)}"
            logger.log_message_sent(phone, False, "text", error)
            return MessageResult(phone, False, error=error)
    
    def send_image_message(self, phone: str, image_path: str, caption: str = "") -> MessageResult:
        """Envoie un message avec image"""
        try:
            # Vérifier que le fichier existe
            if not os.path.exists(image_path):
                error = "Fichier image introuvable"
                logger.log_message_sent(phone, False, "image", error)
                return MessageResult(phone, False, error=error, message_type="image")
            
            # Vérifier la taille du fichier (limite 5MB)
            file_size = os.path.getsize(image_path)
            if file_size > 5 * 1024 * 1024:
                error = f"Fichier trop volumineux: {file_size / 1024 / 1024:.1f}MB (max 5MB)"
                logger.log_message_sent(phone, False, "image", error)
                return MessageResult(phone, False, error=error, message_type="image")
            
            self.rate_limiter.wait_if_needed()
            
            # Encoder l'image en base64
            with open(image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Déterminer le type MIME
            file_extension = os.path.splitext(image_path)[1].lower()
            mime_type = self.mime_types.get(file_extension, 'image/jpeg')
            
            url = f"{self.base_url}/messages/image"
            payload = {
                'token': self.token,
                'to': phone,
                'image': f"data:{mime_type};base64,{image_base64}",
                'caption': caption
            }
            
            response = requests.post(url, data=payload, timeout=self.image_timeout)
            
            if response.status_code == 200:
                result_data = response.json()
                success = result_data.get('sent', False)
                
                if success:
                    logger.log_message_sent(phone, True, "image")
                    return MessageResult(phone, True, response_data=result_data, message_type="image")
                else:
                    error = result_data.get('message', 'Échec d\'envoi d\'image inconnu')
                    logger.log_message_sent(phone, False, "image", error)
                    return MessageResult(phone, False, error=error, response_data=result_data, message_type="image")
            else:
                error = f"Erreur HTTP {response.status_code}: {response.text}"
                logger.log_message_sent(phone, False, "image", error)
                return MessageResult(phone, False, error=error, message_type="image")
        
        except Exception as e:
            error = f"Erreur lors de l'envoi d'image: {str(e)}"
            logger.log_message_sent(phone, False, "image", error)
            return MessageResult(phone, False, error=error, message_type="image")
    
    def send_bulk_messages(
        self, 
        messages: List[Tuple[str, str, Optional[str]]], 
        max_workers: int = 3,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[MessageResult]:
        """
        Envoie des messages en masse avec threading
        
        Args:
            messages: Liste de tuples (phone, text_message, image_path)
            max_workers: Nombre maximum de threads
            progress_callback: Fonction appelée avec (completed, total)
        """
        results = []
        start_time = time.time()
        
        logger.info("bulk_send_started", total_messages=len(messages), max_workers=max_workers)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Soumettre toutes les tâches
            future_to_message = {}
            
            for phone, message, image_path in messages:
                # Valider et formater le numéro
                if not PhoneValidator.is_valid_phone(phone):
                    results.append(MessageResult(phone, False, "Numéro invalide"))
                    continue
                
                formatted_phone = PhoneValidator.format_for_whatsapp(phone)
                
                if image_path and os.path.exists(image_path):
                    future = executor.submit(self.send_image_message, formatted_phone, image_path, message)
                else:
                    future = executor.submit(self.send_text_message, formatted_phone, message)
                
                future_to_message[future] = (formatted_phone, message, image_path)
            
            # Collecter les résultats
            completed = 0
            for future in as_completed(future_to_message):
                result = future.result()
                results.append(result)
                completed += 1
                
                if progress_callback:
                    progress_callback(completed, len(messages))
        
        # Calculer les statistiques
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        duration = time.time() - start_time
        
        logger.log_bulk_send_completed(len(messages), successful, failed, duration)
        
        return results
    
    def get_sending_statistics(self, results: List[MessageResult]) -> Dict:
        """Génère des statistiques d'envoi"""
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        
        # Grouper les erreurs
        error_counts = {}
        for result in results:
            if not result.success and result.error:
                error_counts[result.error] = error_counts.get(result.error, 0) + 1
        
        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'error_breakdown': error_counts
        }