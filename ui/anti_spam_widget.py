# -*- coding: utf-8 -*-
"""
Widget d'interface pour la configuration anti-spam
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional
from utils.anti_spam_manager import (
    AntiSpamManager, SpamProtectionConfig, BehaviorPattern, RiskLevel,
    create_conservative_config, create_balanced_config, create_aggressive_config
)


class AntiSpamConfigWidget(ctk.CTkFrame):
    """Widget de configuration anti-spam avancé"""
    
    def __init__(self, parent, anti_spam_manager: AntiSpamManager, on_config_change: Optional[Callable] = None):
        super().__init__(parent, corner_radius=15)
        
        self.anti_spam_manager = anti_spam_manager
        self.on_config_change = on_config_change
        self.config = anti_spam_manager.config
        
        self.create_widgets()
        self.load_current_config()
    
    def create_widgets(self):
        """Crée l'interface de configuration"""
        # Titre
        title_label = ctk.CTkLabel(
            self,
            text="🛡️ Protection Anti-Spam Pro",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 10))
        
        # Notebook avec onglets
        self.notebook = ctk.CTkTabview(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Onglets
        self.limits_tab = self.notebook.add("📊 Limites")
        self.behavior_tab = self.notebook.add("🎭 Comportement")
        self.monitoring_tab = self.notebook.add("📈 Surveillance")
        self.presets_tab = self.notebook.add("⚡ Préréglages")
        
        self.create_limits_tab()
        self.create_behavior_tab() 
        self.create_monitoring_tab()
        self.create_presets_tab()
        
        # Boutons d'action
        self.create_action_buttons()
    
    def create_limits_tab(self):
        """Onglet de configuration des limites"""
        # Messages par jour
        daily_frame = ctk.CTkFrame(self.limits_tab, fg_color="transparent")
        daily_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(daily_frame, text="📅 Messages par jour:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.daily_limit_var = tk.IntVar(value=80)
        daily_slider = ctk.CTkSlider(daily_frame, from_=20, to=200, variable=self.daily_limit_var, number_of_steps=18)
        daily_slider.pack(fill="x", pady=(5, 0))
        
        self.daily_value_label = ctk.CTkLabel(daily_frame, text="80 messages/jour")
        self.daily_value_label.pack(anchor="w")
        daily_slider.configure(command=lambda v: self.daily_value_label.configure(text=f"{int(v)} messages/jour"))
        
        # Messages par heure
        hourly_frame = ctk.CTkFrame(self.limits_tab, fg_color="transparent") 
        hourly_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(hourly_frame, text="⏰ Messages par heure:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.hourly_limit_var = tk.IntVar(value=15)
        hourly_slider = ctk.CTkSlider(hourly_frame, from_=5, to=50, variable=self.hourly_limit_var, number_of_steps=9)
        hourly_slider.pack(fill="x", pady=(5, 0))
        
        self.hourly_value_label = ctk.CTkLabel(hourly_frame, text="15 messages/heure")
        self.hourly_value_label.pack(anchor="w")
        hourly_slider.configure(command=lambda v: self.hourly_value_label.configure(text=f"{int(v)} messages/heure"))
        
        # Délais entre messages
        delay_frame = ctk.CTkFrame(self.limits_tab, fg_color="transparent")
        delay_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(delay_frame, text="⏱️ Délai entre messages:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        
        delay_sub_frame = ctk.CTkFrame(delay_frame, fg_color="transparent")
        delay_sub_frame.pack(fill="x")
        
        # Min delay
        min_delay_frame = ctk.CTkFrame(delay_sub_frame, fg_color="transparent")
        min_delay_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(min_delay_frame, text="Minimum:", font=ctk.CTkFont(size=10)).pack(anchor="w")
        self.min_delay_var = tk.IntVar(value=30)
        min_delay_slider = ctk.CTkSlider(min_delay_frame, from_=15, to=300, variable=self.min_delay_var)
        min_delay_slider.pack(fill="x")
        self.min_delay_label = ctk.CTkLabel(min_delay_frame, text="30s", font=ctk.CTkFont(size=9))
        self.min_delay_label.pack(anchor="w")
        min_delay_slider.configure(command=lambda v: self.min_delay_label.configure(text=f"{int(v)}s"))
        
        # Max delay
        max_delay_frame = ctk.CTkFrame(delay_sub_frame, fg_color="transparent")
        max_delay_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(max_delay_frame, text="Maximum:", font=ctk.CTkFont(size=10)).pack(anchor="w")
        self.max_delay_var = tk.IntVar(value=180)
        max_delay_slider = ctk.CTkSlider(max_delay_frame, from_=60, to=600, variable=self.max_delay_var)
        max_delay_slider.pack(fill="x")
        self.max_delay_label = ctk.CTkLabel(max_delay_frame, text="180s", font=ctk.CTkFont(size=9))
        self.max_delay_label.pack(anchor="w")
        max_delay_slider.configure(command=lambda v: self.max_delay_label.configure(text=f"{int(v)}s"))
    
    def create_behavior_tab(self):
        """Onglet de configuration du comportement"""
        # Pattern de comportement
        pattern_frame = ctk.CTkFrame(self.behavior_tab, fg_color="transparent")
        pattern_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(pattern_frame, text="🎭 Pattern de comportement:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 5))
        
        self.behavior_var = tk.StringVar(value="office_worker")
        patterns = [
            ("👔 Employé de bureau (8h-18h)", "office_worker"),
            ("💼 Heures d'affaires (9h-17h)", "business_hours"),
            ("🌙 Utilisateur casual (plus le soir)", "casual_user"),
            ("🔄 Flexible (6h-22h)", "flexible")
        ]
        
        for text, value in patterns:
            radio = ctk.CTkRadioButton(pattern_frame, text=text, variable=self.behavior_var, value=value)
            radio.pack(anchor="w", padx=20, pady=2)
        
        # Heures de travail personnalisées
        hours_frame = ctk.CTkFrame(self.behavior_tab, fg_color="transparent")
        hours_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(hours_frame, text="🕐 Heures de travail personnalisées:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        
        hours_sub_frame = ctk.CTkFrame(hours_frame, fg_color="transparent")
        hours_sub_frame.pack(fill="x")
        
        # Début
        start_frame = ctk.CTkFrame(hours_sub_frame, fg_color="transparent")
        start_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(start_frame, text="Début:", font=ctk.CTkFont(size=10)).pack(anchor="w")
        self.work_start_var = tk.IntVar(value=8)
        start_combo = ctk.CTkComboBox(start_frame, values=[f"{i}h" for i in range(6, 12)], variable=self.work_start_var, width=80)
        start_combo.pack()
        
        # Fin
        end_frame = ctk.CTkFrame(hours_sub_frame, fg_color="transparent")
        end_frame.pack(side="right", fill="x", expand=True, padx=(10, 0))
        ctk.CTkLabel(end_frame, text="Fin:", font=ctk.CTkFont(size=10)).pack(anchor="w")
        self.work_end_var = tk.IntVar(value=18)
        end_combo = ctk.CTkComboBox(end_frame, values=[f"{i}h" for i in range(15, 23)], variable=self.work_end_var, width=80)
        end_combo.pack()
        
        # Options avancées
        advanced_frame = ctk.CTkFrame(self.behavior_tab, fg_color="transparent")
        advanced_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(advanced_frame, text="⚙️ Options avancées:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        
        self.weekend_slowdown_var = tk.BooleanVar(value=True)
        weekend_cb = ctk.CTkCheckBox(advanced_frame, text="🏖️ Ralentir le weekend", variable=self.weekend_slowdown_var)
        weekend_cb.pack(anchor="w", padx=20, pady=2)
        
        self.progressive_delays_var = tk.BooleanVar(value=True)
        progressive_cb = ctk.CTkCheckBox(advanced_frame, text="📈 Délais progressifs", variable=self.progressive_delays_var)
        progressive_cb.pack(anchor="w", padx=20, pady=2)
        
        self.delivery_monitoring_var = tk.BooleanVar(value=True)
        monitoring_cb = ctk.CTkCheckBox(advanced_frame, text="📊 Surveillance livraison", variable=self.delivery_monitoring_var)
        monitoring_cb.pack(anchor="w", padx=20, pady=2)
    
    def create_monitoring_tab(self):
        """Onglet de surveillance et statistiques"""
        # Statistiques du jour
        today_frame = ctk.CTkFrame(self.monitoring_tab, corner_radius=10)
        today_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(today_frame, text="📊 Aujourd'hui", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        self.today_stats_frame = ctk.CTkFrame(today_frame, fg_color="transparent")
        self.today_stats_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Analyse de risque
        risk_frame = ctk.CTkFrame(self.monitoring_tab, corner_radius=10)
        risk_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(risk_frame, text="🛡️ Analyse de Risque", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        self.risk_analysis_frame = ctk.CTkFrame(risk_frame, fg_color="transparent")
        self.risk_analysis_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Statistiques de la semaine
        week_frame = ctk.CTkFrame(self.monitoring_tab, corner_radius=10)
        week_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(week_frame, text="📅 Cette Semaine", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        self.week_stats_frame = ctk.CTkFrame(week_frame, fg_color="transparent")
        self.week_stats_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Bouton de rafraîchissement
        refresh_btn = ctk.CTkButton(
            self.monitoring_tab,
            text="🔄 Actualiser",
            command=self.refresh_monitoring,
            width=120,
            height=30
        )
        refresh_btn.pack(pady=10)
        
        # Charger les stats initiales
        self.refresh_monitoring()
    
    def create_presets_tab(self):
        """Onglet des préréglages"""
        ctk.CTkLabel(self.presets_tab, text="⚡ Configurations Prédéfinies", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 15))
        
        # Conservative
        conservative_frame = ctk.CTkFrame(self.presets_tab, corner_radius=10)
        conservative_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(conservative_frame, text="🟢 Conservative (Risque Minimal)", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        ctk.CTkLabel(conservative_frame, text="• 50 messages/jour • 8 messages/heure • Délais longs", font=ctk.CTkFont(size=10)).pack(anchor="w", padx=15)
        
        conservative_btn = ctk.CTkButton(
            conservative_frame,
            text="Appliquer",
            command=lambda: self.apply_preset("conservative"),
            width=100,
            height=25
        )
        conservative_btn.pack(anchor="e", padx=15, pady=(0, 10))
        
        # Balanced
        balanced_frame = ctk.CTkFrame(self.presets_tab, corner_radius=10)
        balanced_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(balanced_frame, text="🟡 Équilibré (Recommandé)", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        ctk.CTkLabel(balanced_frame, text="• 80 messages/jour • 15 messages/heure • Délais moyens", font=ctk.CTkFont(size=10)).pack(anchor="w", padx=15)
        
        balanced_btn = ctk.CTkButton(
            balanced_frame,
            text="Appliquer",
            command=lambda: self.apply_preset("balanced"),
            width=100,
            height=25
        )
        balanced_btn.pack(anchor="e", padx=15, pady=(0, 10))
        
        # Aggressive
        aggressive_frame = ctk.CTkFrame(self.presets_tab, corner_radius=10)
        aggressive_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(aggressive_frame, text="🔴 Agressif (Risque Élevé)", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        ctk.CTkLabel(aggressive_frame, text="• 120 messages/jour • 25 messages/heure • Délais courts", font=ctk.CTkFont(size=10)).pack(anchor="w", padx=15)
        
        aggressive_btn = ctk.CTkButton(
            aggressive_frame,
            text="Appliquer",
            command=lambda: self.apply_preset("aggressive"),
            width=100,
            height=25,
            fg_color=("red", "darkred")
        )
        aggressive_btn.pack(anchor="e", padx=15, pady=(0, 10))
        
        # Avertissement
        warning_label = ctk.CTkLabel(
            self.presets_tab,
            text="⚠️ Les configurations agressives augmentent le risque de détection spam",
            font=ctk.CTkFont(size=10),
            text_color="orange"
        )
        warning_label.pack(pady=10)
    
    def create_action_buttons(self):
        """Boutons d'action principaux"""
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Sauvegarder
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Sauvegarder",
            command=self.save_config,
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        save_btn.pack(side="left", padx=(0, 10))
        
        # Réinitialiser
        reset_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 Réinitialiser", 
            command=self.reset_to_defaults,
            width=120,
            height=35,
            fg_color=("gray", "darkgray")
        )
        reset_btn.pack(side="left", padx=(0, 10))
        
        # Test de configuration
        test_btn = ctk.CTkButton(
            buttons_frame,
            text="🧪 Tester",
            command=self.test_configuration,
            width=120,
            height=35,
            fg_color=("green", "darkgreen")
        )
        test_btn.pack(side="right")
    
    def load_current_config(self):
        """Charge la configuration actuelle dans l'interface"""
        config = self.config
        
        # Limites
        self.daily_limit_var.set(config.max_messages_per_day)
        self.hourly_limit_var.set(config.max_messages_per_hour)
        self.min_delay_var.set(config.min_delay_between_messages)
        self.max_delay_var.set(config.max_delay_between_messages)
        
        # Mise à jour des labels
        self.daily_value_label.configure(text=f"{config.max_messages_per_day} messages/jour")
        self.hourly_value_label.configure(text=f"{config.max_messages_per_hour} messages/heure")
        self.min_delay_label.configure(text=f"{config.min_delay_between_messages}s")
        self.max_delay_label.configure(text=f"{config.max_delay_between_messages}s")
        
        # Comportement
        self.behavior_var.set(config.behavior_pattern.value)
        self.work_start_var.set(config.working_hours_start)
        self.work_end_var.set(config.working_hours_end)
        self.weekend_slowdown_var.set(config.enable_weekend_slowdown)
        self.progressive_delays_var.set(config.enable_progressive_delays)
        self.delivery_monitoring_var.set(config.enable_delivery_monitoring)
    
    def save_config(self):
        """Sauvegarde la configuration"""
        try:
            # Validation
            if self.min_delay_var.get() >= self.max_delay_var.get():
                messagebox.showerror("Erreur", "Le délai minimum doit être inférieur au délai maximum")
                return
            
            if self.work_start_var.get() >= self.work_end_var.get():
                messagebox.showerror("Erreur", "L'heure de début doit être antérieure à l'heure de fin")
                return
            
            # Créer la nouvelle configuration
            new_config = SpamProtectionConfig(
                max_messages_per_day=self.daily_limit_var.get(),
                max_messages_per_hour=self.hourly_limit_var.get(),
                min_delay_between_messages=self.min_delay_var.get(),
                max_delay_between_messages=self.max_delay_var.get(),
                behavior_pattern=BehaviorPattern(self.behavior_var.get()),
                working_hours_start=self.work_start_var.get(),
                working_hours_end=self.work_end_var.get(),
                enable_weekend_slowdown=self.weekend_slowdown_var.get(),
                enable_progressive_delays=self.progressive_delays_var.get(),
                enable_delivery_monitoring=self.delivery_monitoring_var.get()
            )
            
            # Appliquer la configuration
            self.anti_spam_manager.config = new_config
            self.config = new_config
            
            # Callback si défini
            if self.on_config_change:
                self.on_config_change(new_config)
            
            messagebox.showinfo("Succès", "Configuration sauvegardée avec succès !")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {str(e)}")
    
    def apply_preset(self, preset_name: str):
        """Applique un préréglage"""
        if preset_name == "conservative":
            config = create_conservative_config()
        elif preset_name == "balanced":
            config = create_balanced_config()
        elif preset_name == "aggressive":
            config = create_aggressive_config()
        else:
            return
        
        # Appliquer à l'interface
        self.config = config
        self.load_current_config()
        
        messagebox.showinfo("Préréglage appliqué", f"Configuration '{preset_name}' appliquée.\nN'oubliez pas de sauvegarder !")
    
    def reset_to_defaults(self):
        """Remet les valeurs par défaut"""
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment réinitialiser à la configuration par défaut ?"):
            self.config = SpamProtectionConfig()
            self.load_current_config()
    
    def test_configuration(self):
        """Teste la configuration actuelle"""
        try:
            # Simulation d'un test
            can_send, reason, delay = self.anti_spam_manager.can_send_message()
            
            if can_send:
                test_msg = (
                    f"✅ Configuration valide !\n\n"
                    f"📤 Envoi autorisé\n"
                    f"⏱️ Délai recommandé : {delay}s\n"
                    f"🎯 Raison : {reason}"
                )
                messagebox.showinfo("Test réussi", test_msg)
            else:
                test_msg = (
                    f"⚠️ Envoi actuellement bloqué\n\n"
                    f"🚫 Raison : {reason}\n"
                    f"⏳ Délai d'attente : {delay}s"
                )
                messagebox.showwarning("Test - Envoi bloqué", test_msg)
                
        except Exception as e:
            messagebox.showerror("Erreur de test", f"Erreur lors du test : {str(e)}")
    
    def refresh_monitoring(self):
        """Actualise les données de surveillance"""
        try:
            # Nettoyer les frames existants
            for widget in self.today_stats_frame.winfo_children():
                widget.destroy()
            for widget in self.risk_analysis_frame.winfo_children():
                widget.destroy()
            for widget in self.week_stats_frame.winfo_children():
                widget.destroy()
            
            # Stats du jour
            today_stats = self.anti_spam_manager.get_today_stats()
            
            stats_text = [
                f"📊 Messages envoyés: {today_stats.messages_sent}",
                f"✅ Messages livrés: {today_stats.messages_delivered}",
                f"❌ Messages échoués: {today_stats.messages_failed}",
                f"⏸️ Pauses prises: {today_stats.pauses_taken}"
            ]
            
            for stat in stats_text:
                label = ctk.CTkLabel(self.today_stats_frame, text=stat, font=ctk.CTkFont(size=10))
                label.pack(anchor="w", padx=5, pady=1)
            
            # Analyse de risque
            risk_analysis = self.anti_spam_manager.get_risk_analysis()
            
            # Niveau de risque avec couleur
            risk_colors = {
                "low": "green",
                "medium": "orange", 
                "high": "red",
                "critical": "darkred"
            }
            
            risk_color = risk_colors.get(risk_analysis["risk_level"], "gray")
            risk_label = ctk.CTkLabel(
                self.risk_analysis_frame,
                text=f"🛡️ Risque: {risk_analysis['risk_level'].upper()}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=risk_color
            )
            risk_label.pack(anchor="w", padx=5, pady=2)
            
            # Recommandations
            for rec in risk_analysis["recommendations"][:3]:  # Max 3 recommandations
                rec_label = ctk.CTkLabel(
                    self.risk_analysis_frame,
                    text=f"• {rec}",
                    font=ctk.CTkFont(size=9),
                    wraplength=300
                )
                rec_label.pack(anchor="w", padx=15, pady=1)
            
            # Stats de la semaine
            week_stats = self.anti_spam_manager.get_weekly_stats()
            
            week_text = [
                f"📊 Total semaine: {week_stats['messages_sent']}",
                f"📈 Moyenne/jour: {week_stats['average_per_day']:.1f}",
                f"🎯 Taux livraison: {week_stats['delivery_rate']:.1f}%"
            ]
            
            for stat in week_text:
                label = ctk.CTkLabel(self.week_stats_frame, text=stat, font=ctk.CTkFont(size=10))
                label.pack(anchor="w", padx=5, pady=1)
                
        except Exception as e:
            print(f"Erreur refresh monitoring: {e}")


class AntiSpamStatusWidget(ctk.CTkFrame):
    """Widget compact d'affichage du statut anti-spam"""
    
    def __init__(self, parent, anti_spam_manager: AntiSpamManager):
        super().__init__(parent, corner_radius=10)
        
        self.anti_spam_manager = anti_spam_manager
        self.create_widgets()
        self.update_status()
    
    def create_widgets(self):
        """Crée les widgets d'affichage de statut"""
        # Status principal
        self.status_label = ctk.CTkLabel(
            self,
            text="🛡️ Protection: Active",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Compteur de messages
        self.counter_label = ctk.CTkLabel(
            self,
            text="0/80 aujourd'hui",
            font=ctk.CTkFont(size=10)
        )
        self.counter_label.pack(side="left", padx=(0, 10))
        
        # Niveau de risque
        self.risk_label = ctk.CTkLabel(
            self,
            text="🟢 Faible",
            font=ctk.CTkFont(size=10, weight="bold")
        )
        self.risk_label.pack(side="right", padx=10)
    
    def update_status(self):
        """Met à jour l'affichage du statut"""
        try:
            today_stats = self.anti_spam_manager.get_today_stats()
            risk_analysis = self.anti_spam_manager.get_risk_analysis()
            
            # Compteur
            limit = self.anti_spam_manager.config.max_messages_per_day
            self.counter_label.configure(text=f"{today_stats.messages_sent}/{limit} aujourd'hui")
            
            # Niveau de risque
            risk_level = risk_analysis["risk_level"]
            risk_colors = {
                "low": ("🟢 Faible", "green"),
                "medium": ("🟡 Moyen", "orange"),
                "high": ("🟠 Élevé", "red"),
                "critical": ("🔴 Critique", "darkred")
            }
            
            risk_text, risk_color = risk_colors.get(risk_level, ("❓ Inconnu", "gray"))
            self.risk_label.configure(text=risk_text, text_color=risk_color)
            
            # Statut général
            can_send, reason, _ = self.anti_spam_manager.can_send_message()
            if can_send:
                self.status_label.configure(text="🛡️ Protection: Prêt", text_color="green")
            else:
                self.status_label.configure(text="🛡️ Protection: Pause", text_color="orange")
                
        except Exception as e:
            print(f"Erreur update status: {e}")