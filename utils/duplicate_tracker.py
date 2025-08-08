"""
Gestionnaire pour éviter les doublons d'envoi de messages
"""

import json
import hashlib
from pathlib import Path
from typing import Set, List, Optional
from datetime import datetime
import os

class DuplicateTracker:
    """Classe pour gérer les numéros déjà contactés et éviter les doublons"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialise le tracker de doublons
        
        Args:
            config_dir: Répertoire de configuration, par défaut ~/.insam_message/
        """
        if config_dir is None:
            config_dir = Path.home() / ".insam_message"
        
        self.config_dir = config_dir
        self.config_dir.mkdir(exist_ok=True)
        
        self.sent_file = self.config_dir / "sent_numbers.json"
        self._sent_data = self._load_sent_data()
    
    def _load_sent_data(self) -> dict:
        """Charge les données des numéros déjà contactés"""
        try:
            if self.sent_file.exists():
                with open(self.sent_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"sent_numbers": {}, "last_updated": None}
        except Exception as e:
            print(f"Erreur lors du chargement des données: {e}")
            return {"sent_numbers": {}, "last_updated": None}
    
    def _save_sent_data(self):
        """Sauvegarde les données des numéros contactés"""
        try:
            self._sent_data["last_updated"] = datetime.now().isoformat()
            with open(self.sent_file, 'w', encoding='utf-8') as f:
                json.dump(self._sent_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalise un numéro de téléphone"""
        # Supprimer les espaces et caractères spéciaux
        normalized = ''.join(filter(str.isdigit, str(phone)))
        return normalized
    
    def _create_message_hash(self, message: str, image_path: Optional[str] = None) -> str:
        """Crée un hash unique pour un message + image"""
        content = message
        if image_path and os.path.exists(image_path):
            # Ajouter la taille du fichier image pour identifier l'image
            try:
                file_size = os.path.getsize(image_path)
                content += f"_img_{file_size}"
            except:
                content += f"_img_{image_path}"
        
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:12]
    
    def is_already_sent(self, phone: str, message: str, image_path: Optional[str] = None) -> bool:
        """
        Vérifie si ce message a déjà été envoyé à ce numéro
        
        Args:
            phone: Numéro de téléphone
            message: Contenu du message
            image_path: Chemin de l'image (optionnel)
            
        Returns:
            True si déjà envoyé, False sinon
        """
        normalized_phone = self._normalize_phone(phone)
        message_hash = self._create_message_hash(message, image_path)
        
        phone_data = self._sent_data["sent_numbers"].get(normalized_phone, {})
        return message_hash in phone_data.get("message_hashes", [])
    
    def mark_as_sent(self, phone: str, message: str, image_path: Optional[str] = None, success: bool = True):
        """
        Marque un message comme envoyé
        
        Args:
            phone: Numéro de téléphone
            message: Contenu du message
            image_path: Chemin de l'image (optionnel)
            success: Si l'envoi a réussi
        """
        if not success:
            return  # Ne pas marquer les échecs
        
        normalized_phone = self._normalize_phone(phone)
        message_hash = self._create_message_hash(message, image_path)
        
        if normalized_phone not in self._sent_data["sent_numbers"]:
            self._sent_data["sent_numbers"][normalized_phone] = {
                "message_hashes": [],
                "last_sent": None,
                "total_sent": 0
            }
        
        phone_data = self._sent_data["sent_numbers"][normalized_phone]
        
        if message_hash not in phone_data["message_hashes"]:
            phone_data["message_hashes"].append(message_hash)
            phone_data["last_sent"] = datetime.now().isoformat()
            phone_data["total_sent"] += 1
            
            self._save_sent_data()
    
    def get_sent_numbers_count(self) -> int:
        """Retourne le nombre de numéros déjà contactés"""
        return len(self._sent_data["sent_numbers"])
    
    def get_total_messages_sent(self) -> int:
        """Retourne le nombre total de messages envoyés"""
        total = 0
        for phone_data in self._sent_data["sent_numbers"].values():
            total += phone_data.get("total_sent", 0)
        return total
    
    def filter_unsent_numbers(self, phones_messages: List[tuple]) -> List[tuple]:
        """
        Filtre les numéros pour ne garder que ceux pas encore contactés
        
        Args:
            phones_messages: Liste de tuples (phone, message, image_path)
            
        Returns:
            Liste filtrée sans les doublons
        """
        filtered = []
        duplicates = []
        
        for phone, message, image_path in phones_messages:
            if not self.is_already_sent(phone, message, image_path):
                filtered.append((phone, message, image_path))
            else:
                duplicates.append(phone)
        
        return filtered, duplicates
    
    def reset_sent_history(self):
        """Remet à zéro l'historique des envois"""
        self._sent_data = {"sent_numbers": {}, "last_updated": None}
        self._save_sent_data()
    
    def get_phone_history(self, phone: str) -> Optional[dict]:
        """
        Récupère l'historique d'un numéro spécifique
        
        Args:
            phone: Numéro de téléphone
            
        Returns:
            Dictionnaire avec l'historique ou None
        """
        normalized_phone = self._normalize_phone(phone)
        return self._sent_data["sent_numbers"].get(normalized_phone)
    
    def export_sent_numbers(self, file_path: str):
        """Exporte la liste des numéros contactés vers un fichier"""
        try:
            export_data = {
                "exported_on": datetime.now().isoformat(),
                "total_numbers": self.get_sent_numbers_count(),
                "total_messages": self.get_total_messages_sent(),
                "numbers": []
            }
            
            for phone, data in self._sent_data["sent_numbers"].items():
                export_data["numbers"].append({
                    "phone": phone,
                    "total_sent": data.get("total_sent", 0),
                    "last_sent": data.get("last_sent"),
                    "messages_count": len(data.get("message_hashes", []))
                })
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise Exception(f"Erreur lors de l'export: {e}")