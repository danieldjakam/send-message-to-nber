# -*- coding: utf-8 -*-
"""
Gestionnaire anti-spam intelligent pour WhatsApp
Système de protection avancé contre la détection de spam avec simulation comportementale humaine
"""

import time
import random
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from utils.logger import logger


class RiskLevel(Enum):
    """Niveaux de risque pour la détection anti-spam"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BehaviorPattern(Enum):
    """Patterns de comportement humain simulés"""
    OFFICE_WORKER = "office_worker"
    CASUAL_USER = "casual_user"
    BUSINESS_USER = "business_user"
    STUDENT = "student"
    EVENING_USER = "evening_user"
    WEEKEND_WARRIOR = "weekend_warrior"
    CUSTOM = "custom"


@dataclass
class AntiSpamConfig:
    """Configuration complète du système anti-spam"""
    # Limites quotidiennes et horaires
    daily_message_limit: int = 500
    hourly_message_limit: int = 50
    enable_daily_limit: bool = True
    enable_hourly_limit: bool = True
    
    # Délais intelligents
    min_message_delay: int = 30  # secondes
    max_message_delay: int = 180  # secondes
    enable_intelligent_delays: bool = True
    
    # Heures de travail
    working_hours_start: int = 8  # 8h00
    working_hours_end: int = 18   # 18h00
    respect_working_hours: bool = True
    
    # Pattern de comportement
    behavior_pattern: str = BehaviorPattern.OFFICE_WORKER.value
    
    # Protections avancées
    enable_weekend_protection: bool = True
    enable_risk_analysis: bool = True
    enable_multi_day_distribution: bool = True
    
    # Mode expert
    expert_mode: bool = False
    
    # Configuration personnalisée
    custom_delays: List[int] = None
    custom_working_hours: List[Tuple[int, int]] = None  # [(start, end), ...]
    
    def __post_init__(self):
        if self.custom_delays is None:
            self.custom_delays = []
        if self.custom_working_hours is None:
            self.custom_working_hours = []


class AntiSpamManager:
    """Gestionnaire anti-spam intelligent avec simulation de comportement humain"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or str(Path.home() / ".excel_whatsapp" / "anti_spam_config.json")
        self.stats_file = str(Path.home() / ".excel_whatsapp" / "anti_spam_stats.json")
        
        # Charger la configuration
        self.config = self.load_config()
        
        # État actuel
        self.daily_stats: Dict[str, Any] = {}
        self.hourly_stats: Dict[str, Any] = {}
        self.risk_factors: List[str] = []
        
        # Charger les statistiques
        self.load_stats()
        
        # Cache pour les calculs
        self._last_file_hash: Optional[str] = None
        self._cached_recommendations: Optional[Dict] = None
        
    def load_config(self) -> AntiSpamConfig:
        """Charge la configuration depuis le fichier"""
        try:
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return AntiSpamConfig(**data)
            else:
                # Configuration par défaut
                return AntiSpamConfig()
        except Exception as e:
            logger.error("anti_spam_config_load_error", error=str(e))
            return AntiSpamConfig()
    
    def save_config(self):
        """Sauvegarde la configuration"""
        try:
            config_path = Path(self.config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, indent=2, ensure_ascii=False)
            
            logger.info("anti_spam_config_saved")
        except Exception as e:
            logger.error("anti_spam_config_save_error", error=str(e))
    
    def load_stats(self):
        """Charge les statistiques d'usage"""
        try:
            stats_path = Path(self.stats_file)
            if stats_path.exists():
                with open(stats_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.daily_stats = data.get('daily_stats', {})
                    self.hourly_stats = data.get('hourly_stats', {})
        except Exception as e:
            logger.error("anti_spam_stats_load_error", error=str(e))
    
    def save_stats(self):
        """Sauvegarde les statistiques"""
        try:
            stats_path = Path(self.stats_file)
            stats_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'daily_stats': self.daily_stats,
                'hourly_stats': self.hourly_stats,
                'last_updated': time.time()
            }
            
            with open(stats_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error("anti_spam_stats_save_error", error=str(e))
    
    def get_today_key(self) -> str:
        """Retourne la clé pour les stats du jour"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def get_hour_key(self) -> str:
        """Retourne la clé pour les stats de l'heure"""
        return datetime.now().strftime("%Y-%m-%d-%H")
    
    def get_today_stats(self) -> Dict[str, int]:
        """Retourne les stats du jour actuel"""
        today = self.get_today_key()
        return self.daily_stats.get(today, {'messages_sent': 0, 'files_processed': 0})
    
    def get_hour_stats(self) -> Dict[str, int]:
        """Retourne les stats de l'heure actuelle"""
        hour = self.get_hour_key()
        return self.hourly_stats.get(hour, {'messages_sent': 0})
    
    def can_send_message(self, phone_number: str = "", file_hash: str = "") -> Tuple[bool, str, int]:
        """
        Vérifie si un message peut être envoyé en respectant les règles anti-spam
        
        Returns:
            Tuple[bool, str, int]: (can_send, reason, suggested_delay)
        """
        if self.config.expert_mode:
            return True, "Mode expert activé - aucune restriction", 0
        
        # Vérification des limites quotidiennes
        if self.config.enable_daily_limit:
            today_stats = self.get_today_stats()
            if today_stats['messages_sent'] >= self.config.daily_message_limit:
                tomorrow = datetime.now() + timedelta(days=1)
                tomorrow_start = tomorrow.replace(hour=8, minute=0, second=0, microsecond=0)
                delay = int((tomorrow_start - datetime.now()).total_seconds())
                return False, f"Limite quotidienne atteinte ({self.config.daily_message_limit})", delay
        
        # Vérification des limites horaires
        if self.config.enable_hourly_limit:
            hour_stats = self.get_hour_stats()
            if hour_stats['messages_sent'] >= self.config.hourly_message_limit:
                next_hour = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                delay = int((next_hour - datetime.now()).total_seconds())
                return False, f"Limite horaire atteinte ({self.config.hourly_message_limit})", delay
        
        # Vérification des heures de travail
        if self.config.respect_working_hours:
            current_hour = datetime.now().hour
            if not (self.config.working_hours_start <= current_hour <= self.config.working_hours_end):
                # Calculer le temps jusqu'à la prochaine heure de travail
                next_work_time = self._get_next_working_time()
                delay = int((next_work_time - datetime.now()).total_seconds())
                return False, "En dehors des heures de travail", delay
        
        # Vérification weekend
        if self.config.enable_weekend_protection:
            if datetime.now().weekday() >= 5:  # Samedi = 5, Dimanche = 6
                next_monday = self._get_next_monday()
                delay = int((next_monday - datetime.now()).total_seconds())
                return False, "Protection weekend activée", delay
        
        # Calcul du délai intelligent
        delay = self.calculate_intelligent_delay()
        return True, "Autorisation d'envoi", delay
    
    def calculate_intelligent_delay(self) -> int:
        """Calcule un délai intelligent basé sur le comportement et le risque"""
        if not self.config.enable_intelligent_delays:
            return 0
        
        # Délai de base selon le pattern de comportement
        base_delay = self._get_behavior_delay()
        
        # Ajustement selon le niveau de risque
        risk_level = self.calculate_risk_level()
        risk_multiplier = self._get_risk_multiplier(risk_level)
        
        # Randomisation pour simuler un comportement humain
        min_delay = max(self.config.min_message_delay, int(base_delay * 0.7))
        max_delay = min(self.config.max_message_delay, int(base_delay * risk_multiplier * 1.5))
        
        if min_delay >= max_delay:
            return min_delay
        
        # Distribution non uniforme (plus probable vers le centre)
        center = (min_delay + max_delay) // 2
        variance = (max_delay - min_delay) // 4
        
        delay = int(random.gauss(center, variance))
        return max(min_delay, min(max_delay, delay))
    
    def calculate_risk_level(self) -> RiskLevel:
        """Calcule le niveau de risque actuel"""
        if not self.config.enable_risk_analysis:
            return RiskLevel.LOW
        
        score = 0
        self.risk_factors = []
        
        # Analyse des statistiques quotidiennes
        today_stats = self.get_today_stats()
        daily_ratio = today_stats['messages_sent'] / max(self.config.daily_message_limit, 1)
        
        if daily_ratio > 0.8:
            score += 3
            self.risk_factors.append("Proche de la limite quotidienne")
        elif daily_ratio > 0.6:
            score += 2
            self.risk_factors.append("Usage quotidien élevé")
        
        # Analyse des statistiques horaires
        hour_stats = self.get_hour_stats()
        hourly_ratio = hour_stats['messages_sent'] / max(self.config.hourly_message_limit, 1)
        
        if hourly_ratio > 0.7:
            score += 2
            self.risk_factors.append("Usage horaire intensif")
        
        # Analyse temporelle
        current_hour = datetime.now().hour
        if current_hour < 8 or current_hour > 20:
            score += 1
            self.risk_factors.append("Envoi en heures non standard")
        
        # Classification du risque
        if score >= 5:
            return RiskLevel.CRITICAL
        elif score >= 3:
            return RiskLevel.HIGH
        elif score >= 1:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _get_behavior_delay(self) -> int:
        """Retourne le délai de base selon le pattern de comportement"""
        pattern = BehaviorPattern(self.config.behavior_pattern)
        
        delays = {
            BehaviorPattern.OFFICE_WORKER: 45,
            BehaviorPattern.CASUAL_USER: 120,
            BehaviorPattern.BUSINESS_USER: 30,
            BehaviorPattern.STUDENT: 90,
            BehaviorPattern.EVENING_USER: 180,
            BehaviorPattern.WEEKEND_WARRIOR: 300,
            BehaviorPattern.CUSTOM: self.config.min_message_delay
        }
        
        return delays.get(pattern, 60)
    
    def _get_risk_multiplier(self, risk_level: RiskLevel) -> float:
        """Retourne le multiplicateur de délai selon le niveau de risque"""
        multipliers = {
            RiskLevel.LOW: 1.0,
            RiskLevel.MEDIUM: 1.5,
            RiskLevel.HIGH: 2.5,
            RiskLevel.CRITICAL: 4.0
        }
        return multipliers[risk_level]
    
    def _get_next_working_time(self) -> datetime:
        """Calcule la prochaine heure de travail"""
        now = datetime.now()
        
        # Vérifier si on peut commencer aujourd'hui
        today_start = now.replace(hour=self.config.working_hours_start, minute=0, second=0, microsecond=0)
        if now.hour < self.config.working_hours_start:
            return today_start
        
        # Sinon demain
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=self.config.working_hours_start, minute=0, second=0, microsecond=0)
    
    def _get_next_monday(self) -> datetime:
        """Calcule le prochain lundi matin"""
        now = datetime.now()
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        
        next_monday = now + timedelta(days=days_until_monday)
        return next_monday.replace(hour=self.config.working_hours_start, minute=0, second=0, microsecond=0)
    
    def record_message_sent(self, phone_number: str = "", file_hash: str = ""):
        """Enregistre l'envoi d'un message pour les statistiques"""
        today = self.get_today_key()
        hour = self.get_hour_key()
        
        # Stats quotidiennes
        if today not in self.daily_stats:
            self.daily_stats[today] = {'messages_sent': 0, 'files_processed': 0}
        self.daily_stats[today]['messages_sent'] += 1
        
        # Stats horaires
        if hour not in self.hourly_stats:
            self.hourly_stats[hour] = {'messages_sent': 0}
        self.hourly_stats[hour]['messages_sent'] += 1
        
        # Nettoyer les anciennes stats (garder 30 jours)
        self._cleanup_old_stats()
        
        # Sauvegarder
        self.save_stats()
        
        logger.info("anti_spam_message_recorded", 
                   today=today, 
                   hour=hour,
                   daily_total=self.daily_stats[today]['messages_sent'])
    
    def _cleanup_old_stats(self):
        """Nettoie les statistiques anciennes pour économiser l'espace"""
        cutoff_date = datetime.now() - timedelta(days=30)
        cutoff_day = cutoff_date.strftime("%Y-%m-%d")
        cutoff_hour = cutoff_date.strftime("%Y-%m-%d-%H")
        
        # Nettoyer les stats quotidiennes
        self.daily_stats = {
            k: v for k, v in self.daily_stats.items() 
            if k >= cutoff_day
        }
        
        # Nettoyer les stats horaires
        self.hourly_stats = {
            k: v for k, v in self.hourly_stats.items() 
            if k >= cutoff_hour
        }
    
    def get_recommendations(self, file_path: str = "", total_messages: int = 0) -> Dict[str, Any]:
        """Génère des recommandations intelligentes pour l'envoi"""
        # Cache des recommandations
        if file_path:
            current_hash = self._calculate_file_hash(file_path)
            if (self._last_file_hash == current_hash and 
                self._cached_recommendations and
                time.time() - self._cached_recommendations.get('generated_at', 0) < 300):  # 5 minutes
                return self._cached_recommendations
        
        recommendations = {
            'generated_at': time.time(),
            'file_analyzed': bool(file_path),
            'total_messages': total_messages
        }
        
        # Analyse du volume
        if total_messages > 0:
            risk_level = self.calculate_risk_level()
            
            # Estimation du temps nécessaire
            avg_delay = self.calculate_intelligent_delay()
            estimated_time = total_messages * avg_delay
            
            recommendations.update({
                'risk_level': risk_level.value,
                'risk_factors': self.risk_factors,
                'estimated_duration_seconds': estimated_time,
                'estimated_duration_text': self._format_duration(estimated_time),
                'recommended_batch_size': self._get_recommended_batch_size(total_messages, risk_level),
                'optimal_time_to_start': self._get_optimal_start_time(),
                'should_distribute_over_days': total_messages > 200 and self.config.enable_multi_day_distribution
            })
            
            # Conseils spécifiques
            suggestions = []
            if risk_level == RiskLevel.CRITICAL:
                suggestions.append("⚠️ Risque critique - Réduisez le volume ou attendez demain")
            elif risk_level == RiskLevel.HIGH:
                suggestions.append("🔶 Risque élevé - Augmentez les délais ou répartissez sur plusieurs jours")
            elif total_messages > 500:
                suggestions.append("📅 Volume important - Considérez une distribution sur plusieurs jours")
            
            if not self.config.respect_working_hours:
                suggestions.append("🕐 Activez les heures de travail pour un envoi plus naturel")
            
            recommendations['suggestions'] = suggestions
        
        # Mettre en cache
        if file_path:
            self._last_file_hash = current_hash
            self._cached_recommendations = recommendations
        
        return recommendations
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcule le hash MD5 d'un fichier pour la mise en cache"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return str(time.time())  # Fallback
    
    def _format_duration(self, seconds: int) -> str:
        """Formate une durée en texte lisible"""
        if seconds < 3600:  # Moins d'une heure
            minutes = seconds // 60
            return f"{minutes} minutes"
        elif seconds < 86400:  # Moins d'un jour
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}min"
        else:  # Plusieurs jours
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days} jours {hours}h"
    
    def _get_recommended_batch_size(self, total_messages: int, risk_level: RiskLevel) -> int:
        """Recommande une taille de batch selon le volume et le risque"""
        base_sizes = {
            RiskLevel.LOW: min(50, total_messages),
            RiskLevel.MEDIUM: min(30, total_messages),
            RiskLevel.HIGH: min(20, total_messages),
            RiskLevel.CRITICAL: min(10, total_messages)
        }
        
        return max(1, base_sizes[risk_level])
    
    def _get_optimal_start_time(self) -> str:
        """Suggère le meilleur moment pour commencer l'envoi"""
        now = datetime.now()
        
        if not self.config.respect_working_hours:
            return "Maintenant"
        
        # Si on est dans les heures de travail
        if self.config.working_hours_start <= now.hour <= self.config.working_hours_end:
            return "Maintenant"
        
        # Sinon, suggérer la prochaine heure de travail
        next_work = self._get_next_working_time()
        return next_work.strftime("%Y-%m-%d à %H:%M")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Retourne le statut actuel du système anti-spam"""
        today_stats = self.get_today_stats()
        hour_stats = self.get_hour_stats()
        risk_level = self.calculate_risk_level()
        
        return {
            'config_active': not self.config.expert_mode,
            'daily_usage': {
                'sent': today_stats['messages_sent'],
                'limit': self.config.daily_message_limit,
                'percentage': (today_stats['messages_sent'] / max(self.config.daily_message_limit, 1)) * 100
            },
            'hourly_usage': {
                'sent': hour_stats['messages_sent'],
                'limit': self.config.hourly_message_limit,
                'percentage': (hour_stats['messages_sent'] / max(self.config.hourly_message_limit, 1)) * 100
            },
            'risk_level': risk_level.value,
            'risk_factors': self.risk_factors,
            'next_safe_time': self._get_next_working_time().isoformat() if not self._can_send_now() else None,
            'behavior_pattern': self.config.behavior_pattern,
            'working_hours': f"{self.config.working_hours_start:02d}h-{self.config.working_hours_end:02d}h"
        }
    
    def _can_send_now(self) -> bool:
        """Vérifie rapidement si on peut envoyer maintenant"""
        can_send, _, _ = self.can_send_message()
        return can_send