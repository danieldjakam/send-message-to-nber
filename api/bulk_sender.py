# -*- coding: utf-8 -*-
"""
Gestionnaire d'envoi en masse optimisé pour de gros volumes (10k+ messages)
"""
import time
import threading
from typing import List, Dict, Callable, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        
        # Configuration pour gros volumes
        self.max_workers = 3  # Limité pour éviter la surcharge
        self.batch_delay = 2.0  # Délai entre les batches (secondes)
        self.retry_attempts = 2
        self.memory_cleanup_interval = 100  # Nettoyer la mémoire tous les 100 messages
        
        # État de l'envoi
        self.current_session: Optional[SendingSession] = None
        self.is_paused = False
        self.is_cancelled = False
        self.progress_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        
        # File d'attente pour les résultats
        self.results_queue = queue.Queue()
        self.lock = threading.Lock()
    
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
        
        # Créer ou reprendre une session
        if resume_session_id:
            session = self._load_session(resume_session_id)
            if not session:
                raise ValueError(f"Session {resume_session_id} introuvable")
        else:
            session_id = f"bulk_send_{int(time.time())}"
            session = SendingSession(
                session_id=session_id,
                total_messages=len(messages_data),
                start_time=time.time()
            )
        
        self.current_session = session
        
        try:
            logger.info("bulk_send_started_optimized", 
                       session_id=session.session_id,
                       total=session.total_messages,
                       batch_size=self.batch_size)
            
            # Diviser en batches
            batches = self._create_batches(messages_data, session.current_batch)
            
            for batch_num, batch in enumerate(batches, start=session.current_batch):
                if self.is_cancelled:
                    break
                
                while self.is_paused and not self.is_cancelled:
                    time.sleep(0.1)
                
                session.current_batch = batch_num
                self._save_session(session)
                
                self._update_status(f"Traitement du batch {batch_num + 1}/{len(batches) + session.current_batch}")
                
                # Traiter le batch
                batch_results = self._process_batch(batch, batch_num)
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
            
            # Sauvegarder l'état final
            self._save_session(session)
            
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
    
    def _process_batch(self, batch: List[Tuple], batch_num: int) -> List[MessageResult]:
        """Traite un batch de messages avec gestion d'erreurs robuste"""
        batch_results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Soumettre toutes les tâches du batch
            future_to_data = {}
            
            for phone, message, image_path in batch:
                if self.is_cancelled:
                    break
                
                try:
                    if image_path:
                        future = executor.submit(
                            self._send_message_with_retry,
                            'image', phone, message, image_path
                        )
                    else:
                        future = executor.submit(
                            self._send_message_with_retry,
                            'text', phone, message
                        )
                    
                    future_to_data[future] = (phone, message, image_path)
                    
                except Exception as e:
                    # Erreur lors de la soumission
                    result = MessageResult(phone, False, str(e))
                    batch_results.append(result)
                    logger.error("task_submission_error", phone=phone, error=str(e))
            
            # Collecter les résultats
            for future in as_completed(future_to_data, timeout=300):  # 5 min timeout par batch
                if self.is_cancelled:
                    future.cancel()
                    continue
                
                try:
                    result = future.result(timeout=60)  # 1 min timeout par message
                    batch_results.append(result)
                    
                    # Mettre à jour la progression
                    total_completed = self.current_session.completed + len(batch_results)
                    self._update_progress(total_completed, self.current_session.total_messages)
                    
                except Exception as e:
                    phone_data = future_to_data.get(future, ("unknown", "", None))
                    phone = phone_data[0]
                    result = MessageResult(phone, False, f"Timeout/Error: {str(e)}")
                    batch_results.append(result)
                    logger.error("message_processing_error", phone=phone, error=str(e))
        
        logger.info("batch_completed", batch_num=batch_num, 
                   results_count=len(batch_results),
                   successful=sum(1 for r in batch_results if r.success))
        
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