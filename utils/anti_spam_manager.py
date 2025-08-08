# -*- coding: utf-8 -*-
"""
Module de gestion anti-spam avancé
Protection contre la détection de comportements automatisés sur WhatsApp
"""

import json
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading


class RiskLevel(Enum):
    """Niveaux de risque de détection spam"""
    LOW = "low"          # Vert : < 30 messages/jour
    MEDIUM = "medium"    # Jaune : 30-80 messages/jour
    HIGH = "high"        # Orange : 80-150 messages/jour  
    CRITICAL = "critical" # Rouge : > 150 messages/jour


class BehaviorPattern(Enum):
    """Patterns de comportement humain"""
    OFFICE_WORKER = "office_worker"      # 8h-18h avec pauses
    CASUAL_USER = "casual_user"          # Irrégulier, plus le soir
    BUSINESS_HOURS = "business_hours"    # 9h-17h strict
    FLEXIBLE = "flexible"                # 6h-22h avec variations


@dataclass
class SpamProtectionConfig:
    """Configuration de protection anti-spam"""
    # Limites quotidiennes
    max_messages_per_day: int = 80
    max_messages_per_hour: int = 15
    max_messages_per_burst: int = 10
    
    # Délais (en secondes)
    min_delay_between_messages: int = 30
    max_delay_between_messages: int = 180
    pause_after_burst_min: int = 600    # 10 minutes
    pause_after_burst_max: int = 1800   # 30 minutes
    long_pause_after_count: int = 50
    long_pause_min: int = 3600          # 1 heure
    long_pause_max: int = 7200          # 2 heures
    
    # Patterns temporels
    behavior_pattern: BehaviorPattern = BehaviorPattern.OFFICE_WORKER
    working_hours_start: int = 8        # 8h
    working_hours_end: int = 18         # 18h
    lunch_break_start: int = 12         # 12h
    lunch_break_end: int = 14           # 14h
    
    # Seuils d'alerte
    warning_threshold: float = 0.7      # 70% de la limite
    critical_threshold: float = 0.9     # 90% de la limite
    
    # Options avancées
    enable_weekend_slowdown: bool = True
    weekend_speed_factor: float = 0.5   # 50% plus lent le weekend
    enable_progressive_delays: bool = True
    enable_delivery_monitoring: bool = True


@dataclass 
class DailyStats:
    """Statistiques d'envoi quotidien"""
    date: str
    messages_sent: int = 0
    messages_delivered: int = 0
    messages_failed: int = 0
    first_message_time: Optional[str] = None
    last_message_time: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.LOW
    pauses_taken: int = 0
    total_pause_time: int = 0  # en secondes


