# -*- coding: utf-8 -*-
"""
Système de logging structuré
"""
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class StructuredLogger:
    """Logger structuré pour l'application"""
    
    def __init__(self, name: str = "ExcelWhatsApp", log_dir: Path = None):
        self.logger = logging.getLogger(name)
        
        if log_dir is None:
            log_dir = Path.home() / ".excel_whatsapp" / "logs"
        
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration du logger principal
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            
            # Handler pour fichier
            log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # Handler pour console (développement)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            
            # Formatter structuré
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def _log_structured(self, level: str, event: str, **kwargs):
        """Log avec structure JSON"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event': event,
            'level': level,
            **kwargs
        }
        
        # Convertir en string JSON pour le message
        message = json.dumps(log_data, ensure_ascii=False, default=str)
        
        if level == 'INFO':
            self.logger.info(message)
        elif level == 'WARNING':
            self.logger.warning(message)
        elif level == 'ERROR':
            self.logger.error(message)
        elif level == 'DEBUG':
            self.logger.debug(message)
    
    def info(self, event: str, **kwargs):
        """Log niveau INFO"""
        self._log_structured('INFO', event, **kwargs)
    
    def warning(self, event: str, **kwargs):
        """Log niveau WARNING"""
        self._log_structured('WARNING', event, **kwargs)
    
    def error(self, event: str, **kwargs):
        """Log niveau ERROR"""
        self._log_structured('ERROR', event, **kwargs)
    
    def debug(self, event: str, **kwargs):
        """Log niveau DEBUG"""
        self._log_structured('DEBUG', event, **kwargs)
    
    # Méthodes spécifiques au domaine métier
    def log_file_loaded(self, file_path: str, rows: int, columns: int):
        """Log chargement de fichier"""
        self.info(
            "file_loaded",
            file_path=file_path,
            rows=rows,
            columns=columns
        )
    
    def log_api_test(self, success: bool, phone: str, error: str = None):
        """Log test API"""
        if success:
            self.info("api_test_success", phone=phone)
        else:
            self.warning("api_test_failed", phone=phone, error=error)
    
    def log_message_sent(self, phone: str, success: bool, message_type: str = "text", error: str = None):
        """Log envoi de message"""
        if success:
            self.info(
                "message_sent",
                phone=phone,
                message_type=message_type
            )
        else:
            self.warning(
                "message_failed",
                phone=phone,
                message_type=message_type,
                error=error
            )
    
    def log_bulk_send_completed(self, total: int, sent: int, failed: int, duration: float):
        """Log fin d'envoi en masse"""
        self.info(
            "bulk_send_completed",
            total=total,
            sent=sent,
            failed=failed,
            success_rate=round((sent / total) * 100, 2) if total > 0 else 0,
            duration_seconds=round(duration, 2)
        )
    
    def log_security_event(self, event_type: str, details: Dict[str, Any] = None):
        """Log événements de sécurité"""
        self.warning(
            "security_event",
            event_type=event_type,
            details=details or {}
        )
    
    def log_config_change(self, key: str, action: str):
        """Log changements de configuration"""
        # Ne pas logger les valeurs sensibles
        sensitive_keys = {'token', 'instance_id'}
        if key in sensitive_keys:
            self.info("config_change", key=key, action=action, value="[ENCRYPTED]")
        else:
            self.info("config_change", key=key, action=action)


# Instance globale du logger
logger = StructuredLogger()