# -*- coding: utf-8 -*-
"""
Système de barres de chargement avancées avec animations et feedback temps réel
"""
import customtkinter as ctk
import tkinter as tk
import threading
import time
import math
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ProgressType(Enum):
    """Types de progression"""
    DETERMINATE = "determinate"
    INDETERMINATE = "indeterminate"
    PULSE = "pulse"
    WAVE = "wave"


@dataclass
class ProgressStats:
    """Statistiques de progression"""
    current: int = 0
    total: int = 0
    rate: float = 0.0
    eta: float = 0.0
    elapsed: float = 0.0
    status: str = ""
    success_count: int = 0
    error_count: int = 0


class AnimatedProgressBar(ctk.CTkProgressBar):
    """Barre de progression avec animations personnalisées"""
    
    def __init__(self, master, animation_type: ProgressType = ProgressType.DETERMINATE, **kwargs):
        super().__init__(master, **kwargs)
        
        self.animation_type = animation_type
        self.animation_running = False
        self.animation_thread = None
        self.pulse_direction = 1
        self.wave_offset = 0.0
        self.animation_speed = 0.05  # secondes
        
        # Couleurs d'animation
        self.colors = {
            'success': ('#28a745', '#20c997'),
            'warning': ('#ffc107', '#fd7e14'),
            'error': ('#dc3545', '#e83e8c'),
            'info': ('#17a2b8', '#6f42c1'),
            'default': ('#1f538d', '#14375e')
        }
        self.current_color = 'default'
    
    def start_animation(self):
        """Démarre l'animation"""
        if not self.animation_running:
            self.animation_running = True
            self.animation_thread = threading.Thread(target=self._animate, daemon=True)
            self.animation_thread.start()
    
    def stop_animation(self):
        """Arrête l'animation"""
        self.animation_running = False
        if self.animation_thread:
            self.animation_thread.join(timeout=1)
    
    def set_color_theme(self, color_name: str):
        """Change le thème de couleur"""
        if color_name in self.colors:
            self.current_color = color_name
            colors = self.colors[color_name]
            self.configure(progress_color=colors[0])
    
    def _animate(self):
        """Thread d'animation"""
        while self.animation_running:
            try:
                if self.animation_type == ProgressType.INDETERMINATE:
                    self._animate_indeterminate()
                elif self.animation_type == ProgressType.PULSE:
                    self._animate_pulse()
                elif self.animation_type == ProgressType.WAVE:
                    self._animate_wave()
                
                time.sleep(self.animation_speed)
            except Exception:
                break
    
    def _animate_indeterminate(self):
        """Animation indéterminée"""
        # Cycle entre 0 et 1
        current_time = time.time()
        progress = (math.sin(current_time * 2) + 1) / 2
        self.after(0, lambda: self.set(progress))
    
    def _animate_pulse(self):
        """Animation pulsée"""
        current_progress = self.get()
        if current_progress >= 1.0:
            self.pulse_direction = -1
        elif current_progress <= 0.0:
            self.pulse_direction = 1
        
        new_progress = current_progress + (self.pulse_direction * 0.02)
        self.after(0, lambda: self.set(max(0, min(1, new_progress))))
    
    def _animate_wave(self):
        """Animation en vagues"""
        self.wave_offset += 0.1
        progress = (math.sin(self.wave_offset) + 1) / 2
        self.after(0, lambda: self.set(progress))