class AntiSpamManager:
    """Gestionnaire anti-spam avancé avec IA comportementale"""
    
    def __init__(self, config: Optional[SpamProtectionConfig] = None):
        self.config = config or SpamProtectionConfig()
        self.stats_file = Path.home() / ".whatsapp_daily_stats.json"
        self.daily_stats: Dict[str, DailyStats] = self.load_daily_stats()
        self.session_start_time = datetime.now()
        self.messages_sent_in_session = 0
        self.last_message_time: Optional[datetime] = None
        self._lock = threading.Lock()
        
        # Initialiser les stats du jour si nécessaire
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.daily_stats:
            self.daily_stats[today] = DailyStats(date=today)
    
    def load_daily_stats(self) -> Dict[str, DailyStats]:
        """Charge les statistiques quotidiennes"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {
                        date: DailyStats(**stats) 
                        for date, stats in data.items()
                    }
            return {}
        except Exception:
            return {}
    
    def save_daily_stats(self):
        """Sauvegarde les statistiques quotidiennes"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                data = {
                    date: asdict(stats) 
                    for date, stats in self.daily_stats.items()
                }
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur sauvegarde stats anti-spam: {e}")
    
    def get_today_stats(self) -> DailyStats:
        """Obtient les stats du jour courant"""
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.daily_stats:
            self.daily_stats[today] = DailyStats(date=today)
        return self.daily_stats[today]
    
    def calculate_risk_level(self) -> RiskLevel:
        """Calcule le niveau de risque actuel"""
        today_stats = self.get_today_stats()
        messages_today = today_stats.messages_sent
        
        if messages_today >= self.config.max_messages_per_day * 1.5:
            return RiskLevel.CRITICAL
        elif messages_today >= self.config.max_messages_per_day:
            return RiskLevel.HIGH
        elif messages_today >= self.config.max_messages_per_day * 0.6:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def is_within_working_hours(self) -> bool:
        """Vérifie si on est dans les heures de travail selon le pattern"""
        now = datetime.now()
        current_hour = now.hour
        is_weekend = now.weekday() >= 5  # 5=samedi, 6=dimanche
        
        pattern = self.config.behavior_pattern
        
        if pattern == BehaviorPattern.OFFICE_WORKER:
            if is_weekend:
                return False
            # Pause déjeuner
            if self.config.lunch_break_start <= current_hour < self.config.lunch_break_end:
                return False
            return self.config.working_hours_start <= current_hour < self.config.working_hours_end
        
        elif pattern == BehaviorPattern.BUSINESS_HOURS:
            if is_weekend:
                return current_hour >= 10 and current_hour < 16  # Weekend plus restreint
            return 9 <= current_hour < 17
        
        elif pattern == BehaviorPattern.CASUAL_USER:
            # Plus actif le soir et weekend
            if is_weekend:
                return 10 <= current_hour <= 22
            return current_hour >= 18 or current_hour <= 9 or (12 <= current_hour <= 14)
        
        elif pattern == BehaviorPattern.FLEXIBLE:
            return 6 <= current_hour <= 22
        
        return True
    
    def calculate_intelligent_delay(self) -> int:
        """Calcule un délai intelligent basé sur le comportement et le risque"""
        today_stats = self.get_today_stats()
        risk_level = self.calculate_risk_level()
        messages_in_last_hour = self._count_messages_last_hour()
        
        # Délai de base
        base_min = self.config.min_delay_between_messages
        base_max = self.config.max_delay_between_messages
        
        # Ajustements selon le risque
        if risk_level == RiskLevel.CRITICAL:
            base_min *= 3
            base_max *= 4
        elif risk_level == RiskLevel.HIGH:
            base_min *= 2
            base_max *= 2.5
        elif risk_level == RiskLevel.MEDIUM:
            base_min *= 1.5
            base_max *= 1.8
        
        # Ajustements selon l'heure
        if not self.is_within_working_hours():
            base_min *= 2
            base_max *= 2
        
        # Ajustements weekend
        if self.config.enable_weekend_slowdown:
            now = datetime.now()
            if now.weekday() >= 5:
                base_min = int(base_min / self.config.weekend_speed_factor)
                base_max = int(base_max / self.config.weekend_speed_factor)
        
        # Délais progressifs
        if self.config.enable_progressive_delays:
            if today_stats.messages_sent > 30:
                multiplier = 1 + (today_stats.messages_sent - 30) * 0.1
                base_min = int(base_min * multiplier)
                base_max = int(base_max * multiplier)
        
        # Randomisation finale
        return random.randint(base_min, base_max)
    
    def _count_messages_last_hour(self) -> int:
        """Compte les messages envoyés dans la dernière heure"""
        # Pour une implémentation complète, il faudrait tracker 
        # les timestamps précis, ici on simule
        return min(self.messages_sent_in_session, self.config.max_messages_per_hour)
    
    def should_take_long_pause(self) -> Tuple[bool, int]:
        """Détermine s'il faut prendre une pause longue"""
        today_stats = self.get_today_stats()
        
        # Pause après un certain nombre de messages
        if (today_stats.messages_sent > 0 and 
            today_stats.messages_sent % self.config.long_pause_after_count == 0):
            
            pause_duration = random.randint(
                self.config.long_pause_min, 
                self.config.long_pause_max
            )
            return True, pause_duration
        
        # Pause si on atteint la limite horaire
        messages_last_hour = self._count_messages_last_hour()
        if messages_last_hour >= self.config.max_messages_per_hour:
            return True, 3600  # 1 heure de pause
        
        return False, 0
    
    def can_send_message(self) -> Tuple[bool, str, int]:
        """
        Détermine si on peut envoyer un message
        Returns: (can_send, reason, suggested_delay)
        """
        today_stats = self.get_today_stats()
        risk_level = self.calculate_risk_level()
        
        # Vérification limite quotidienne
        if today_stats.messages_sent >= self.config.max_messages_per_day:
            tomorrow = datetime.now() + timedelta(days=1)
            seconds_until_tomorrow = int((tomorrow.replace(hour=8, minute=0, second=0) - datetime.now()).total_seconds())
            return False, f"Limite quotidienne atteinte ({self.config.max_messages_per_day})", seconds_until_tomorrow
        
        # Vérification limite horaire
        messages_last_hour = self._count_messages_last_hour()
        if messages_last_hour >= self.config.max_messages_per_hour:
            return False, f"Limite horaire atteinte ({self.config.max_messages_per_hour})", 3600
        
        # Vérification heures de travail
        if not self.is_within_working_hours():
            next_work_hour = self._calculate_next_work_hour()
            return False, "Hors heures de travail (simulation comportement humain)", next_work_hour
        
        # Vérification délai minimum depuis le dernier message
        if self.last_message_time:
            time_since_last = (datetime.now() - self.last_message_time).total_seconds()
            min_delay = self.config.min_delay_between_messages
            
            if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                min_delay *= 2
            
            if time_since_last < min_delay:
                remaining = int(min_delay - time_since_last)
                return False, f"Délai minimum non respecté (risque: {risk_level.value})", remaining
        
        # Calcul du délai recommandé
        suggested_delay = self.calculate_intelligent_delay()
        return True, "Autorisation d'envoyer", suggested_delay
    
    def _calculate_next_work_hour(self) -> int:
        """Calcule le nombre de secondes jusqu'à la prochaine heure de travail"""
        now = datetime.now()
        
        if self.config.behavior_pattern == BehaviorPattern.OFFICE_WORKER:
            # Si on est avant 8h, attendre jusqu'à 8h
            if now.hour < self.config.working_hours_start:
                next_work = now.replace(hour=self.config.working_hours_start, minute=0, second=0)
            # Si on est en pause déjeuner, attendre la fin
            elif self.config.lunch_break_start <= now.hour < self.config.lunch_break_end:
                next_work = now.replace(hour=self.config.lunch_break_end, minute=0, second=0)
            # Si on est après 18h, attendre le lendemain 8h
            else:
                next_work = (now + timedelta(days=1)).replace(hour=self.config.working_hours_start, minute=0, second=0)
        else:
            # Pour les autres patterns, attendre 1 heure
            next_work = now + timedelta(hours=1)
        
        return int((next_work - now).total_seconds())
    
    def record_message_sent(self, success: bool, delivered: bool = True):
        """Enregistre l'envoi d'un message"""
        with self._lock:
            now = datetime.now()
            today_stats = self.get_today_stats()
            
            if success:
                today_stats.messages_sent += 1
                if delivered:
                    today_stats.messages_delivered += 1
                
                # Première/dernière message du jour
                time_str = now.strftime("%H:%M:%S")
                if not today_stats.first_message_time:
                    today_stats.first_message_time = time_str
                today_stats.last_message_time = time_str
            else:
                today_stats.messages_failed += 1
            
            # Mise à jour des stats de session
            self.messages_sent_in_session += 1
            self.last_message_time = now
            
            # Calcul du niveau de risque
            today_stats.risk_level = self.calculate_risk_level()
            
            # Sauvegarde
            self.save_daily_stats()
    
    def record_pause(self, pause_duration: int):
        """Enregistre une pause prise"""
        today_stats = self.get_today_stats()
        today_stats.pauses_taken += 1
        today_stats.total_pause_time += pause_duration
        self.save_daily_stats()
    
    def get_risk_analysis(self) -> Dict:
        """Analyse complète du risque et recommandations"""
        today_stats = self.get_today_stats()
        risk_level = self.calculate_risk_level()
        
        # Calculs
        daily_progress = (today_stats.messages_sent / self.config.max_messages_per_day) * 100
        delivery_rate = (today_stats.messages_delivered / max(today_stats.messages_sent, 1)) * 100
        
        # Recommandations
        recommendations = []
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.append("🚨 ARRÊT IMMÉDIAT recommandé - Risque très élevé")
            recommendations.append("⏰ Reprendre demain avec des délais plus longs")
        elif risk_level == RiskLevel.HIGH:
            recommendations.append("⚠️ Ralentir significativement les envois")
            recommendations.append("⏸️ Prendre des pauses plus longues")
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.append("🟡 Surveiller attentivement les taux de livraison")
            recommendations.append("⏱️ Augmenter légèrement les délais")
        else:
            recommendations.append("✅ Niveau de risque acceptable")
            recommendations.append("📈 Continuer avec précaution")
        
        if delivery_rate < 90:
            recommendations.append(f"📉 Taux de livraison faible ({delivery_rate:.1f}%) - Ralentir")
        
        if not self.is_within_working_hours():
            recommendations.append("🕐 Hors heures de travail - Simulation comportement humain")
        
        return {
            "risk_level": risk_level.value,
            "daily_progress": daily_progress,
            "messages_sent_today": today_stats.messages_sent,
            "messages_limit": self.config.max_messages_per_day,
            "delivery_rate": delivery_rate,
            "working_hours_active": self.is_within_working_hours(),
            "recommendations": recommendations,
            "next_safe_send_time": self._calculate_next_safe_time(),
            "pattern": self.config.behavior_pattern.value
        }
    
    def _calculate_next_safe_time(self) -> str:
        """Calcule la prochaine heure d'envoi sûre"""
        can_send, reason, delay = self.can_send_message()
        
        if can_send:
            next_time = datetime.now() + timedelta(seconds=delay)
        else:
            next_time = datetime.now() + timedelta(seconds=delay)
        
        return next_time.strftime("%H:%M:%S")
    
    def cleanup_old_stats(self, days_to_keep: int = 30):
        """Nettoie les anciennes statistiques"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")
        
        keys_to_remove = [
            date for date in self.daily_stats.keys() 
            if date < cutoff_str
        ]
        
        for key in keys_to_remove:
            del self.daily_stats[key]
        
        if keys_to_remove:
            self.save_daily_stats()
    
    def get_weekly_stats(self) -> Dict:
        """Statistiques de la semaine"""
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        
        weekly_messages = 0
        weekly_delivered = 0
        weekly_failed = 0
        
        for i in range(7):
            date = (week_start + timedelta(days=i)).strftime("%Y-%m-%d")
            if date in self.daily_stats:
                stats = self.daily_stats[date]
                weekly_messages += stats.messages_sent
                weekly_delivered += stats.messages_delivered
                weekly_failed += stats.messages_failed
        
        return {
            "messages_sent": weekly_messages,
            "messages_delivered": weekly_delivered,
            "messages_failed": weekly_failed,
            "delivery_rate": (weekly_delivered / max(weekly_messages, 1)) * 100,
            "average_per_day": weekly_messages / 7
        }


# Factory function pour créer des configurations prédéfinies
def create_conservative_config() -> SpamProtectionConfig:
    """Configuration conservative (risque minimal)"""
    return SpamProtectionConfig(
        max_messages_per_day=50,
        max_messages_per_hour=8,
        min_delay_between_messages=60,
        max_delay_between_messages=300,
        long_pause_after_count=25
    )


def create_balanced_config() -> SpamProtectionConfig:
    """Configuration équilibrée (recommandée)"""
    return SpamProtectionConfig(
        max_messages_per_day=80,
        max_messages_per_hour=15,
        min_delay_between_messages=45,
        max_delay_between_messages=180,
        long_pause_after_count=40
    )


def create_aggressive_config() -> SpamProtectionConfig:
    """Configuration agressive (risque plus élevé)"""
    return SpamProtectionConfig(
        max_messages_per_day=120,
        max_messages_per_hour=25,
        min_delay_between_messages=30,
        max_delay_between_messages=120,
        long_pause_after_count=60
    )