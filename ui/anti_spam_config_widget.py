# -*- coding: utf-8 -*-
"""
Widget de configuration anti-spam entièrement personnalisable par l'utilisateur
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json
from typing import Callable, Optional
from utils.anti_spam_manager import (
    AntiSpamManager, SpamProtectionConfig, BehaviorPattern, RiskLevel,
    create_conservative_config, create_balanced_config, create_aggressive_config
)


class UserCustomizableAntiSpamWidget(ctk.CTkFrame):
    """Widget de configuration anti-spam 100% personnalisable"""
    
    def __init__(self, parent, anti_spam_manager: AntiSpamManager, on_config_change: Optional[Callable] = None):
        super().__init__(parent, corner_radius=15)
        
        self.anti_spam_manager = anti_spam_manager
        self.on_config_change = on_config_change
        self.config = anti_spam_manager.config
        
        # Variables pour tous les paramètres
        self.setup_config_variables()
        
        self.create_widgets()
        self.load_current_config()
    
    def setup_config_variables(self):
        """Initialise toutes les variables de configuration"""
        # Limites principales
        self.daily_limit_var = tk.IntVar()
        self.hourly_limit_var = tk.IntVar()
        self.burst_limit_var = tk.IntVar()
        
        # Délais
        self.min_delay_var = tk.IntVar()
        self.max_delay_var = tk.IntVar()
        
        # Pauses longues
        self.long_pause_after_var = tk.IntVar()
        self.long_pause_min_var = tk.IntVar()
        self.long_pause_max_var = tk.IntVar()
        
        # Pauses courtes après rafale
        self.burst_pause_min_var = tk.IntVar()
        self.burst_pause_max_var = tk.IntVar()
        
        # Comportement
        self.behavior_var = tk.StringVar()
        self.work_start_var = tk.IntVar()
        self.work_end_var = tk.IntVar()
        self.lunch_start_var = tk.IntVar()
        self.lunch_end_var = tk.IntVar()
        
        # Facteurs de risque
        self.warning_threshold_var = tk.DoubleVar()
        self.critical_threshold_var = tk.DoubleVar()
        self.weekend_factor_var = tk.DoubleVar()
        
        # Options
        self.expert_mode_var = tk.BooleanVar()
        self.weekend_slowdown_var = tk.BooleanVar()
        self.progressive_delays_var = tk.BooleanVar()
        self.delivery_monitoring_var = tk.BooleanVar()
        
        # Activations sélectives
        self.enable_daily_limit_var = tk.BooleanVar()
        self.enable_hourly_limit_var = tk.BooleanVar()
        self.enable_delays_var = tk.BooleanVar()
        self.enable_long_pauses_var = tk.BooleanVar()
        self.enable_working_hours_var = tk.BooleanVar()
    
    def create_widgets(self):
        """Crée l'interface de configuration personnalisable"""
        # Titre avec mode expert
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🛡️ Configuration Anti-Spam Personnalisée",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(side="left")
        
        # Mode Expert
        self.expert_cb = ctk.CTkCheckBox(
            title_frame,
            text="🔧 Mode Expert",
            variable=self.expert_mode_var,
            command=self.toggle_expert_mode,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("red", "orange")
        )
        self.expert_cb.pack(side="right")
        
        # Notebook avec tous les onglets
        self.notebook = ctk.CTkTabview(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Onglets
        self.limits_tab = self.notebook.add("📊 Limites")
        self.delays_tab = self.notebook.add("⏱️ Délais")
        self.behavior_tab = self.notebook.add("🎭 Comportement")
        self.advanced_tab = self.notebook.add("⚙️ Avancé")
        self.presets_tab = self.notebook.add("⚡ Préréglages")
        
        self.create_limits_tab()
        self.create_delays_tab()
        self.create_behavior_tab()
        self.create_advanced_tab()
        self.create_presets_tab()
        
        # Boutons d'action
        self.create_action_buttons()
    
    def create_limits_tab(self):
        """Onglet des limites - Entièrement personnalisable"""
        # Messages par jour
        daily_section = self.create_configurable_limit_section(
            self.limits_tab,
            "📅 Messages par jour",
            self.enable_daily_limit_var,
            self.daily_limit_var,
            default_value=80,
            min_val=1,
            max_val=1000,
            help_text="0 = illimité"
        )
        
        # Messages par heure
        hourly_section = self.create_configurable_limit_section(
            self.limits_tab,
            "⏰ Messages par heure",
            self.enable_hourly_limit_var,
            self.hourly_limit_var,
            default_value=15,
            min_val=1,
            max_val=200,
            help_text="0 = illimité"
        )
        
        # Messages en rafale
        burst_section = self.create_configurable_limit_section(
            self.limits_tab,
            "💥 Messages en rafale (avant pause)",
            None,  # Toujours activé
            self.burst_limit_var,
            default_value=10,
            min_val=1,
            max_val=100,
            help_text="Nombre de messages avant une pause courte"
        )
        
        # Informations
        info_frame = ctk.CTkFrame(self.limits_tab, corner_radius=10)
        info_frame.pack(fill="x", padx=10, pady=10)
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="💡 Astuce: Mettez 0 pour désactiver une limite. Mode Expert supprime toutes les protections.",
            font=ctk.CTkFont(size=10),
            wraplength=400,
            text_color="gray"
        )
        info_label.pack(padx=15, pady=10)
    
    def create_delays_tab(self):
        """Onglet des délais - Totalement configurable"""
        # Activation des délais
        enable_delays_frame = ctk.CTkFrame(self.delays_tab, fg_color="transparent")
        enable_delays_frame.pack(fill="x", padx=10, pady=10)
        
        enable_delays_cb = ctk.CTkCheckBox(
            enable_delays_frame,
            text="⏱️ Activer les délais intelligents",
            variable=self.enable_delays_var,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.update_delays_state
        )
        enable_delays_cb.pack(anchor="w")
        
        # Container des délais
        self.delays_container = ctk.CTkFrame(self.delays_tab, corner_radius=10)
        self.delays_container.pack(fill="x", padx=10, pady=10)
        
        # Délai minimum
        min_delay_section = self.create_configurable_delay_section(
            self.delays_container,
            "⏱️ Délai minimum entre messages",
            self.min_delay_var,
            default_value=30,
            max_val=3600,
            unit="secondes"
        )
        
        # Délai maximum
        max_delay_section = self.create_configurable_delay_section(
            self.delays_container,
            "⏱️ Délai maximum entre messages", 
            self.max_delay_var,
            default_value=180,
            max_val=7200,
            unit="secondes"
        )
        
        # Pauses après rafale
        ctk.CTkLabel(
            self.delays_container,
            text="⏸️ Pauses après rafale",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        burst_pause_frame = ctk.CTkFrame(self.delays_container, fg_color="transparent")
        burst_pause_frame.pack(fill="x", padx=15, pady=5)
        
        # Pause min après rafale
        burst_min_frame = ctk.CTkFrame(burst_pause_frame, fg_color="transparent")
        burst_min_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(burst_min_frame, text="Minimum:", font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.burst_pause_min_entry = ctk.CTkEntry(burst_min_frame, textvariable=self.burst_pause_min_var, width=80)
        self.burst_pause_min_entry.pack(anchor="w")
        ctk.CTkLabel(burst_min_frame, text="secondes", font=ctk.CTkFont(size=9)).pack(anchor="w")
        
        # Pause max après rafale
        burst_max_frame = ctk.CTkFrame(burst_pause_frame, fg_color="transparent")
        burst_max_frame.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(burst_max_frame, text="Maximum:", font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.burst_pause_max_entry = ctk.CTkEntry(burst_max_frame, textvariable=self.burst_pause_max_var, width=80)
        self.burst_pause_max_entry.pack(anchor="w")
        ctk.CTkLabel(burst_max_frame, text="secondes", font=ctk.CTkFont(size=9)).pack(anchor="w")
        
        # Pauses longues
        self.create_long_pauses_section()
    
    def create_long_pauses_section(self):
        """Section des pauses longues configurables"""
        long_pause_frame = ctk.CTkFrame(self.delays_tab, corner_radius=10)
        long_pause_frame.pack(fill="x", padx=10, pady=10)
        
        # Activation
        enable_long_cb = ctk.CTkCheckBox(
            long_pause_frame,
            text="⏸️ Activer les pauses longues",
            variable=self.enable_long_pauses_var,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.update_long_pauses_state
        )
        enable_long_cb.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Container des paramètres
        self.long_pauses_container = ctk.CTkFrame(long_pause_frame, fg_color="transparent")
        self.long_pauses_container.pack(fill="x", padx=15, pady=(0, 15))
        
        # Après combien de messages
        after_frame = ctk.CTkFrame(self.long_pauses_container, fg_color="transparent")
        after_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(after_frame, text="Déclencher une pause longue après:", font=ctk.CTkFont(size=11)).pack(side="left")
        self.long_pause_after_entry = ctk.CTkEntry(after_frame, textvariable=self.long_pause_after_var, width=80)
        self.long_pause_after_entry.pack(side="right", padx=(10, 0))
        ctk.CTkLabel(after_frame, text="messages", font=ctk.CTkFont(size=11)).pack(side="right")
        
        # Durée des pauses longues
        duration_frame = ctk.CTkFrame(self.long_pauses_container, fg_color="transparent")
        duration_frame.pack(fill="x", pady=10)
        
        # Min
        min_long_frame = ctk.CTkFrame(duration_frame, fg_color="transparent")
        min_long_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(min_long_frame, text="Durée minimum:", font=ctk.CTkFont(size=10)).pack(anchor="w")
        self.long_pause_min_entry = ctk.CTkEntry(min_long_frame, textvariable=self.long_pause_min_var, width=80)
        self.long_pause_min_entry.pack(anchor="w")
        ctk.CTkLabel(min_long_frame, text="secondes", font=ctk.CTkFont(size=9)).pack(anchor="w")
        
        # Max
        max_long_frame = ctk.CTkFrame(duration_frame, fg_color="transparent")
        max_long_frame.pack(side="right", fill="x", expand=True, padx=(10, 0))
        ctk.CTkLabel(max_long_frame, text="Durée maximum:", font=ctk.CTkFont(size=10)).pack(anchor="w")
        self.long_pause_max_entry = ctk.CTkEntry(max_long_frame, textvariable=self.long_pause_max_var, width=80)
        self.long_pause_max_entry.pack(anchor="w")
        ctk.CTkLabel(max_long_frame, text="secondes", font=ctk.CTkFont(size=9)).pack(anchor="w")
    
    def create_behavior_tab(self):
        """Onglet comportement - Entièrement personnalisable"""
        # Pattern de comportement
        pattern_frame = ctk.CTkFrame(self.behavior_tab, corner_radius=10)
        pattern_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(pattern_frame, text="🎭 Pattern de comportement:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))
        
        patterns = [
            ("👔 Employé de bureau", "office_worker"),
            ("💼 Heures d'affaires", "business_hours"),
            ("🌙 Utilisateur casual", "casual_user"),
            ("🔄 Flexible", "flexible"),
            ("🚫 Aucune restriction", "none")
        ]
        
        for text, value in patterns:
            radio = ctk.CTkRadioButton(pattern_frame, text=text, variable=self.behavior_var, value=value)
            radio.pack(anchor="w", padx=30, pady=3)
        
        # Heures de travail personnalisées
        hours_frame = ctk.CTkFrame(self.behavior_tab, corner_radius=10)
        hours_frame.pack(fill="x", padx=10, pady=10)
        
        # Activation
        enable_hours_cb = ctk.CTkCheckBox(
            hours_frame,
            text="🕐 Appliquer des heures de travail",
            variable=self.enable_working_hours_var,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.update_working_hours_state
        )
        enable_hours_cb.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Container des heures
        self.hours_container = ctk.CTkFrame(hours_frame, fg_color="transparent")
        self.hours_container.pack(fill="x", padx=15, pady=(0, 15))
        
        # Heures de travail
        work_hours_frame = ctk.CTkFrame(self.hours_container, fg_color="transparent")
        work_hours_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(work_hours_frame, text="Heures de travail:", font=ctk.CTkFont(size=11)).pack(side="left")
        
        self.work_start_combo = ctk.CTkComboBox(work_hours_frame, values=[f"{i}h" for i in range(0, 24)], 
                                               width=70, variable=self.work_start_var)
        self.work_start_combo.pack(side="right", padx=(5, 0))
        
        ctk.CTkLabel(work_hours_frame, text="à", font=ctk.CTkFont(size=11)).pack(side="right", padx=5)
        
        self.work_end_combo = ctk.CTkComboBox(work_hours_frame, values=[f"{i}h" for i in range(0, 24)], 
                                             width=70, variable=self.work_end_var)
        self.work_end_combo.pack(side="right", padx=(5, 0))
        
        # Pause déjeuner
        lunch_frame = ctk.CTkFrame(self.hours_container, fg_color="transparent")
        lunch_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(lunch_frame, text="Pause déjeuner:", font=ctk.CTkFont(size=11)).pack(side="left")
        
        self.lunch_start_combo = ctk.CTkComboBox(lunch_frame, values=[f"{i}h" for i in range(0, 24)], 
                                                width=70, variable=self.lunch_start_var)
        self.lunch_start_combo.pack(side="right", padx=(5, 0))
        
        ctk.CTkLabel(lunch_frame, text="à", font=ctk.CTkFont(size=11)).pack(side="right", padx=5)
        
        self.lunch_end_combo = ctk.CTkComboBox(lunch_frame, values=[f"{i}h" for i in range(0, 24)], 
                                              width=70, variable=self.lunch_end_var)
        self.lunch_end_combo.pack(side="right", padx=(5, 0))
    
    def create_advanced_tab(self):
        """Onglet des paramètres avancés"""
        # Facteurs de risque
        risk_frame = ctk.CTkFrame(self.advanced_tab, corner_radius=10)
        risk_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(risk_frame, text="⚠️ Seuils d'alerte:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Seuil d'avertissement
        warning_frame = ctk.CTkFrame(risk_frame, fg_color="transparent")
        warning_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(warning_frame, text="Avertissement à:", font=ctk.CTkFont(size=11)).pack(side="left")
        self.warning_entry = ctk.CTkEntry(warning_frame, textvariable=self.warning_threshold_var, width=80)
        self.warning_entry.pack(side="right", padx=(5, 0))
        ctk.CTkLabel(warning_frame, text="% de la limite", font=ctk.CTkFont(size=11)).pack(side="right")
        
        # Seuil critique
        critical_frame = ctk.CTkFrame(risk_frame, fg_color="transparent")
        critical_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        ctk.CTkLabel(critical_frame, text="Critique à:", font=ctk.CTkFont(size=11)).pack(side="left")
        self.critical_entry = ctk.CTkEntry(critical_frame, textvariable=self.critical_threshold_var, width=80)
        self.critical_entry.pack(side="right", padx=(5, 0))
        ctk.CTkLabel(critical_frame, text="% de la limite", font=ctk.CTkFont(size=11)).pack(side="right")
        
        # Options spéciales
        options_frame = ctk.CTkFrame(self.advanced_tab, corner_radius=10)
        options_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(options_frame, text="🔧 Options avancées:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Weekend
        weekend_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        weekend_frame.pack(fill="x", padx=15, pady=5)
        
        weekend_cb = ctk.CTkCheckBox(weekend_frame, text="🏖️ Ralentir le weekend", variable=self.weekend_slowdown_var)
        weekend_cb.pack(side="left")
        
        if self.weekend_slowdown_var.get():
            ctk.CTkLabel(weekend_frame, text="Facteur:", font=ctk.CTkFont(size=10)).pack(side="right", padx=(10, 5))
            self.weekend_factor_entry = ctk.CTkEntry(weekend_frame, textvariable=self.weekend_factor_var, width=60)
            self.weekend_factor_entry.pack(side="right")
        
        progressive_cb = ctk.CTkCheckBox(options_frame, text="📈 Délais progressifs", variable=self.progressive_delays_var)
        progressive_cb.pack(anchor="w", padx=15, pady=5)
        
        monitoring_cb = ctk.CTkCheckBox(options_frame, text="📊 Surveillance livraison", variable=self.delivery_monitoring_var)
        monitoring_cb.pack(anchor="w", padx=15, pady=(5, 15))
    
    def create_presets_tab(self):
        """Onglet des préréglages avec import/export"""
        # Préréglages standards
        standard_frame = ctk.CTkFrame(self.presets_tab, corner_radius=10)
        standard_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(standard_frame, text="⚡ Configurations Standards:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))
        
        presets = [
            ("🟢 Conservative", "conservative", "Sécurité maximale"),
            ("🟡 Équilibré", "balanced", "Recommandé pour la plupart"),
            ("🔴 Agressif", "aggressive", "Performance maximale, risque élevé")
        ]
        
        for color, preset_name, description in presets:
            preset_frame = ctk.CTkFrame(standard_frame, fg_color="transparent")
            preset_frame.pack(fill="x", padx=15, pady=5)
            
            ctk.CTkLabel(preset_frame, text=f"{color} {preset_name}", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
            ctk.CTkLabel(preset_frame, text=description, font=ctk.CTkFont(size=10)).pack(side="left", padx=(10, 0))
            
            apply_btn = ctk.CTkButton(preset_frame, text="Appliquer", width=80, height=25,
                                     command=lambda p=preset_name: self.apply_preset(p))
            apply_btn.pack(side="right")
        
        # Import/Export personnalisé
        custom_frame = ctk.CTkFrame(self.presets_tab, corner_radius=10)
        custom_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(custom_frame, text="💾 Configurations Personnalisées:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))
        
        buttons_frame = ctk.CTkFrame(custom_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        export_btn = ctk.CTkButton(buttons_frame, text="📤 Exporter Config", command=self.export_config, width=120)
        export_btn.pack(side="left", padx=(0, 10))
        
        import_btn = ctk.CTkButton(buttons_frame, text="📥 Importer Config", command=self.import_config, width=120)
        import_btn.pack(side="left")
        
        reset_btn = ctk.CTkButton(buttons_frame, text="🔄 Reset Usine", command=self.factory_reset, width=120,
                                 fg_color="red", hover_color="darkred")
        reset_btn.pack(side="right")
    
    def create_action_buttons(self):
        """Boutons d'action avec sauvegarde/test"""
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Sauvegarder
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Sauvegarder",
            command=self.save_config,
            width=130,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        save_btn.pack(side="left", padx=(0, 10))
        
        # Test
        test_btn = ctk.CTkButton(
            buttons_frame,
            text="🧪 Tester Config",
            command=self.test_configuration,
            width=130,
            height=40,
            fg_color="green"
        )
        test_btn.pack(side="left", padx=(0, 10))
        
        # Aperçu temps réel
        preview_btn = ctk.CTkButton(
            buttons_frame,
            text="👁️ Aperçu",
            command=self.show_config_preview,
            width=100,
            height=40
        )
        preview_btn.pack(side="right")
    
    # ============================================================================
    # MÉTHODES UTILITAIRES
    # ============================================================================
    
    def create_configurable_limit_section(self, parent, title, enable_var, value_var, default_value, min_val, max_val, help_text):
        """Crée une section de limite configurable"""
        section_frame = ctk.CTkFrame(parent, corner_radius=10)
        section_frame.pack(fill="x", padx=10, pady=8)
        
        # Header avec checkbox d'activation si fournie
        header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        if enable_var:
            enable_cb = ctk.CTkCheckBox(header_frame, text=title, variable=enable_var, 
                                       font=ctk.CTkFont(size=12, weight="bold"))
            enable_cb.pack(side="left")
        else:
            ctk.CTkLabel(header_frame, text=title, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        
        # Champ de saisie
        input_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        input_frame.pack(side="right")
        
        entry = ctk.CTkEntry(input_frame, textvariable=value_var, width=80)
        entry.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(input_frame, text="max", font=ctk.CTkFont(size=9)).pack(side="left")
        
        # Slider d'aide
        if max_val <= 1000:
            slider = ctk.CTkSlider(section_frame, from_=min_val, to=max_val, variable=value_var)
            slider.pack(fill="x", padx=15, pady=(0, 10))
        
        # Texte d'aide
        if help_text:
            help_label = ctk.CTkLabel(section_frame, text=f"💡 {help_text}", font=ctk.CTkFont(size=9), text_color="gray")
            help_label.pack(anchor="w", padx=15, pady=(0, 15))
        
        return section_frame
    
    def create_configurable_delay_section(self, parent, title, value_var, default_value, max_val, unit):
        """Crée une section de délai configurable"""
        section_frame = ctk.CTkFrame(parent, fg_color="transparent")
        section_frame.pack(fill="x", padx=15, pady=8)
        
        header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        header_frame.pack(fill="x")
        
        ctk.CTkLabel(header_frame, text=title, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left")
        
        input_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        input_frame.pack(side="right")
        
        entry = ctk.CTkEntry(input_frame, textvariable=value_var, width=80)
        entry.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(input_frame, text=unit, font=ctk.CTkFont(size=9)).pack(side="left")
        
        return section_frame
    
    def toggle_expert_mode(self):
        """Bascule le mode expert"""
        if self.expert_mode_var.get():
            result = messagebox.askyesno(
                "⚠️ Mode Expert",
                "Le mode expert désactive TOUTES les protections anti-spam.\n\n"
                "Cela signifie :\n"
                "• Aucune limite de messages\n"
                "• Aucun délai entre les envois\n" 
                "• Aucune pause automatique\n"
                "• Risque TRÈS ÉLEVÉ de détection\n\n"
                "Êtes-vous sûr de vouloir continuer ?"
            )
            
            if not result:
                self.expert_mode_var.set(False)
                return
            
            # Désactiver toutes les protections
            self.enable_daily_limit_var.set(False)
            self.enable_hourly_limit_var.set(False)
            self.enable_delays_var.set(False)
            self.enable_long_pauses_var.set(False)
            self.enable_working_hours_var.set(False)
            
            # Mettre des valeurs extrêmes
            self.daily_limit_var.set(10000)
            self.hourly_limit_var.set(1000)
            self.min_delay_var.set(0)
            self.max_delay_var.set(1)
            
            messagebox.showwarning("Mode Expert Activé", "⚠️ Toutes les protections sont désactivées !\nUtilisez avec EXTRÊME prudence.")
        
        self.update_all_states()
    
    def update_all_states(self):
        """Met à jour l'état de tous les widgets"""
        self.update_delays_state()
        self.update_long_pauses_state()
        self.update_working_hours_state()
    
    def update_delays_state(self):
        """Met à jour l'état des délais"""
        enabled = self.enable_delays_var.get() and not self.expert_mode_var.get()
        # Ici, vous pourriez activer/désactiver les widgets de délais
    
    def update_long_pauses_state(self):
        """Met à jour l'état des pauses longues"""
        enabled = self.enable_long_pauses_var.get() and not self.expert_mode_var.get()
        # Ici, vous pourriez activer/désactiver les widgets de pauses longues
    
    def update_working_hours_state(self):
        """Met à jour l'état des heures de travail"""
        enabled = self.enable_working_hours_var.get() and not self.expert_mode_var.get()
        # Ici, vous pourriez activer/désactiver les widgets d'heures
    
    def load_current_config(self):
        """Charge la configuration actuelle"""
        config = self.config
        
        # Charger toutes les valeurs
        self.daily_limit_var.set(config.max_messages_per_day)
        self.hourly_limit_var.set(config.max_messages_per_hour)
        self.burst_limit_var.set(config.max_messages_per_burst)
        self.min_delay_var.set(config.min_delay_between_messages)
        self.max_delay_var.set(config.max_delay_between_messages)
        self.long_pause_after_var.set(config.long_pause_after_count)
        self.long_pause_min_var.set(config.long_pause_min)
        self.long_pause_max_var.set(config.long_pause_max)
        self.burst_pause_min_var.set(config.pause_after_burst_min)
        self.burst_pause_max_var.set(config.pause_after_burst_max)
        self.behavior_var.set(config.behavior_pattern.value)
        self.work_start_var.set(config.working_hours_start)
        self.work_end_var.set(config.working_hours_end)
        self.lunch_start_var.set(config.lunch_break_start)
        self.lunch_end_var.set(config.lunch_break_end)
        self.warning_threshold_var.set(config.warning_threshold * 100)
        self.critical_threshold_var.set(config.critical_threshold * 100)
        self.weekend_factor_var.set(config.weekend_speed_factor)
        self.weekend_slowdown_var.set(config.enable_weekend_slowdown)
        self.progressive_delays_var.set(config.enable_progressive_delays)
        self.delivery_monitoring_var.set(config.enable_delivery_monitoring)
        
        # Activer les fonctionnalités par défaut
        self.enable_daily_limit_var.set(True)
        self.enable_hourly_limit_var.set(True)
        self.enable_delays_var.set(True)
        self.enable_long_pauses_var.set(True)
        self.enable_working_hours_var.set(True)
    
    def save_config(self):
        """Sauvegarde la configuration personnalisée"""
        try:
            # Créer la nouvelle configuration
            new_config = SpamProtectionConfig(
                max_messages_per_day=self.daily_limit_var.get() if self.enable_daily_limit_var.get() else 999999,
                max_messages_per_hour=self.hourly_limit_var.get() if self.enable_hourly_limit_var.get() else 999999,
                max_messages_per_burst=self.burst_limit_var.get(),
                min_delay_between_messages=self.min_delay_var.get() if self.enable_delays_var.get() else 0,
                max_delay_between_messages=self.max_delay_var.get() if self.enable_delays_var.get() else 1,
                pause_after_burst_min=self.burst_pause_min_var.get() if self.enable_delays_var.get() else 0,
                pause_after_burst_max=self.burst_pause_max_var.get() if self.enable_delays_var.get() else 1,
                long_pause_after_count=self.long_pause_after_var.get() if self.enable_long_pauses_var.get() else 999999,
                long_pause_min=self.long_pause_min_var.get() if self.enable_long_pauses_var.get() else 0,
                long_pause_max=self.long_pause_max_var.get() if self.enable_long_pauses_var.get() else 1,
                behavior_pattern=BehaviorPattern(self.behavior_var.get()),
                working_hours_start=self.work_start_var.get() if self.enable_working_hours_var.get() else 0,
                working_hours_end=self.work_end_var.get() if self.enable_working_hours_var.get() else 23,
                lunch_break_start=self.lunch_start_var.get() if self.enable_working_hours_var.get() else 0,
                lunch_break_end=self.lunch_end_var.get() if self.enable_working_hours_var.get() else 0,
                warning_threshold=self.warning_threshold_var.get() / 100,
                critical_threshold=self.critical_threshold_var.get() / 100,
                weekend_speed_factor=self.weekend_factor_var.get(),
                enable_weekend_slowdown=self.weekend_slowdown_var.get(),
                enable_progressive_delays=self.progressive_delays_var.get(),
                enable_delivery_monitoring=self.delivery_monitoring_var.get()
            )
            
            # Appliquer la configuration
            self.anti_spam_manager.config = new_config
            self.config = new_config
            
            if self.on_config_change:
                self.on_config_change(new_config)
            
            mode_text = "EXPERT (Aucune protection)" if self.expert_mode_var.get() else "STANDARD"
            messagebox.showinfo("✅ Configuration Sauvegardée", f"Configuration sauvegardée avec succès !\n\nMode: {mode_text}")
            
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
        
        self.config = config
        self.load_current_config()
        messagebox.showinfo("Préréglage Appliqué", f"Configuration '{preset_name}' appliquée.\nN'oubliez pas de sauvegarder !")
    
    def export_config(self):
        """Exporte la configuration vers un fichier"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Exporter la configuration",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                config_dict = {
                    "daily_limit": self.daily_limit_var.get(),
                    "hourly_limit": self.hourly_limit_var.get(),
                    "burst_limit": self.burst_limit_var.get(),
                    "min_delay": self.min_delay_var.get(),
                    "max_delay": self.max_delay_var.get(),
                    "long_pause_after": self.long_pause_after_var.get(),
                    "long_pause_min": self.long_pause_min_var.get(),
                    "long_pause_max": self.long_pause_max_var.get(),
                    "behavior_pattern": self.behavior_var.get(),
                    "work_start": self.work_start_var.get(),
                    "work_end": self.work_end_var.get(),
                    "expert_mode": self.expert_mode_var.get(),
                    "enable_delays": self.enable_delays_var.get(),
                    "enable_long_pauses": self.enable_long_pauses_var.get(),
                    "enable_working_hours": self.enable_working_hours_var.get()
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("✅ Export Réussi", f"Configuration exportée vers :\n{filename}")
        
        except Exception as e:
            messagebox.showerror("Erreur Export", f"Erreur lors de l'export : {str(e)}")
    
    def import_config(self):
        """Importe une configuration depuis un fichier"""
        try:
            filename = filedialog.askopenfilename(
                title="Importer une configuration",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    config_dict = json.load(f)
                
                # Charger les valeurs
                self.daily_limit_var.set(config_dict.get("daily_limit", 80))
                self.hourly_limit_var.set(config_dict.get("hourly_limit", 15))
                self.burst_limit_var.set(config_dict.get("burst_limit", 10))
                self.min_delay_var.set(config_dict.get("min_delay", 30))
                self.max_delay_var.set(config_dict.get("max_delay", 180))
                self.long_pause_after_var.set(config_dict.get("long_pause_after", 50))
                self.long_pause_min_var.set(config_dict.get("long_pause_min", 3600))
                self.long_pause_max_var.set(config_dict.get("long_pause_max", 7200))
                self.behavior_var.set(config_dict.get("behavior_pattern", "office_worker"))
                self.work_start_var.set(config_dict.get("work_start", 8))
                self.work_end_var.set(config_dict.get("work_end", 18))
                self.expert_mode_var.set(config_dict.get("expert_mode", False))
                self.enable_delays_var.set(config_dict.get("enable_delays", True))
                self.enable_long_pauses_var.set(config_dict.get("enable_long_pauses", True))
                self.enable_working_hours_var.set(config_dict.get("enable_working_hours", True))
                
                messagebox.showinfo("✅ Import Réussi", f"Configuration importée depuis :\n{filename}\nN'oubliez pas de sauvegarder !")
        
        except Exception as e:
            messagebox.showerror("Erreur Import", f"Erreur lors de l'import : {str(e)}")
    
    def factory_reset(self):
        """Remet la configuration d'usine"""
        if messagebox.askyesno("⚠️ Reset Usine", "Voulez-vous vraiment remettre tous les paramètres par défaut ?"):
            self.config = SpamProtectionConfig()
            self.expert_mode_var.set(False)
            self.load_current_config()
            messagebox.showinfo("Reset Effectué", "Configuration remise aux valeurs d'usine.")
    
    def test_configuration(self):
        """Teste la configuration actuelle"""
        try:
            can_send, reason, delay = self.anti_spam_manager.can_send_message()
            risk_analysis = self.anti_spam_manager.get_risk_analysis()
            
            test_msg = f"🧪 TEST DE CONFIGURATION\n\n"
            
            if self.expert_mode_var.get():
                test_msg += "⚠️ MODE EXPERT ACTIF - Aucune protection !\n\n"
            
            test_msg += f"📊 Statut actuel :\n"
            test_msg += f"• Envoi autorisé : {'✅ Oui' if can_send else '❌ Non'}\n"
            test_msg += f"• Raison : {reason}\n"
            test_msg += f"• Délai recommandé : {delay}s\n"
            test_msg += f"• Niveau de risque : {risk_analysis['risk_level'].upper()}\n\n"
            
            test_msg += f"⚙️ Configuration active :\n"
            test_msg += f"• Limite quotidienne : {self.daily_limit_var.get()}\n"
            test_msg += f"• Limite horaire : {self.hourly_limit_var.get()}\n"
            test_msg += f"• Délais : {self.min_delay_var.get()}s - {self.max_delay_var.get()}s\n"
            test_msg += f"• Pattern : {self.behavior_var.get()}"
            
            messagebox.showinfo("Résultat du Test", test_msg)
            
        except Exception as e:
            messagebox.showerror("Erreur Test", f"Erreur lors du test : {str(e)}")
    
    def show_config_preview(self):
        """Affiche un aperçu de la configuration"""
        preview_msg = "👁️ APERÇU DE LA CONFIGURATION\n\n"
        
        if self.expert_mode_var.get():
            preview_msg += "🚨 MODE EXPERT : Aucune protection active !\n\n"
        else:
            preview_msg += "🛡️ PROTECTIONS ACTIVES :\n"
            
            if self.enable_daily_limit_var.get():
                preview_msg += f"• Limite quotidienne : {self.daily_limit_var.get()} messages\n"
            
            if self.enable_hourly_limit_var.get():
                preview_msg += f"• Limite horaire : {self.hourly_limit_var.get()} messages\n"
            
            if self.enable_delays_var.get():
                preview_msg += f"• Délais entre messages : {self.min_delay_var.get()}-{self.max_delay_var.get()}s\n"
            
            if self.enable_long_pauses_var.get():
                preview_msg += f"• Pause longue après {self.long_pause_after_var.get()} messages\n"
            
            if self.enable_working_hours_var.get():
                preview_msg += f"• Heures de travail : {self.work_start_var.get()}h-{self.work_end_var.get()}h\n"
            
            preview_msg += f"\n🎭 Pattern : {self.behavior_var.get()}"
        
        messagebox.showinfo("Aperçu Configuration", preview_msg)
    
    # Méthodes d'assistance pour la mise à jour des affichages
    def update_daily_display(self):
        try:
            self.daily_value_label.configure(text=f"{self.daily_limit_var.get()} messages/jour")
        except:
            pass
    
    def update_hourly_display(self):
        try:
            self.hourly_value_label.configure(text=f"{self.hourly_limit_var.get()} messages/heure")
        except:
            pass
    
    def update_min_delay_display(self):
        try:
            self.min_delay_label.configure(text=f"{self.min_delay_var.get()}s")
        except:
            pass
    
    def update_max_delay_display(self):
        try:
            self.max_delay_label.configure(text=f"{self.max_delay_var.get()}s")
        except:
            pass