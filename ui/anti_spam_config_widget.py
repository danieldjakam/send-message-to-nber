# -*- coding: utf-8 -*-
"""
Widget de configuration anti-spam entièrement personnalisable
Interface utilisateur complète pour tous les paramètres anti-spam
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import time
from typing import Dict, Any, List, Callable, Optional, Tuple
from utils.anti_spam_manager import AntiSpamManager, AntiSpamConfig, BehaviorPattern, RiskLevel
from utils.logger import logger


class UserCustomizableAntiSpamWidget(ctk.CTkFrame):
    """Widget entièrement personnalisable pour la configuration anti-spam"""
    
    def __init__(self, parent, anti_spam_manager: AntiSpamManager, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.anti_spam_manager = anti_spam_manager
        self.config = anti_spam_manager.config
        
        # Variables de l'interface
        self.setup_variables()
        
        # Callbacks
        self.on_config_change: Optional[Callable] = None
        self.on_test_config: Optional[Callable] = None
        
        # Interface utilisateur
        self.create_interface()
        
        # Charger la configuration actuelle
        self.load_current_config()
        
        # Connecter les traces pour la sauvegarde automatique
        self.setup_auto_save()
    
    def setup_variables(self):
        """Initialise toutes les variables de l'interface"""
        # Mode expert
        self.expert_mode_var = tk.BooleanVar()
        
        # Limites
        self.enable_daily_limit_var = tk.BooleanVar()
        self.daily_limit_var = tk.IntVar()
        self.enable_hourly_limit_var = tk.BooleanVar()
        self.hourly_limit_var = tk.IntVar()
        
        # Délais
        self.enable_delays_var = tk.BooleanVar()
        self.min_delay_var = tk.IntVar()
        self.max_delay_var = tk.IntVar()
        
        # Heures de travail
        self.enable_working_hours_var = tk.BooleanVar()
        self.work_start_var = tk.IntVar()
        self.work_end_var = tk.IntVar()
        
        # Pattern de comportement
        self.behavior_pattern_var = tk.StringVar()
        
        # Protections avancées
        self.enable_weekend_protection_var = tk.BooleanVar()
        self.enable_risk_analysis_var = tk.BooleanVar()
        self.enable_multi_day_var = tk.BooleanVar()
        
        # Configuration personnalisée
        self.custom_delays_text = tk.StringVar()
        self.custom_hours_text = tk.StringVar()
    
    def create_interface(self):
        """Crée l'interface utilisateur complète"""
        # Titre principal
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill='x', pady=(10, 20))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🛡️ Configuration Anti-Spam Avancée",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(side='left')
        
        # Bouton de statut
        self.status_btn = ctk.CTkButton(
            title_frame,
            text="📊 Statut",
            width=80,
            height=30,
            command=self.show_status,
            font=ctk.CTkFont(size=11)
        )
        self.status_btn.pack(side='right', padx=(10, 0))
        
        # Notebook pour organiser les onglets
        self.notebook = ctk.CTkTabview(self, height=500)
        self.notebook.pack(fill='both', expand=True, pady=10)
        
        # Onglets
        self.create_general_tab()
        self.create_limits_tab()
        self.create_timing_tab()
        self.create_behavior_tab()
        self.create_advanced_tab()
        self.create_expert_tab()
        
        # Boutons d'action en bas
        self.create_action_buttons()
    
    def create_general_tab(self):
        """Onglet des paramètres généraux"""
        tab = self.notebook.add("📋 Général")
        
        # Mode expert
        expert_frame = ctk.CTkFrame(tab)
        expert_frame.pack(fill='x', padx=15, pady=10)
        
        expert_label = ctk.CTkLabel(
            expert_frame,
            text="⚠️ Mode Expert",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        expert_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        expert_cb = ctk.CTkCheckBox(
            expert_frame,
            text="Désactiver TOUTES les protections anti-spam",
            variable=self.expert_mode_var,
            command=self.toggle_expert_mode,
            font=ctk.CTkFont(size=12),
            text_color=("red", "red")
        )
        expert_cb.pack(anchor='w', padx=15, pady=(0, 5))
        
        expert_warning = ctk.CTkLabel(
            expert_frame,
            text="⚠️ ATTENTION: En mode expert, aucune protection n'est appliquée.\n"
                 "Utilisez uniquement si vous savez ce que vous faites.",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray70"),
            wraplength=400
        )
        expert_warning.pack(anchor='w', padx=15, pady=(0, 10))
        
        # État actuel
        status_frame = ctk.CTkFrame(tab)
        status_frame.pack(fill='x', padx=15, pady=10)
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="📊 État Actuel",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        status_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        self.status_text = ctk.CTkTextbox(
            status_frame,
            height=100,
            font=ctk.CTkFont(size=11)
        )
        self.status_text.pack(fill='x', padx=15, pady=(0, 10))
        
        # Bouton de rafraîchissement du statut
        refresh_btn = ctk.CTkButton(
            status_frame,
            text="🔄 Actualiser le statut",
            command=self.update_status_display,
            height=30,
            width=150
        )
        refresh_btn.pack(pady=(0, 10))
    
    def create_limits_tab(self):
        """Onglet de configuration des limites"""
        tab = self.notebook.add("📊 Limites")
        
        # Limites quotidiennes
        daily_frame = ctk.CTkFrame(tab)
        daily_frame.pack(fill='x', padx=15, pady=10)
        
        daily_label = ctk.CTkLabel(
            daily_frame,
            text="📅 Limites Quotidiennes",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        daily_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        daily_enable = ctk.CTkCheckBox(
            daily_frame,
            text="Activer la limite quotidienne",
            variable=self.enable_daily_limit_var
        )
        daily_enable.pack(anchor='w', padx=15, pady=5)
        
        daily_controls = ctk.CTkFrame(daily_frame, fg_color="transparent")
        daily_controls.pack(fill='x', padx=15, pady=5)
        
        ctk.CTkLabel(daily_controls, text="Limite:").pack(side='left')
        daily_entry = ctk.CTkEntry(
            daily_controls,
            textvariable=self.daily_limit_var,
            width=100,
            placeholder_text="500"
        )
        daily_entry.pack(side='left', padx=(10, 5))
        ctk.CTkLabel(daily_controls, text="messages par jour").pack(side='left')
        
        # Slider pour limite quotidienne
        daily_slider = ctk.CTkSlider(
            daily_frame,
            from_=50,
            to=2000,
            variable=self.daily_limit_var,
            number_of_steps=39
        )
        daily_slider.pack(fill='x', padx=15, pady=(5, 10))
        
        # Limites horaires
        hourly_frame = ctk.CTkFrame(tab)
        hourly_frame.pack(fill='x', padx=15, pady=10)
        
        hourly_label = ctk.CTkLabel(
            hourly_frame,
            text="⏰ Limites Horaires",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        hourly_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        hourly_enable = ctk.CTkCheckBox(
            hourly_frame,
            text="Activer la limite horaire",
            variable=self.enable_hourly_limit_var
        )
        hourly_enable.pack(anchor='w', padx=15, pady=5)
        
        hourly_controls = ctk.CTkFrame(hourly_frame, fg_color="transparent")
        hourly_controls.pack(fill='x', padx=15, pady=5)
        
        ctk.CTkLabel(hourly_controls, text="Limite:").pack(side='left')
        hourly_entry = ctk.CTkEntry(
            hourly_controls,
            textvariable=self.hourly_limit_var,
            width=100,
            placeholder_text="50"
        )
        hourly_entry.pack(side='left', padx=(10, 5))
        ctk.CTkLabel(hourly_controls, text="messages par heure").pack(side='left')
        
        # Slider pour limite horaire
        hourly_slider = ctk.CTkSlider(
            hourly_frame,
            from_=10,
            to=200,
            variable=self.hourly_limit_var,
            number_of_steps=19
        )
        hourly_slider.pack(fill='x', padx=15, pady=(5, 10))
    
    def create_timing_tab(self):
        """Onglet de configuration des délais"""
        tab = self.notebook.add("⏱️ Délais")
        
        # Délais intelligents
        delay_frame = ctk.CTkFrame(tab)
        delay_frame.pack(fill='x', padx=15, pady=10)
        
        delay_label = ctk.CTkLabel(
            delay_frame,
            text="⏱️ Délais Intelligents",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        delay_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        delay_enable = ctk.CTkCheckBox(
            delay_frame,
            text="Activer les délais intelligents",
            variable=self.enable_delays_var
        )
        delay_enable.pack(anchor='w', padx=15, pady=5)
        
        # Délai minimum
        min_frame = ctk.CTkFrame(delay_frame, fg_color="transparent")
        min_frame.pack(fill='x', padx=15, pady=5)
        
        ctk.CTkLabel(min_frame, text="Délai minimum:").pack(side='left')
        min_entry = ctk.CTkEntry(
            min_frame,
            textvariable=self.min_delay_var,
            width=80,
            placeholder_text="30"
        )
        min_entry.pack(side='left', padx=(10, 5))
        ctk.CTkLabel(min_frame, text="secondes").pack(side='left')
        
        min_slider = ctk.CTkSlider(
            delay_frame,
            from_=5,
            to=300,
            variable=self.min_delay_var,
            number_of_steps=59
        )
        min_slider.pack(fill='x', padx=15, pady=2)
        
        # Délai maximum
        max_frame = ctk.CTkFrame(delay_frame, fg_color="transparent")
        max_frame.pack(fill='x', padx=15, pady=5)
        
        ctk.CTkLabel(max_frame, text="Délai maximum:").pack(side='left')
        max_entry = ctk.CTkEntry(
            max_frame,
            textvariable=self.max_delay_var,
            width=80,
            placeholder_text="180"
        )
        max_entry.pack(side='left', padx=(10, 5))
        ctk.CTkLabel(max_frame, text="secondes").pack(side='left')
        
        max_slider = ctk.CTkSlider(
            delay_frame,
            from_=60,
            to=3600,
            variable=self.max_delay_var,
            number_of_steps=59
        )
        max_slider.pack(fill='x', padx=15, pady=(2, 10))
        
        # Heures de travail
        work_frame = ctk.CTkFrame(tab)
        work_frame.pack(fill='x', padx=15, pady=10)
        
        work_label = ctk.CTkLabel(
            work_frame,
            text="🕐 Heures de Travail",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        work_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        work_enable = ctk.CTkCheckBox(
            work_frame,
            text="Respecter les heures de travail",
            variable=self.enable_working_hours_var
        )
        work_enable.pack(anchor='w', padx=15, pady=5)
        
        work_controls = ctk.CTkFrame(work_frame, fg_color="transparent")
        work_controls.pack(fill='x', padx=15, pady=5)
        
        ctk.CTkLabel(work_controls, text="De").pack(side='left')
        start_combo = ctk.CTkComboBox(
            work_controls,
            values=[f"{i:02d}h00" for i in range(24)],
            width=80,
            state="readonly"
        )
        start_combo.pack(side='left', padx=(10, 10))
        
        ctk.CTkLabel(work_controls, text="à").pack(side='left')
        end_combo = ctk.CTkComboBox(
            work_controls,
            values=[f"{i:02d}h00" for i in range(24)],
            width=80,
            state="readonly"
        )
        end_combo.pack(side='left', padx=(10, 0))
        
        # Lier les combobox aux variables
        def on_start_change(value):
            self.work_start_var.set(int(value[:2]))
        
        def on_end_change(value):
            self.work_end_var.set(int(value[:2]))
        
        start_combo.configure(command=on_start_change)
        end_combo.configure(command=on_end_change)
        
        self.start_combo = start_combo
        self.end_combo = end_combo
        
        # Délais personnalisés
        custom_frame = ctk.CTkFrame(work_frame)
        custom_frame.pack(fill='x', padx=15, pady=(10, 10))
        
        ctk.CTkLabel(
            custom_frame,
            text="⚙️ Délais Personnalisés (optionnel)",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor='w', padx=10, pady=(5, 0))
        
        ctk.CTkLabel(
            custom_frame,
            text="Liste de délais séparés par des virgules (ex: 30,60,90,120):",
            font=ctk.CTkFont(size=10)
        ).pack(anchor='w', padx=10, pady=2)
        
        custom_entry = ctk.CTkEntry(
            custom_frame,
            textvariable=self.custom_delays_text,
            placeholder_text="30,60,90,120,180"
        )
        custom_entry.pack(fill='x', padx=10, pady=(0, 10))
    
    def create_behavior_tab(self):
        """Onglet de configuration du comportement"""
        tab = self.notebook.add("🎭 Comportement")
        
        # Pattern de comportement
        pattern_frame = ctk.CTkFrame(tab)
        pattern_frame.pack(fill='x', padx=15, pady=10)
        
        pattern_label = ctk.CTkLabel(
            pattern_frame,
            text="🎭 Pattern de Comportement",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        pattern_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        pattern_info = ctk.CTkLabel(
            pattern_frame,
            text="Simule un comportement humain réaliste pour éviter la détection",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray70")
        )
        pattern_info.pack(anchor='w', padx=15, pady=(0, 10))
        
        # Boutons radio pour les patterns
        self.pattern_var = tk.StringVar()
        patterns = [
            (BehaviorPattern.OFFICE_WORKER, "👔 Travailleur de Bureau", "Envois pendant les heures de bureau"),
            (BehaviorPattern.CASUAL_USER, "😊 Utilisateur Occasionnel", "Délais longs et irréguliers"),
            (BehaviorPattern.BUSINESS_USER, "💼 Utilisateur Professionnel", "Envois réguliers et rapides"),
            (BehaviorPattern.STUDENT, "🎓 Étudiant", "Envois par rafales avec pauses"),
            (BehaviorPattern.EVENING_USER, "🌃 Utilisateur du Soir", "Principalement le soir"),
            (BehaviorPattern.WEEKEND_WARRIOR, "🏖️ Warrior du Weekend", "Surtout les weekends"),
            (BehaviorPattern.CUSTOM, "⚙️ Personnalisé", "Configuration manuelle")
        ]
        
        for pattern, title, description in patterns:
            radio_frame = ctk.CTkFrame(pattern_frame, fg_color="transparent")
            radio_frame.pack(fill='x', padx=15, pady=2)
            
            radio = ctk.CTkRadioButton(
                radio_frame,
                text=f"{title}",
                variable=self.pattern_var,
                value=pattern.value
            )
            radio.pack(side='left')
            
            desc_label = ctk.CTkLabel(
                radio_frame,
                text=f"- {description}",
                font=ctk.CTkFont(size=9),
                text_color=("gray50", "gray70")
            )
            desc_label.pack(side='left', padx=(10, 0))
        
        # Heures personnalisées
        custom_hours_frame = ctk.CTkFrame(tab)
        custom_hours_frame.pack(fill='x', padx=15, pady=10)
        
        ctk.CTkLabel(
            custom_hours_frame,
            text="🕐 Heures de Travail Personnalisées",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor='w', padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            custom_hours_frame,
            text="Format: heure_début-heure_fin, séparé par des virgules (ex: 8-12,14-18):",
            font=ctk.CTkFont(size=10)
        ).pack(anchor='w', padx=15, pady=2)
        
        custom_hours_entry = ctk.CTkEntry(
            custom_hours_frame,
            textvariable=self.custom_hours_text,
            placeholder_text="8-12,14-18,20-22"
        )
        custom_hours_entry.pack(fill='x', padx=15, pady=(0, 10))
    
    def create_advanced_tab(self):
        """Onglet des paramètres avancés"""
        tab = self.notebook.add("🔧 Avancé")
        
        # Protections avancées
        protections_frame = ctk.CTkFrame(tab)
        protections_frame.pack(fill='x', padx=15, pady=10)
        
        protections_label = ctk.CTkLabel(
            protections_frame,
            text="🛡️ Protections Avancées",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        protections_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        weekend_cb = ctk.CTkCheckBox(
            protections_frame,
            text="🏖️ Protection Weekend (pas d'envoi le weekend)",
            variable=self.enable_weekend_protection_var
        )
        weekend_cb.pack(anchor='w', padx=15, pady=5)
        
        risk_cb = ctk.CTkCheckBox(
            protections_frame,
            text="📊 Analyse de Risque (ajuste les délais selon l'usage)",
            variable=self.enable_risk_analysis_var
        )
        risk_cb.pack(anchor='w', padx=15, pady=5)
        
        multiday_cb = ctk.CTkCheckBox(
            protections_frame,
            text="📅 Distribution Multi-jours (étale les gros volumes)",
            variable=self.enable_multi_day_var
        )
        multiday_cb.pack(anchor='w', padx=15, pady=(5, 10))
        
        # Simulation et test
        test_frame = ctk.CTkFrame(tab)
        test_frame.pack(fill='x', padx=15, pady=10)
        
        test_label = ctk.CTkLabel(
            test_frame,
            text="🧪 Test et Simulation",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        test_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        test_buttons = ctk.CTkFrame(test_frame, fg_color="transparent")
        test_buttons.pack(fill='x', padx=15, pady=5)
        
        simulate_btn = ctk.CTkButton(
            test_buttons,
            text="🎯 Simuler 100 messages",
            command=self.simulate_sending,
            width=150,
            height=35
        )
        simulate_btn.pack(side='left', padx=(0, 10))
        
        preview_btn = ctk.CTkButton(
            test_buttons,
            text="👀 Aperçu des délais",
            command=self.preview_delays,
            width=150,
            height=35
        )
        preview_btn.pack(side='left')
        
        # Zone de résultat
        self.test_result = ctk.CTkTextbox(
            test_frame,
            height=120,
            font=ctk.CTkFont(size=10)
        )
        self.test_result.pack(fill='x', padx=15, pady=(5, 10))
        
        # Import/Export de configuration
        io_frame = ctk.CTkFrame(tab)
        io_frame.pack(fill='x', padx=15, pady=10)
        
        io_label = ctk.CTkLabel(
            io_frame,
            text="💾 Import/Export Configuration",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        io_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        io_buttons = ctk.CTkFrame(io_frame, fg_color="transparent")
        io_buttons.pack(fill='x', padx=15, pady=5)
        
        export_btn = ctk.CTkButton(
            io_buttons,
            text="💾 Exporter",
            command=self.export_config,
            width=120,
            height=35
        )
        export_btn.pack(side='left', padx=(0, 10))
        
        import_btn = ctk.CTkButton(
            io_buttons,
            text="📥 Importer",
            command=self.import_config,
            width=120,
            height=35
        )
        import_btn.pack(side='left')
        
        reset_btn = ctk.CTkButton(
            io_buttons,
            text="🔄 Reset",
            command=self.reset_to_defaults,
            width=120,
            height=35,
            fg_color=("orange", "darkorange")
        )
        reset_btn.pack(side='right', pady=(0, 10))
    
    def create_expert_tab(self):
        """Onglet mode expert avec configuration JSON directe"""
        tab = self.notebook.add("⚠️ Expert")
        
        # Avertissement
        warning_frame = ctk.CTkFrame(tab, fg_color=("red", "darkred"))
        warning_frame.pack(fill='x', padx=15, pady=10)
        
        warning_label = ctk.CTkLabel(
            warning_frame,
            text="⚠️ MODE EXPERT - CONFIGURATION DIRECTE ⚠️",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        warning_label.pack(pady=10)
        
        warning_text = ctk.CTkLabel(
            warning_frame,
            text="Modification directe de la configuration JSON.\n"
                 "Attention : une configuration incorrecte peut causer des dysfonctionnements.",
            font=ctk.CTkFont(size=10),
            text_color="white",
            wraplength=500
        )
        warning_text.pack(pady=(0, 10))
        
        # Éditeur JSON
        json_frame = ctk.CTkFrame(tab)
        json_frame.pack(fill='both', expand=True, padx=15, pady=10)
        
        json_label = ctk.CTkLabel(
            json_frame,
            text="📝 Configuration JSON",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        json_label.pack(anchor='w', padx=10, pady=(10, 5))
        
        self.json_editor = ctk.CTkTextbox(
            json_frame,
            font=ctk.CTkFont(family="Courier", size=11)
        )
        self.json_editor.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Boutons pour l'éditeur JSON
        json_buttons = ctk.CTkFrame(json_frame, fg_color="transparent")
        json_buttons.pack(fill='x', padx=10, pady=(0, 10))
        
        load_json_btn = ctk.CTkButton(
            json_buttons,
            text="🔄 Charger Config",
            command=self.load_json_config,
            width=120,
            height=30
        )
        load_json_btn.pack(side='left', padx=(0, 10))
        
        validate_json_btn = ctk.CTkButton(
            json_buttons,
            text="✅ Valider",
            command=self.validate_json_config,
            width=100,
            height=30
        )
        validate_json_btn.pack(side='left', padx=(0, 10))
        
        apply_json_btn = ctk.CTkButton(
            json_buttons,
            text="🔧 Appliquer",
            command=self.apply_json_config,
            width=100,
            height=30,
            fg_color=("red", "darkred")
        )
        apply_json_btn.pack(side='left')
    
    def create_action_buttons(self):
        """Crée les boutons d'action en bas du widget"""
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill='x', pady=10)
        
        # Boutons à gauche
        left_buttons = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        left_buttons.pack(side='left')
        
        preview_btn = ctk.CTkButton(
            left_buttons,
            text="👀 Aperçu",
            command=self.preview_configuration,
            width=100,
            height=35
        )
        preview_btn.pack(side='left', padx=(0, 10))
        
        test_btn = ctk.CTkButton(
            left_buttons,
            text="🧪 Tester",
            command=self.test_configuration,
            width=100,
            height=35
        )
        test_btn.pack(side='left')
        
        # Boutons à droite
        right_buttons = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        right_buttons.pack(side='right')
        
        self.save_btn = ctk.CTkButton(
            right_buttons,
            text="💾 Sauvegarder",
            command=self.save_configuration,
            width=120,
            height=35,
            fg_color=("green", "darkgreen")
        )
        self.save_btn.pack(side='right')
    
    def toggle_expert_mode(self):
        """Bascule le mode expert"""
        if self.expert_mode_var.get():
            # Désactiver toutes les protections
            self.enable_daily_limit_var.set(False)
            self.enable_hourly_limit_var.set(False)
            self.enable_delays_var.set(False)
            self.enable_working_hours_var.set(False)
            self.enable_weekend_protection_var.set(False)
            self.enable_risk_analysis_var.set(False)
            self.enable_multi_day_var.set(False)
            
            messagebox.showwarning(
                "Mode Expert Activé",
                "⚠️ ATTENTION !\n\n"
                "Le mode expert a été activé.\n"
                "TOUTES les protections anti-spam sont désactivées.\n\n"
                "Votre compte WhatsApp pourrait être détecté comme spam !"
            )
        else:
            # Réactiver les protections par défaut
            self.enable_daily_limit_var.set(True)
            self.enable_hourly_limit_var.set(True)
            self.enable_delays_var.set(True)
            self.enable_working_hours_var.set(True)
            
            messagebox.showinfo(
                "Mode Expert Désactivé",
                "✅ Mode expert désactivé.\n\n"
                "Les protections anti-spam par défaut ont été restaurées."
            )
        
        self.auto_save_config()
    
    def setup_auto_save(self):
        """Configure la sauvegarde automatique"""
        variables = [
            self.expert_mode_var, self.enable_daily_limit_var, self.daily_limit_var,
            self.enable_hourly_limit_var, self.hourly_limit_var,
            self.enable_delays_var, self.min_delay_var, self.max_delay_var,
            self.enable_working_hours_var, self.work_start_var, self.work_end_var,
            self.enable_weekend_protection_var, self.enable_risk_analysis_var,
            self.enable_multi_day_var, self.custom_delays_text, self.custom_hours_text
        ]
        
        for var in variables:
            var.trace_add('write', lambda *args: self.schedule_auto_save())
        
        self.pattern_var.trace_add('write', lambda *args: self.schedule_auto_save())
    
    def schedule_auto_save(self):
        """Programme la sauvegarde automatique avec délai"""
        if hasattr(self, '_auto_save_job'):
            self.after_cancel(self._auto_save_job)
        
        self._auto_save_job = self.after(1000, self.auto_save_config)  # 1 seconde de délai
    
    def auto_save_config(self):
        """Sauvegarde automatique de la configuration"""
        try:
            self.apply_ui_to_config()
            self.anti_spam_manager.save_config()
            
            if self.on_config_change:
                self.on_config_change()
                
        except Exception as e:
            logger.error("auto_save_config_error", error=str(e))
    
    def load_current_config(self):
        """Charge la configuration actuelle dans l'interface"""
        config = self.config
        
        # Mode expert
        self.expert_mode_var.set(config.expert_mode)
        
        # Limites
        self.enable_daily_limit_var.set(config.enable_daily_limit)
        self.daily_limit_var.set(config.daily_message_limit)
        self.enable_hourly_limit_var.set(config.enable_hourly_limit)
        self.hourly_limit_var.set(config.hourly_message_limit)
        
        # Délais
        self.enable_delays_var.set(config.enable_intelligent_delays)
        self.min_delay_var.set(config.min_message_delay)
        self.max_delay_var.set(config.max_message_delay)
        
        # Heures de travail
        self.enable_working_hours_var.set(config.respect_working_hours)
        self.work_start_var.set(config.working_hours_start)
        self.work_end_var.set(config.working_hours_end)
        
        # Mettre à jour les combobox
        if hasattr(self, 'start_combo'):
            self.start_combo.set(f"{config.working_hours_start:02d}h00")
        if hasattr(self, 'end_combo'):
            self.end_combo.set(f"{config.working_hours_end:02d}h00")
        
        # Pattern de comportement
        self.pattern_var.set(config.behavior_pattern)
        
        # Protections avancées
        self.enable_weekend_protection_var.set(config.enable_weekend_protection)
        self.enable_risk_analysis_var.set(config.enable_risk_analysis)
        self.enable_multi_day_var.set(config.enable_multi_day_distribution)
        
        # Configuration personnalisée
        if config.custom_delays:
            self.custom_delays_text.set(','.join(map(str, config.custom_delays)))
        
        if config.custom_working_hours:
            hours_text = ','.join(f"{start}-{end}" for start, end in config.custom_working_hours)
            self.custom_hours_text.set(hours_text)
        
        # Mettre à jour l'affichage du statut
        self.update_status_display()
    
    def apply_ui_to_config(self):
        """Applique les valeurs de l'interface à la configuration"""
        config = self.config
        
        # Mode expert
        config.expert_mode = self.expert_mode_var.get()
        
        # Limites
        config.enable_daily_limit = self.enable_daily_limit_var.get()
        config.daily_message_limit = self.daily_limit_var.get()
        config.enable_hourly_limit = self.enable_hourly_limit_var.get()
        config.hourly_message_limit = self.hourly_limit_var.get()
        
        # Délais
        config.enable_intelligent_delays = self.enable_delays_var.get()
        config.min_message_delay = self.min_delay_var.get()
        config.max_message_delay = self.max_delay_var.get()
        
        # Heures de travail
        config.respect_working_hours = self.enable_working_hours_var.get()
        config.working_hours_start = self.work_start_var.get()
        config.working_hours_end = self.work_end_var.get()
        
        # Pattern de comportement
        config.behavior_pattern = self.pattern_var.get()
        
        # Protections avancées
        config.enable_weekend_protection = self.enable_weekend_protection_var.get()
        config.enable_risk_analysis = self.enable_risk_analysis_var.get()
        config.enable_multi_day_distribution = self.enable_multi_day_var.get()
        
        # Configuration personnalisée
        custom_delays_text = self.custom_delays_text.get().strip()
        if custom_delays_text:
            try:
                config.custom_delays = [int(x.strip()) for x in custom_delays_text.split(',') if x.strip()]
            except ValueError:
                config.custom_delays = []
        
        custom_hours_text = self.custom_hours_text.get().strip()
        if custom_hours_text:
            try:
                hours = []
                for part in custom_hours_text.split(','):
                    if '-' in part:
                        start, end = part.split('-')
                        hours.append((int(start.strip()), int(end.strip())))
                config.custom_working_hours = hours
            except ValueError:
                config.custom_working_hours = []
    
    def update_status_display(self):
        """Met à jour l'affichage du statut"""
        try:
            status = self.anti_spam_manager.get_current_status()
            
            status_text = f"📊 État du Système Anti-Spam\n\n"
            
            if status['config_active']:
                status_text += "🛡️ Protections: ACTIVÉES\n"
            else:
                status_text += "⚠️ Protections: DÉSACTIVÉES (Mode Expert)\n"
            
            daily = status['daily_usage']
            status_text += f"📅 Usage quotidien: {daily['sent']}/{daily['limit']} ({daily['percentage']:.1f}%)\n"
            
            hourly = status['hourly_usage']
            status_text += f"⏰ Usage horaire: {hourly['sent']}/{hourly['limit']} ({hourly['percentage']:.1f}%)\n"
            
            status_text += f"🎯 Niveau de risque: {status['risk_level'].upper()}\n"
            status_text += f"🎭 Comportement: {status['behavior_pattern']}\n"
            status_text += f"🕐 Heures de travail: {status['working_hours']}\n"
            
            if status['risk_factors']:
                status_text += f"\n⚠️ Facteurs de risque:\n"
                for factor in status['risk_factors']:
                    status_text += f"  • {factor}\n"
            
            if status['next_safe_time']:
                next_time = status['next_safe_time']
                status_text += f"\n⏰ Prochain envoi sûr: {next_time}\n"
            
            self.status_text.delete('1.0', 'end')
            self.status_text.insert('1.0', status_text)
            
        except Exception as e:
            logger.error("status_display_error", error=str(e))
            self.status_text.delete('1.0', 'end')
            self.status_text.insert('1.0', f"❌ Erreur de statut: {str(e)}")
    
    def show_status(self):
        """Affiche le statut détaillé dans une fenêtre séparée"""
        status_window = ctk.CTkToplevel(self)
        status_window.title("📊 Statut Anti-Spam Détaillé")
        status_window.geometry("600x400")
        status_window.transient(self)
        
        # Centrer la fenêtre
        x = (status_window.winfo_screenwidth() // 2) - 300
        y = (status_window.winfo_screenheight() // 2) - 200
        status_window.geometry(f"600x400+{x}+{y}")
        
        # Contenu détaillé
        text_widget = ctk.CTkTextbox(status_window, font=ctk.CTkFont(size=11))
        text_widget.pack(fill='both', expand=True, padx=20, pady=20)
        
        try:
            status = self.anti_spam_manager.get_current_status()
            recommendations = self.anti_spam_manager.get_recommendations()
            
            detailed_status = f"📊 RAPPORT ANTI-SPAM DÉTAILLÉ\n"
            detailed_status += "=" * 50 + "\n\n"
            
            # Configuration actuelle
            detailed_status += "⚙️ CONFIGURATION ACTUELLE\n"
            detailed_status += f"• Mode Expert: {'✅ Activé' if not status['config_active'] else '❌ Désactivé'}\n"
            detailed_status += f"• Pattern: {status['behavior_pattern']}\n"
            detailed_status += f"• Heures de travail: {status['working_hours']}\n\n"
            
            # Usage actuel
            detailed_status += "📈 USAGE ACTUEL\n"
            daily = status['daily_usage']
            detailed_status += f"• Quotidien: {daily['sent']}/{daily['limit']} ({daily['percentage']:.1f}%)\n"
            hourly = status['hourly_usage']
            detailed_status += f"• Horaire: {hourly['sent']}/{hourly['limit']} ({hourly['percentage']:.1f}%)\n\n"
            
            # Niveau de risque
            detailed_status += f"🚨 NIVEAU DE RISQUE: {status['risk_level'].upper()}\n"
            if status['risk_factors']:
                detailed_status += "Facteurs identifiés:\n"
                for factor in status['risk_factors']:
                    detailed_status += f"  • {factor}\n"
            else:
                detailed_status += "Aucun facteur de risque détecté.\n"
            detailed_status += "\n"
            
            # Recommandations
            if 'suggestions' in recommendations:
                detailed_status += "💡 RECOMMANDATIONS\n"
                for suggestion in recommendations['suggestions']:
                    detailed_status += f"• {suggestion}\n"
            
            text_widget.insert('1.0', detailed_status)
            
        except Exception as e:
            text_widget.insert('1.0', f"❌ Erreur lors de la génération du rapport: {str(e)}")
    
    def simulate_sending(self):
        """Simule l'envoi de 100 messages pour tester la configuration"""
        self.apply_ui_to_config()
        
        simulation_results = []
        total_delay = 0
        messages_sent = 0
        
        try:
            for i in range(100):
                can_send, reason, delay = self.anti_spam_manager.can_send_message()
                
                if can_send:
                    messages_sent += 1
                    total_delay += delay
                    if i < 10:  # Montrer seulement les 10 premiers
                        simulation_results.append(f"Message {i+1}: ✅ Envoi autorisé (délai: {delay}s)")
                else:
                    if len(simulation_results) < 10:
                        simulation_results.append(f"Message {i+1}: ❌ Bloqué - {reason}")
                    break
            
            # Résumé
            avg_delay = total_delay / max(messages_sent, 1)
            total_time = total_delay / 60  # en minutes
            
            result_text = f"🧪 SIMULATION DE 100 MESSAGES\n\n"
            result_text += f"✅ Messages autorisés: {messages_sent}/100\n"
            result_text += f"⏱️ Délai moyen: {avg_delay:.1f} secondes\n"
            result_text += f"🕐 Temps total estimé: {total_time:.1f} minutes\n\n"
            result_text += "📝 Détails des 10 premiers:\n"
            result_text += "\n".join(simulation_results)
            
            self.test_result.delete('1.0', 'end')
            self.test_result.insert('1.0', result_text)
            
        except Exception as e:
            self.test_result.delete('1.0', 'end')
            self.test_result.insert('1.0', f"❌ Erreur de simulation: {str(e)}")
    
    def preview_delays(self):
        """Aperçu des délais qui seront appliqués"""
        self.apply_ui_to_config()
        
        try:
            delays = []
            for _ in range(20):
                delay = self.anti_spam_manager.calculate_intelligent_delay()
                delays.append(delay)
            
            min_delay = min(delays)
            max_delay = max(delays)
            avg_delay = sum(delays) / len(delays)
            
            result_text = f"👀 APERÇU DES DÉLAIS (20 échantillons)\n\n"
            result_text += f"⏱️ Minimum: {min_delay} secondes\n"
            result_text += f"⏱️ Maximum: {max_delay} secondes\n"
            result_text += f"⏱️ Moyenne: {avg_delay:.1f} secondes\n\n"
            result_text += f"📊 Échantillon des délais:\n"
            
            for i, delay in enumerate(delays[:10], 1):
                result_text += f"  {i:2d}. {delay:3d}s\n"
            
            if len(delays) > 10:
                result_text += f"  ... et {len(delays) - 10} autres\n"
            
            self.test_result.delete('1.0', 'end')
            self.test_result.insert('1.0', result_text)
            
        except Exception as e:
            self.test_result.delete('1.0', 'end')
            self.test_result.insert('1.0', f"❌ Erreur d'aperçu: {str(e)}")
    
    def export_config(self):
        """Exporte la configuration vers un fichier JSON"""
        try:
            self.apply_ui_to_config()
            
            filename = filedialog.asksaveasfilename(
                title="Exporter la configuration anti-spam",
                defaultextension=".json",
                filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
            )
            
            if filename:
                from dataclasses import asdict
                config_dict = asdict(self.config)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo(
                    "Export réussi",
                    f"Configuration exportée vers:\n{filename}"
                )
                
        except Exception as e:
            messagebox.showerror("Erreur d'export", f"Impossible d'exporter la configuration:\n{str(e)}")
    
    def import_config(self):
        """Importe une configuration depuis un fichier JSON"""
        try:
            filename = filedialog.askopenfilename(
                title="Importer une configuration anti-spam",
                filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    config_dict = json.load(f)
                
                # Créer une nouvelle configuration
                new_config = AntiSpamConfig(**config_dict)
                
                # Confirmer l'import
                confirm = messagebox.askyesno(
                    "Confirmer l'import",
                    "Cette action remplacera la configuration actuelle.\n\n"
                    "Voulez-vous continuer ?"
                )
                
                if confirm:
                    self.config = new_config
                    self.anti_spam_manager.config = new_config
                    self.load_current_config()
                    self.anti_spam_manager.save_config()
                    
                    messagebox.showinfo(
                        "Import réussi",
                        "Configuration importée et appliquée avec succès!"
                    )
                
        except Exception as e:
            messagebox.showerror("Erreur d'import", f"Impossible d'importer la configuration:\n{str(e)}")
    
    def reset_to_defaults(self):
        """Remet la configuration aux valeurs par défaut"""
        confirm = messagebox.askyesno(
            "Confirmer la remise à zéro",
            "Cette action remplacera toute la configuration actuelle\n"
            "par les valeurs par défaut.\n\n"
            "Voulez-vous continuer ?"
        )
        
        if confirm:
            self.config = AntiSpamConfig()  # Configuration par défaut
            self.anti_spam_manager.config = self.config
            self.load_current_config()
            self.anti_spam_manager.save_config()
            
            messagebox.showinfo(
                "Configuration réinitialisée",
                "La configuration a été remise aux valeurs par défaut."
            )
    
    def load_json_config(self):
        """Charge la configuration actuelle dans l'éditeur JSON"""
        try:
            self.apply_ui_to_config()
            from dataclasses import asdict
            config_dict = asdict(self.config)
            json_text = json.dumps(config_dict, indent=2, ensure_ascii=False)
            
            self.json_editor.delete('1.0', 'end')
            self.json_editor.insert('1.0', json_text)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger la configuration JSON:\n{str(e)}")
    
    def validate_json_config(self):
        """Valide la configuration JSON"""
        try:
            json_text = self.json_editor.get('1.0', 'end').strip()
            config_dict = json.loads(json_text)
            
            # Essayer de créer une configuration
            test_config = AntiSpamConfig(**config_dict)
            
            messagebox.showinfo(
                "Validation réussie",
                "✅ La configuration JSON est valide!"
            )
            
        except json.JSONDecodeError as e:
            messagebox.showerror(
                "Erreur JSON",
                f"Erreur de format JSON:\n{str(e)}"
            )
        except Exception as e:
            messagebox.showerror(
                "Erreur de validation",
                f"Configuration invalide:\n{str(e)}"
            )
    
    def apply_json_config(self):
        """Applique la configuration JSON"""
        try:
            json_text = self.json_editor.get('1.0', 'end').strip()
            config_dict = json.loads(json_text)
            
            # Créer et appliquer la nouvelle configuration
            new_config = AntiSpamConfig(**config_dict)
            
            confirm = messagebox.askyesno(
                "Confirmer l'application",
                "⚠️ Cette action appliquera la configuration JSON\n"
                "et remplacera tous les paramètres actuels.\n\n"
                "Voulez-vous continuer ?"
            )
            
            if confirm:
                self.config = new_config
                self.anti_spam_manager.config = new_config
                self.load_current_config()
                self.anti_spam_manager.save_config()
                
                messagebox.showinfo(
                    "Configuration appliquée",
                    "✅ La configuration JSON a été appliquée avec succès!"
                )
            
        except Exception as e:
            messagebox.showerror(
                "Erreur d'application",
                f"Impossible d'appliquer la configuration:\n{str(e)}"
            )
    
    def preview_configuration(self):
        """Affiche un aperçu de la configuration actuelle"""
        try:
            self.apply_ui_to_config()
            
            preview_window = ctk.CTkToplevel(self)
            preview_window.title("👀 Aperçu de la Configuration")
            preview_window.geometry("500x600")
            preview_window.transient(self)
            
            # Centrer
            x = (preview_window.winfo_screenwidth() // 2) - 250
            y = (preview_window.winfo_screenheight() // 2) - 300
            preview_window.geometry(f"500x600+{x}+{y}")
            
            text_widget = ctk.CTkTextbox(preview_window, font=ctk.CTkFont(size=11))
            text_widget.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Génération de l'aperçu
            preview_text = "👀 APERÇU DE LA CONFIGURATION\n"
            preview_text += "=" * 40 + "\n\n"
            
            config = self.config
            
            if config.expert_mode:
                preview_text += "⚠️ MODE EXPERT ACTIVÉ\n"
                preview_text += "Toutes les protections sont désactivées!\n\n"
            else:
                preview_text += "🛡️ PROTECTIONS ACTIVÉES\n\n"
                
                if config.enable_daily_limit:
                    preview_text += f"📅 Limite quotidienne: {config.daily_message_limit} messages/jour\n"
                else:
                    preview_text += "📅 Limite quotidienne: DÉSACTIVÉE\n"
                
                if config.enable_hourly_limit:
                    preview_text += f"⏰ Limite horaire: {config.hourly_message_limit} messages/heure\n"
                else:
                    preview_text += "⏰ Limite horaire: DÉSACTIVÉE\n"
                
                if config.enable_intelligent_delays:
                    preview_text += f"⏱️ Délais: {config.min_message_delay}s - {config.max_message_delay}s\n"
                else:
                    preview_text += "⏱️ Délais intelligents: DÉSACTIVÉS\n"
                
                if config.respect_working_hours:
                    preview_text += f"🕐 Heures de travail: {config.working_hours_start}h - {config.working_hours_end}h\n"
                else:
                    preview_text += "🕐 Heures de travail: IGNORÉES\n"
                
                preview_text += f"🎭 Comportement: {config.behavior_pattern}\n"
                preview_text += f"🏖️ Protection weekend: {'✅' if config.enable_weekend_protection else '❌'}\n"
                preview_text += f"📊 Analyse de risque: {'✅' if config.enable_risk_analysis else '❌'}\n"
                preview_text += f"📅 Distribution multi-jours: {'✅' if config.enable_multi_day_distribution else '❌'}\n"
            
            if config.custom_delays:
                preview_text += f"\n⚙️ Délais personnalisés: {config.custom_delays}\n"
            
            if config.custom_working_hours:
                preview_text += f"🕐 Heures personnalisées: {config.custom_working_hours}\n"
            
            # Estimation d'impact
            preview_text += "\n" + "=" * 40 + "\n"
            preview_text += "📊 ESTIMATION D'IMPACT\n\n"
            
            if config.expert_mode:
                preview_text += "⚠️ Aucune protection - Risque de détection élevé\n"
            else:
                # Calcul approximatif du débit
                avg_delay = (config.min_message_delay + config.max_message_delay) / 2
                messages_per_hour = 3600 / avg_delay
                
                preview_text += f"📈 Débit estimé: {messages_per_hour:.1f} messages/heure\n"
                preview_text += f"🕐 Temps pour 100 messages: {(100 * avg_delay) / 60:.1f} minutes\n"
                preview_text += f"🛡️ Niveau de protection: "
                
                protection_score = 0
                if config.enable_daily_limit: protection_score += 1
                if config.enable_hourly_limit: protection_score += 1
                if config.enable_intelligent_delays: protection_score += 2
                if config.respect_working_hours: protection_score += 1
                if config.enable_weekend_protection: protection_score += 1
                if config.enable_risk_analysis: protection_score += 1
                
                if protection_score >= 6:
                    preview_text += "🟢 ÉLEVÉ\n"
                elif protection_score >= 4:
                    preview_text += "🟡 MOYEN\n"
                elif protection_score >= 2:
                    preview_text += "🟠 FAIBLE\n"
                else:
                    preview_text += "🔴 TRÈS FAIBLE\n"
            
            text_widget.insert('1.0', preview_text)
            
        except Exception as e:
            messagebox.showerror("Erreur d'aperçu", f"Impossible de générer l'aperçu:\n{str(e)}")
    
    def test_configuration(self):
        """Teste la configuration actuelle"""
        try:
            self.apply_ui_to_config()
            
            # Test basique
            can_send, reason, delay = self.anti_spam_manager.can_send_message()
            
            test_window = ctk.CTkToplevel(self)
            test_window.title("🧪 Test de Configuration")
            test_window.geometry("400x300")
            test_window.transient(self)
            
            # Centrer
            x = (test_window.winfo_screenwidth() // 2) - 200
            y = (test_window.winfo_screenheight() // 2) - 150
            test_window.geometry(f"400x300+{x}+{y}")
            
            text_widget = ctk.CTkTextbox(test_window, font=ctk.CTkFont(size=11))
            text_widget.pack(fill='both', expand=True, padx=20, pady=20)
            
            test_result = "🧪 RÉSULTATS DU TEST\n"
            test_result += "=" * 30 + "\n\n"
            
            if can_send:
                test_result += "✅ AUTORISATION D'ENVOI\n"
                test_result += f"⏱️ Délai suggéré: {delay} secondes\n"
                test_result += f"📝 Raison: {reason}\n"
            else:
                test_result += "❌ ENVOI BLOQUÉ\n"
                test_result += f"📝 Raison: {reason}\n"
                test_result += f"⏱️ Attendre: {delay} secondes ({delay//60} minutes)\n"
            
            # Informations supplémentaires
            status = self.anti_spam_manager.get_current_status()
            test_result += f"\n📊 STATUT ACTUEL\n"
            test_result += f"🎯 Risque: {status['risk_level'].upper()}\n"
            
            daily = status['daily_usage']
            test_result += f"📅 Quotidien: {daily['sent']}/{daily['limit']}\n"
            
            hourly = status['hourly_usage']
            test_result += f"⏰ Horaire: {hourly['sent']}/{hourly['limit']}\n"
            
            if self.on_test_config:
                self.on_test_config(can_send, reason, delay)
            
            text_widget.insert('1.0', test_result)
            
        except Exception as e:
            messagebox.showerror("Erreur de test", f"Impossible de tester la configuration:\n{str(e)}")
    
    def save_configuration(self):
        """Sauvegarde la configuration"""
        try:
            self.apply_ui_to_config()
            self.anti_spam_manager.save_config()
            
            messagebox.showinfo(
                "Configuration sauvegardée",
                "✅ La configuration anti-spam a été sauvegardée avec succès!"
            )
            
            if self.on_config_change:
                self.on_config_change()
                
        except Exception as e:
            messagebox.showerror("Erreur de sauvegarde", f"Impossible de sauvegarder:\n{str(e)}")