class MultiProgressWidget(ctk.CTkFrame):
    """Widget avec plusieurs barres de progression"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.progress_bars = {}
        self.labels = {}
        self.stats = {}
        
        # Configuration du layout
        self.grid_columnconfigure(1, weight=1)
        
        # Titre
        self.title_label = ctk.CTkLabel(
            self,
            text="📊 Progression des Opérations",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=3, pady=(15, 10), sticky="w", padx=15)
    
    def add_progress(self, key: str, label: str, progress_type: ProgressType = ProgressType.DETERMINATE):
        """Ajoute une nouvelle barre de progression"""
        row = len(self.progress_bars) + 1
        
        # Label
        label_widget = ctk.CTkLabel(
            self,
            text=f"{label}:",
            font=ctk.CTkFont(size=11),
            width=120
        )
        label_widget.grid(row=row, column=0, sticky="w", padx=(15, 5), pady=5)
        
        # Barre de progression
        progress_bar = AnimatedProgressBar(
            self,
            animation_type=progress_type,
            height=15,
            corner_radius=8
        )
        progress_bar.grid(row=row, column=1, sticky="ew", padx=(5, 5), pady=5)
        
        # Label de statut
        status_label = ctk.CTkLabel(
            self,
            text="0%",
            font=ctk.CTkFont(size=10),
            width=80,
            text_color="gray"
        )
        status_label.grid(row=row, column=2, sticky="e", padx=(5, 15), pady=5)
        
        self.progress_bars[key] = progress_bar
        self.labels[key] = {
            'main': label_widget,
            'status': status_label
        }
        self.stats[key] = ProgressStats()
    
    def update_progress(self, key: str, current: int, total: int, status: str = ""):
        """Met à jour une barre de progression"""
        if key not in self.progress_bars:
            return
        
        progress_bar = self.progress_bars[key]
        status_label = self.labels[key]['status']
        stats = self.stats[key]
        
        # Calculer le pourcentage
        percentage = (current / total * 100) if total > 0 else 0
        progress_value = current / total if total > 0 else 0
        
        # Mettre à jour les stats
        stats.current = current
        stats.total = total
        stats.status = status
        
        # Mettre à jour la barre
        progress_bar.set(progress_value)
        
        # Mettre à jour le label de statut
        if status:
            status_text = f"{percentage:.1f}% - {status}"
        else:
            status_text = f"{percentage:.1f}% ({current}/{total})"
        
        status_label.configure(text=status_text)
        
        # Changer la couleur selon le statut
        if percentage == 100:
            progress_bar.set_color_theme('success')
        elif percentage > 75:
            progress_bar.set_color_theme('info')
        elif current == 0:
            progress_bar.set_color_theme('default')
    
    def set_progress_status(self, key: str, status_type: str):
        """Change le statut visuel d'une barre"""
        if key in self.progress_bars:
            self.progress_bars[key].set_color_theme(status_type)
    
    def start_animation(self, key: str):
        """Démarre l'animation d'une barre"""
        if key in self.progress_bars:
            self.progress_bars[key].start_animation()
    
    def stop_animation(self, key: str):
        """Arrête l'animation d'une barre"""
        if key in self.progress_bars:
            self.progress_bars[key].stop_animation()
    
    def reset_progress(self, key: str):
        """Remet à zéro une barre de progression"""
        if key in self.progress_bars:
            self.progress_bars[key].set(0)
            self.labels[key]['status'].configure(text="0%")
            self.stats[key] = ProgressStats()


