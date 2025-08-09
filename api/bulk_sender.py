# -*- coding: utf-8 -*-
"""
Gestionnaire d'envoi en masse optimisé pour de gros volumes (10k+ messages)
"""
import time
import threading
from typing import List, Dict, Callable, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import queue
import gc
from utils.logger import logger
from api.whatsapp_client import WhatsAppClient, MessageResult


@dataclass
class SendingSession:
    """Session d'envoi avec état persistant"""
    session_id: str
    total_messages: int
    completed: int = 0
    successful: int = 0
    failed: int = 0
    current_batch: int = 0
    start_time: float = 0
    paused: bool = False
    cancelled: bool = False
    error_messages: List[dict] = None
    
    def __post_init__(self):
        if self.error_messages is None:
            self.error_messages = []


class BulkSender:
    """Gestionnaire d'envoi en masse optimisé pour de gros volumes"""
    
    def __init__(self, whatsapp_client: WhatsAppClient, batch_size: int = 50):
        self.client = whatsapp_client
        self.batch_size = batch_size
        self.sessions_dir = Path.home() / ".excel_whatsapp" / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration pour gros volumes - OPTIMISÉE ET SÉCURISÉE
        self.max_workers = 1  # 1 seul thread pour éviter la surcharge
        self.batch_delay = 2.0  # 2 secondes entre les batches (au lieu de 5)
        self.retry_attempts = 2
        self.memory_cleanup_interval = 100  # Nettoyer la mémoire tous les 100 messages
        
        # Configuration des limites et pauses - OPTIMISÉE MAIS SÉCURISÉE
        self.max_daily_limit = None  # Pas de limite quotidienne
        self.message_burst_limit = 1  # 1 message avant pause (pour respecter le délai de 5 min)
        self.burst_pause_duration = 30  # 30 secondes entre chaque série (au lieu de 60)
        self.message_delay = 300.0  # 5 minutes entre chaque message
        
        # État de l'envoi
        self.current_session: Optional[SendingSession] = None
        self.is_paused = False
        self.is_cancelled = False
        self.progress_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        self.sent_numbers: Set[str] = set()  # Numéros déjà contactés
        self.sent_numbers_file = Path.home() / ".excel_whatsapp" / "sent_numbers.json"
        
        # File d'attente pour les résultats
        self.results_queue = queue.Queue()
        self.lock = threading.Lock()
        
        # Charger les numéros déjà contactés et la configuration
        self._load_sent_numbers()
        self._load_sending_config()
    
    def configure_sending_parameters(self, 
                                   message_delay: float = None,
                                   burst_limit: int = None, 
                                   burst_pause: int = None):
        """Configure les paramètres d'envoi pour ajuster la vitesse"""
        if message_delay is not None:
            self.message_delay = max(1.0, message_delay)  # Minimum 1 seconde
            
        if burst_limit is not None:
            self.message_burst_limit = max(1, burst_limit)  # Minimum 1 message
            
        if burst_pause is not None:
            self.burst_pause_duration = max(5, burst_pause)  # Minimum 5 secondes
        
        # Sauvegarde automatique des paramètres
        self._save_sending_config()
            
        logger.info("bulk_sender_config_updated",
                   message_delay=self.message_delay,
                   burst_limit=self.message_burst_limit,
                   burst_pause=self.burst_pause_duration)
    
    def get_sending_configuration(self) -> dict:
        """Retourne la configuration actuelle d'envoi"""
        return {
            "message_delay": self.message_delay,
            "burst_limit": self.message_burst_limit,
            "burst_pause_duration": self.burst_pause_duration,
            "batch_delay": self.batch_delay,
            "batch_size": self.batch_size
        }
    
    def send_bulk_optimized(
        self,
        messages_data: List[Tuple[str, str, Optional[str]]],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        status_callback: Optional[Callable[[str], None]] = None,
        resume_session_id: Optional[str] = None
    ) -> SendingSession:
        """
        Envoi optimisé pour de gros volumes avec batch processing
        
        Args:
            messages_data: Liste des messages (phone, text, image_path)
            progress_callback: Callback de progression (completed, total, status)
            status_callback: Callback de statut (message)
            resume_session_id: ID de session pour reprendre un envoi
        """
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        
        # Filtrer les numéros déjà contactés
        filtered_messages = self._filter_already_sent(messages_data)
        
        # Plus de limite quotidienne
        if self.max_daily_limit and len(filtered_messages) > self.max_daily_limit:
            self._update_status(f"Limite de {self.max_daily_limit} messages appliquée")
            filtered_messages = filtered_messages[:self.max_daily_limit]
        
        # Créer ou reprendre une session
        if resume_session_id:
            session = self._load_session(resume_session_id)
            if not session:
                raise ValueError(f"Session {resume_session_id} introuvable")
        else:
            session_id = f"bulk_send_{int(time.time())}"
            session = SendingSession(
                session_id=session_id,
                total_messages=len(filtered_messages),
                start_time=time.time()
            )
        
        self.current_session = session
        
        try:
            logger.info("bulk_send_started_optimized", 
                       session_id=session.session_id,
                       total=session.total_messages,
                       batch_size=self.batch_size)
            
            # Diviser en batches
            batches = self._create_batches(filtered_messages, session.current_batch)
            
            for batch_num, batch in enumerate(batches, start=session.current_batch):
                if self.is_cancelled:
                    break
                
                while self.is_paused and not self.is_cancelled:
                    time.sleep(0.1)
                
                session.current_batch = batch_num
                self._save_session(session)
                
                self._update_status(f"Traitement du batch {batch_num + 1}/{len(batches) + session.current_batch}")
                
                # Traiter le batch avec contrôle de limite
                batch_results = self._process_batch_with_limits(batch, batch_num)
                self._update_session_with_results(session, batch_results)
                
                # Nettoyer la mémoire périodiquement
                if batch_num % 10 == 0:
                    gc.collect()
                
                # Délai entre les batches pour éviter la surcharge
                if batch_num < len(batches) - 1:
                    time.sleep(self.batch_delay)
            
            # Finaliser la session
            session.cancelled = self.is_cancelled
            duration = time.time() - session.start_time
            
            logger.log_bulk_send_completed(
                session.total_messages, 
                session.successful, 
                session.failed, 
                duration
            )
            
            # Sauvegarder l'état final et les numéros contactés
            self._save_session(session)
            self._save_sent_numbers()
            
            return session
            
        except Exception as e:
            logger.error("bulk_send_error", session_id=session.session_id, error=str(e))
            session.cancelled = True
            self._save_session(session)
            raise
        
        finally:
            self.current_session = None
            gc.collect()  # Nettoyer la mémoire
    
    def _create_batches(self, messages_data: List[Tuple], start_batch: int = 0) -> List[List[Tuple]]:
        """Divise les messages en batches"""
        # Ignorer les batches déjà traités
        start_index = start_batch * self.batch_size
        remaining_data = messages_data[start_index:]
        
        batches = []
        for i in range(0, len(remaining_data), self.batch_size):
            batch = remaining_data[i:i + self.batch_size]
            batches.append(batch)
        
        return batches
    
    def _process_batch_with_limits(self, batch: List[Tuple], batch_num: int) -> List[MessageResult]:
        """Traite un batch de messages avec gestion des limites et pauses - ENVOI SÉQUENTIEL"""
        batch_results = []
        messages_sent_in_burst = 0
        
        # Traitement séquentiel pour respecter les délais
        for i, (phone, message, image_path) in enumerate(batch):
            if self.is_cancelled:
                break
            
            try:
                # Appliquer le délai AVANT l'envoi (sauf pour le premier message du batch)
                if i > 0:  # Pas de délai pour le premier message du premier batch
                    self._countdown_wait(int(self.message_delay), "⏱️ Délai anti-spam")
                
                # Envoyer le message
                if image_path:
                    result = self._send_message_with_retry('image', phone, message, image_path)
                else:
                    result = self._send_message_with_retry('text', phone, message)
                
                batch_results.append(result)
                
                # Si le message a été envoyé avec succès
                if result.success:
                    self.sent_numbers.add(result.phone)
                    messages_sent_in_burst += 1
                    
                    # Pause après X messages envoyés (burst limit)
                    if messages_sent_in_burst >= self.message_burst_limit:
                        if self.burst_pause_duration > 0:
                            pause_minutes = int(self.burst_pause_duration // 60)
                            pause_seconds = int(self.burst_pause_duration % 60)
                            self._update_status(f"⏸️ Pause de {pause_minutes}min {pause_seconds}s après {self.message_burst_limit} messages")
                            time.sleep(self.burst_pause_duration)
                        messages_sent_in_burst = 0
                
                # Mettre à jour la progression après chaque message
                total_completed = self.current_session.completed + len(batch_results)
                self._update_progress(total_completed, self.current_session.total_messages)
                
            except Exception as e:
                # Erreur lors de l'envoi
                result = MessageResult(phone, False, str(e))
                batch_results.append(result)
                logger.error("message_send_error", phone=phone, error=str(e))
        
        logger.info("batch_completed", batch_num=batch_num, 
                   results_count=len(batch_results),
                   successful=sum(1 for r in batch_results if r.success))
        
        # Sauvegarder les numéros contactés après chaque batch
        self._save_sent_numbers()
        
        return batch_results
    
    def _send_message_with_retry(
        self, 
        message_type: str, 
        phone: str, 
        message: str, 
        image_path: Optional[str] = None
    ) -> MessageResult:
        """Envoie un message avec tentatives de retry"""
        last_error = None
        
        for attempt in range(self.retry_attempts + 1):
            if self.is_cancelled:
                return MessageResult(phone, False, "Cancelled")
            
            try:
                if message_type == 'image' and image_path:
                    result = self.client.send_image_message(phone, image_path, message)
                else:
                    result = self.client.send_text_message(phone, message)
                
                if result.success:
                    return result
                else:
                    last_error = result.error
                    
            except Exception as e:
                last_error = str(e)
                logger.warning("message_retry", phone=phone, attempt=attempt, error=str(e))
            
            # Attendre avant le retry (backoff exponentiel)
            if attempt < self.retry_attempts:
                wait_time = (2 ** attempt) * 0.5  # 0.5, 1, 2 secondes
                time.sleep(wait_time)
        
        return MessageResult(phone, False, f"Failed after {self.retry_attempts + 1} attempts: {last_error}")
    
    def _update_session_with_results(self, session: SendingSession, results: List[MessageResult]):
        """Met à jour la session avec les résultats du batch"""
        with self.lock:
            session.completed += len(results)
            
            for result in results:
                if result.success:
                    session.successful += 1
                else:
                    session.failed += 1
                    # Limiter le nombre d'erreurs stockées pour économiser la mémoire
                    if len(session.error_messages) < 100:
                        session.error_messages.append({
                            'phone': result.phone,
                            'error': result.error,
                            'timestamp': time.time()
                        })
    
    def _save_session(self, session: SendingSession):
        """Sauvegarde l'état de la session"""
        try:
            session_file = self.sessions_dir / f"{session.session_id}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(session), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error("session_save_error", session_id=session.session_id, error=str(e))
    
    def _load_session(self, session_id: str) -> Optional[SendingSession]:
        """Charge l'état d'une session"""
        try:
            session_file = self.sessions_dir / f"{session_id}.json"
            if session_file.exists():
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return SendingSession(**data)
        except Exception as e:
            logger.error("session_load_error", session_id=session_id, error=str(e))
        return None
    
    def _update_progress(self, completed: int, total: int):
        """Met à jour la progression"""
        if self.progress_callback:
            percentage = (completed / total * 100) if total > 0 else 0
            status = f"Envoyé {completed}/{total} ({percentage:.1f}%)"
            try:
                self.progress_callback(completed, total, status)
            except Exception as e:
                logger.error("progress_callback_error", error=str(e))
    
    def _update_status(self, message: str):
        """Met à jour le statut"""
        if self.status_callback:
            try:
                self.status_callback(message)
            except Exception as e:
                logger.error("status_callback_error", error=str(e))
    
    def pause_sending(self):
        """Met en pause l'envoi en cours"""
        self.is_paused = True
        logger.info("sending_paused")
    
    def resume_sending(self):
        """Reprend l'envoi en pause"""
        self.is_paused = False
        logger.info("sending_resumed")
    
    def cancel_sending(self):
        """Annule l'envoi en cours"""
        self.is_cancelled = True
        logger.info("sending_cancelled")
    
    def get_session_stats(self, session: SendingSession) -> Dict:
        """Génère des statistiques détaillées pour une session"""
        if session.total_messages == 0:
            return {}
        
        elapsed_time = time.time() - session.start_time
        rate = session.completed / elapsed_time if elapsed_time > 0 else 0
        
        # ETA
        remaining = session.total_messages - session.completed
        eta = remaining / rate if rate > 0 else 0
        
        # Top erreurs
        error_summary = {}
        for error_msg in session.error_messages:
            error_key = error_msg['error'][:50]  # Tronquer les erreurs longues
            error_summary[error_key] = error_summary.get(error_key, 0) + 1
        
        return {
            'session_id': session.session_id,
            'total': session.total_messages,
            'completed': session.completed,
            'successful': session.successful,
            'failed': session.failed,
            'success_rate': (session.successful / session.completed * 100) if session.completed > 0 else 0,
            'progress_percentage': (session.completed / session.total_messages * 100),
            'elapsed_time': elapsed_time,
            'messages_per_second': rate,
            'estimated_time_remaining': eta,
            'current_batch': session.current_batch,
            'paused': session.paused,
            'cancelled': session.cancelled,
            'top_errors': dict(list(error_summary.items())[:5])
        }
    
    def cleanup_old_sessions(self, max_age_days: int = 7):
        """Nettoie les anciennes sessions"""
        try:
            cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
            
            for session_file in self.sessions_dir.glob("*.json"):
                if session_file.stat().st_mtime < cutoff_time:
                    session_file.unlink()
                    logger.info("old_session_cleaned", file=str(session_file))
        
        except Exception as e:
            logger.error("session_cleanup_error", error=str(e))
    
    def list_sessions(self) -> List[Dict]:
        """Liste toutes les sessions disponibles"""
        sessions = []
        
        try:
            for session_file in self.sessions_dir.glob("*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        sessions.append({
                            'session_id': data['session_id'],
                            'total_messages': data['total_messages'],
                            'completed': data['completed'],
                            'successful': data['successful'],
                            'failed': data['failed'],
                            'cancelled': data.get('cancelled', False),
                            'start_time': data['start_time']
                        })
                except Exception as e:
                    logger.error("session_list_error", file=str(session_file), error=str(e))
        
        except Exception as e:
            logger.error("sessions_directory_error", error=str(e))
        
        return sorted(sessions, key=lambda x: x['start_time'], reverse=True)
    
    def _filter_already_sent(self, messages_data: List[Tuple[str, str, Optional[str]]]) -> List[Tuple[str, str, Optional[str]]]:
        """Filtre les messages pour les numéros déjà contactés"""
        filtered = []
        skipped_count = 0
        
        for phone, message, image_path in messages_data:
            # Normaliser le numéro pour la comparaison
            normalized_phone = self._normalize_phone(phone)
            
            if normalized_phone not in self.sent_numbers:
                filtered.append((phone, message, image_path))
            else:
                skipped_count += 1
                logger.info("phone_already_contacted", phone=phone)
        
        if skipped_count > 0:
            self._update_status(f"{skipped_count} numéros déjà contactés ignorés")
            logger.info("filtered_already_sent", skipped=skipped_count, remaining=len(filtered))
        
        return filtered
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalise un numéro de téléphone pour la comparaison"""
        # Supprimer tous les caractères non numériques sauf le +
        normalized = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        # Si le numéro commence par +, le garder tel quel
        if normalized.startswith('+'):
            return normalized
        
        # Si le numéro commence par 00, remplacer par +
        if normalized.startswith('00'):
            return '+' + normalized[2:]
        
        return normalized
    
    def _load_sent_numbers(self):
        """Charge la liste des numéros déjà contactés"""
        try:
            if self.sent_numbers_file.exists():
                with open(self.sent_numbers_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sent_numbers = set(data.get('sent_numbers', []))
                    logger.info("sent_numbers_loaded", count=len(self.sent_numbers))
            else:
                self.sent_numbers = set()
                logger.info("sent_numbers_file_not_found", creating_new=True)
        except Exception as e:
            logger.error("sent_numbers_load_error", error=str(e))
            self.sent_numbers = set()
    
    def _save_sent_numbers(self):
        """Sauvegarde la liste des numéros contactés"""
        try:
            # Créer le répertoire si nécessaire
            self.sent_numbers_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'sent_numbers': list(self.sent_numbers),
                'last_updated': time.time(),
                'total_count': len(self.sent_numbers)
            }
            
            with open(self.sent_numbers_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info("sent_numbers_saved", count=len(self.sent_numbers))
            
        except Exception as e:
            logger.error("sent_numbers_save_error", error=str(e))
    
    def get_sent_numbers_count(self) -> int:
        """Retourne le nombre de numéros déjà contactés"""
        return len(self.sent_numbers)
    
    def clear_sent_numbers(self):
        """Efface la liste des numéros contactés (pour les tests)"""
        self.sent_numbers.clear()
        self._save_sent_numbers()
        logger.info("sent_numbers_cleared")
    
    def is_phone_already_sent(self, phone: str) -> bool:
        """Vérifie si un numéro a déjà été contacté"""
        normalized_phone = self._normalize_phone(phone)
        return normalized_phone in self.sent_numbers
    
    def _save_sending_config(self):
        """Sauvegarde automatique de la configuration d'envoi"""
        try:
            config_file = Path.home() / ".excel_whatsapp" / "sending_config.json"
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            config = {
                "message_delay": self.message_delay,
                "message_burst_limit": self.message_burst_limit,
                "burst_pause_duration": self.burst_pause_duration,
                "batch_delay": self.batch_delay,
                "last_updated": time.time()
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            logger.error("config_save_error", error=str(e))
    
    def _load_sending_config(self):
        """Charge la configuration d'envoi sauvegardée"""
        try:
            config_file = Path.home() / ".excel_whatsapp" / "sending_config.json"
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Appliquer la configuration chargée
                self.message_delay = max(1.0, config.get("message_delay", self.message_delay))
                self.message_burst_limit = max(1, config.get("message_burst_limit", self.message_burst_limit))
                self.burst_pause_duration = max(5, config.get("burst_pause_duration", self.burst_pause_duration))
                self.batch_delay = max(0.5, config.get("batch_delay", self.batch_delay))
                
                logger.info("config_loaded",
                           message_delay=self.message_delay,
                           burst_limit=self.message_burst_limit,
                           burst_pause=self.burst_pause_duration)
                
        except Exception as e:
            logger.error("config_load_error", error=str(e))
    
    def _countdown_wait(self, seconds: int, status_prefix: str):
        """
        Compte à rebours visuel pour l'attente avec mise à jour temps réel
        """
        for remaining in range(seconds, 0, -1):
            if self.is_cancelled:  # Arrêter si l'envoi est annulé
                break
            
            minutes = remaining // 60
            secs = remaining % 60
            
            if minutes > 0:
                time_text = f"{minutes}min {secs}s"
            else:
                time_text = f"{secs}s"
            
            self._update_status(f"{status_prefix} - Reste: {time_text}")
            time.sleep(1)
        
        # Indiquer que l'attente est terminée
        if not self.is_cancelled:
            self._update_status(f"{status_prefix} - Terminé ✅")