class DetailedProgressDialog(ctk.CTkToplevel):
    """Dialog de progression détaillée avec statistiques temps réel"""
    
    def __init__(self, parent, title: str = "Progression Détaillée"):
        super().__init__(parent)
        
        self.title(title)
        self.geometry("700x500")
        self.minsize(600, 400)
        
        # Variables
        self.start_time = time.time()
        self.update_callback: Optional[Callable] = None
        self.stats = ProgressStats()
        
        # Rendre modal
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Titre avec icône animée
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill='x', pady=(0, 20))
        
        self.title_label = ctk.CTkLabel(
            title_frame,
            text="🔄 Traitement en cours...",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack()
        
        # Barre de progression principale
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(
            progress_frame,
            text="📈 Progression Globale",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 5))
        
        self.main_progress = AnimatedProgressBar(
            progress_frame,
            height=25,
            corner_radius=12
        )
        self.main_progress.pack(fill='x', padx=20, pady=(0, 10))
        
        self.main_status = ctk.CTkLabel(
            progress_frame,
            text="Initialisation...",
            font=ctk.CTkFont(size=12)
        )
        self.main_status.pack(pady=(0, 15))
        
        # Statistiques temps réel
        stats_frame = ctk.CTkFrame(main_frame)
        stats_frame.pack(fill='x', pady=(0, 20))
        
        ctk.CTkLabel(
            stats_frame,
            text="📊 Statistiques Temps Réel",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 10))
        
        # Grid pour les stats
        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(fill='x', padx=20, pady=(0, 15))
        
        # Configuration du grid
        for i in range(3):
            stats_grid.grid_columnconfigure(i, weight=1)
        
        # Statistiques
        self.create_stat_widget(stats_grid, "⏱️ Temps Écoulé", "00:00:00", 0, 0)
        self.create_stat_widget(stats_grid, "🚀 Débit", "0/sec", 0, 1)
        self.create_stat_widget(stats_grid, "⏳ ETA", "Calcul...", 0, 2)
        
        self.create_stat_widget(stats_grid, "✅ Réussis", "0", 1, 0)
        self.create_stat_widget(stats_grid, "❌ Échecs", "0", 1, 1)
        self.create_stat_widget(stats_grid, "📊 Total", "0", 1, 2)
        
        # Barres de progression multiples
        self.multi_progress = MultiProgressWidget(main_frame)
        self.multi_progress.pack(fill='x', pady=(0, 20))
        
        # Ajouter quelques barres par défaut
        self.multi_progress.add_progress("current_batch", "🔄 Batch Actuel")
        self.multi_progress.add_progress("validation", "✅ Validation")
        self.multi_progress.add_progress("network", "🌐 Réseau")
        
        # Log en temps réel
        log_frame = ctk.CTkFrame(main_frame)
        log_frame.pack(fill='both', expand=True)
        
        ctk.CTkLabel(
            log_frame,
            text="📝 Journal d'Activité",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 5), anchor="w", padx=15)
        
        self.log_text = ctk.CTkTextbox(
            log_frame,
            height=120,
            font=ctk.CTkFont(family="Consolas", size=10),
            wrap="word"
        )
        self.log_text.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Démarrer l'animation de la barre principale
        self.main_progress.start_animation()
        
        # Démarrer la mise à jour des stats
        self.start_stats_update()
    
    def create_stat_widget(self, parent, label: str, value: str, row: int, col: int):
        """Crée un widget de statistique"""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(size=10, weight="bold")
        ).pack(pady=(8, 2))
        
        value_label = ctk.CTkLabel(
            frame,
            text=value,
            font=ctk.CTkFont(size=12),
            text_color=("gray10", "gray90")
        )
        value_label.pack(pady=(0, 8))
        
        # Stocker la référence pour les mises à jour
        setattr(self, f"stat_{label.split()[1].lower()}", value_label)
    
    def update_progress(self, current: int, total: int, status: str = ""):
        """Met à jour la progression principale"""
        self.stats.current = current
        self.stats.total = total
        self.stats.status = status
        
        # Calculer le pourcentage
        percentage = (current / total * 100) if total > 0 else 0
        progress_value = current / total if total > 0 else 0
        
        # Mettre à jour la barre principale
        self.main_progress.set(progress_value)
        
        # Mettre à jour le statut
        if status:
            status_text = f"{status} - {percentage:.1f}% ({current}/{total})"
        else:
            status_text = f"{percentage:.1f}% - {current}/{total} éléments traités"
        
        self.main_status.configure(text=status_text)
        
        # Changer la couleur selon le pourcentage
        if percentage == 100:
            self.main_progress.set_color_theme('success')
            self.title_label.configure(text="✅ Traitement terminé !")
        elif percentage > 75:
            self.main_progress.set_color_theme('info')
        
        # Ajouter au log
        self.add_log(f"Progression: {current}/{total} ({percentage:.1f}%) - {status}")
    
    def update_batch_progress(self, batch_current: int, batch_total: int, batch_num: int, total_batches: int):
        """Met à jour la progression du batch actuel"""
        # Batch actuel
        self.multi_progress.update_progress(
            "current_batch", 
            batch_current, 
            batch_total, 
            f"Batch {batch_num}/{total_batches}"
        )
        
        # Progression globale des batches
        overall_progress = (batch_num - 1) * batch_total + batch_current
        overall_total = total_batches * batch_total
        
        self.update_progress(overall_progress, overall_total, f"Batch {batch_num}/{total_batches}")
    
    def update_validation_progress(self, current: int, total: int):
        """Met à jour la progression de validation"""
        self.multi_progress.update_progress("validation", current, total, "Validation")
    
    def update_network_status(self, status: str, progress: float = 0):
        """Met à jour le statut réseau"""
        self.multi_progress.progress_bars["network"].set(progress)
        self.multi_progress.labels["network"]["status"].configure(text=status)
    
    def add_log(self, message: str):
        """Ajoute un message au log"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\\n"
        
        self.log_text.insert("end", log_message)
        self.log_text.see("end")  # Faire défiler vers le bas
    
    def set_success_count(self, count: int):
        """Met à jour le nombre de succès"""
        self.stats.success_count = count
        if hasattr(self, 'stat_réussis'):
            self.stat_réussis.configure(text=str(count))
    
    def set_error_count(self, count: int):
        """Met à jour le nombre d'erreurs"""
        self.stats.error_count = count
        if hasattr(self, 'stat_échecs'):
            self.stat_échecs.configure(text=str(count))
    
    def start_stats_update(self):
        """Démarre la mise à jour automatique des statistiques"""
        def update_stats():
            while True:
                try:
                    elapsed = time.time() - self.start_time
                    
                    # Temps écoulé
                    elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))
                    if hasattr(self, 'stat_écoulé'):
                        self.after(0, lambda: self.stat_écoulé.configure(text=elapsed_str))
                    
                    # Débit
                    if elapsed > 0 and self.stats.current > 0:
                        rate = self.stats.current / elapsed
                        rate_str = f"{rate:.1f}/sec"
                        if hasattr(self, 'stat_débit'):
                            self.after(0, lambda: self.stat_débit.configure(text=rate_str))
                    
                    # ETA
                    if self.stats.current > 0 and self.stats.total > 0:
                        remaining = self.stats.total - self.stats.current
                        if elapsed > 0:
                            eta = remaining / (self.stats.current / elapsed)
                            eta_str = time.strftime("%H:%M:%S", time.gmtime(eta))
                            if hasattr(self, 'stat_eta'):
                                self.after(0, lambda: self.stat_eta.configure(text=eta_str))
                    
                    # Total
                    if hasattr(self, 'stat_total'):
                        self.after(0, lambda: self.stat_total.configure(text=str(self.stats.total)))
                    
                    time.sleep(1)  # Mettre à jour chaque seconde
                    
                except Exception:
                    break
        
        threading.Thread(target=update_stats, daemon=True).start()
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_closing(self):
        """Gestionnaire de fermeture"""
        self.main_progress.stop_animation()
        for key in self.multi_progress.progress_bars:
            self.multi_progress.stop_animation(key)
        
        self.grab_release()
        self.destroy()


class SimpleProgressOverlay(ctk.CTkFrame):
    """Overlay de progression simple pour intégration dans l'UI principale"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.setup_ui()
        self.pack_forget()  # Masquer par défaut
    
    def setup_ui(self):
        """Configure l'interface"""
        # Label de statut
        self.status_label = ctk.CTkLabel(
            self,
            text="Préparation...",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_label.pack(pady=(10, 5))
        
        # Barre de progression
        self.progress_bar = AnimatedProgressBar(
            self,
            height=20,
            corner_radius=10
        )
        self.progress_bar.pack(fill='x', padx=15, pady=5)
        
        # Statistiques rapides
        self.stats_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.stats_label.pack(pady=(5, 10))
    
    def show(self, status: str = "Traitement en cours..."):
        """Affiche l'overlay"""
        self.status_label.configure(text=status)
        self.progress_bar.set(0)
        self.progress_bar.start_animation()
        self.pack(fill='x', pady=10)
    
    def hide(self):
        """Masque l'overlay"""
        self.progress_bar.stop_animation()
        self.pack_forget()
    
    def update(self, current: int, total: int, status: str = ""):
        """Met à jour la progression"""
        # Progression
        percentage = (current / total * 100) if total > 0 else 0
        progress_value = current / total if total > 0 else 0
        self.progress_bar.set(progress_value)
        
        # Statut
        if status:
            self.status_label.configure(text=status)
        
        # Statistiques
        stats_text = f"{current}/{total} ({percentage:.1f}%)"
        self.stats_label.configure(text=stats_text)
        
        # Couleur selon progression
        if percentage == 100:
            self.progress_bar.set_color_theme('success')
        elif percentage > 50:
            self.progress_bar.set_color_theme('info')