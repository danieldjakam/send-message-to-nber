# -*- coding: utf-8 -*-
"""
Application Excel vers WhatsApp - Version avec barres de chargement avancées

Version 2.2 - Système de barres de chargement animées avec feedback temps réel
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
from tkinter import ttk
import tkinter as tk
import threading
import time
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import json
import hashlib
import os
from datetime import datetime

# Imports des modules personnalisés
from config.config_manager import ConfigManager
from api.whatsapp_client import WhatsAppClient, MessageResult
from api.bulk_sender import BulkSender
from utils.validators import PhoneValidator, DataValidator
from utils.logger import logger
from utils.exceptions import *
from utils.anti_spam_manager import AntiSpamManager, create_balanced_config
from ui.anti_spam_widget import AntiSpamConfigWidget, AntiSpamStatusWidget
from ui.components import (
    StatusIndicator, ProgressFrame, CollapsibleSection, 
    ValidatedEntry, DataTable, MessageComposer
)
from ui.bulk_send_dialog import BulkSendDialog
from ui.progress_widgets import DetailedProgressDialog, SimpleProgressOverlay

# Configuration globale
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ExcelWhatsAppApp:
    """Application principale avec système de barres de chargement avancées"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Excel vers WhatsApp Pro - Barres de Chargement Avancées")
        self.root.geometry("1200x900")
        self.root.minsize(800, 600)
        
        # Configuration et logger
        self.config_manager = ConfigManager()
        logger.info("app_started", version="2.2")
        
        # Variables principales
        self.df: Optional[pd.DataFrame] = None
        self.whatsapp_client: Optional[WhatsAppClient] = None
        self.bulk_sender: Optional[BulkSender] = None
        self.column_vars: Dict[str, tk.BooleanVar] = {}
        self.is_sending = False
        
        # Fonctionnalités historique
        self.sent_numbers_file = Path.home() / ".excel_whatsapp_sent_numbers.json"
        self.sent_numbers = self.load_sent_numbers()
        self.history_file = Path.home() / ".excel_whatsapp_history.json"
        self.history = self.load_history()
        
        # Système anti-spam
        self.anti_spam_manager = AntiSpamManager(create_balanced_config())
        
        # Variables UI
        self.selected_file = ctk.StringVar()
        self.instance_id = ctk.StringVar()
        self.token = ctk.StringVar()
        self.phone_column = ctk.StringVar()
        self.selected_image = ctk.StringVar()
        self.include_excel_data = tk.BooleanVar(value=True)
        
        # Tracer les changements pour la sauvegarde automatique
        self._setup_config_traces()
        
        # Interface utilisateur avec onglets
        self.create_tabbed_interface()
        
        # Charger la configuration sauvegardée
        self.load_config()
        
        # Gestionnaire de fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _setup_config_traces(self):
        """Configure les traces pour la sauvegarde automatique"""
        self.instance_id.trace_add('write', self.on_config_change)
        self.token.trace_add('write', self.on_config_change)
        self.phone_column.trace_add('write', self.on_config_change)
        self.selected_image.trace_add('write', self.on_config_change)
        self.include_excel_data.trace_add('write', self.on_config_change)
    
    def create_tabbed_interface(self):
        """Crée l'interface avec onglets : Envoi + Historique"""
        # Configuration du thème
        self.root.configure(fg_color=("#f0f0f0", "#212121"))
        
        # Titre principal avec version
        title_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        title_frame.pack(pady=20)
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="📊 Excel vers WhatsApp Pro", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack()
        
        version_label = ctk.CTkLabel(
            title_frame,
            text="Version 2.2 - Barres Avancées + Historique Anti-Doublons",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        version_label.pack()
        
        # Status global avec animation
        self.status_indicator = StatusIndicator(
            self.root,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_indicator.pack(pady=(0, 10))
        
        # Créer le système d'onglets
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Onglet Principal (Envoi de messages)
        self.main_tab = self.tabview.add("📤 Envoi")
        self.create_main_tab_content()
        
        # Onglet Historique
        self.history_tab = self.tabview.add("📋 Historique")
        self.create_history_tab_content()
        
        # Onglet Anti-Spam
        self.antispam_tab = self.tabview.add("🛡️ Anti-Spam")
        self.create_antispam_tab_content()
    
    def create_main_tab_content(self):
        """Crée le contenu de l'onglet principal"""
        # Section de sélection de fichier
        self.file_section = self._create_file_section()
        
        # Section de configuration API (repliable)
        self.api_section = self._create_api_section()
        
        # Barre de progression avancée intégrée
        self.progress_frame = ProgressFrame(self.main_tab)
        
        # Overlay de progression simple pour petits volumes
        self.simple_overlay = SimpleProgressOverlay(self.main_tab, corner_radius=10)
        
        # Widget de statut anti-spam
        self.antispam_status_widget = AntiSpamStatusWidget(self.main_tab, self.anti_spam_manager)
        self.antispam_status_widget.pack(fill='x', padx=30, pady=5)
        
        # Section des colonnes
        self.columns_section = self._create_columns_section()
        
        # Section d'affichage des données
        self.data_section = self._create_data_section()
    
    def create_history_tab_content(self):
        """Crée l'onglet historique avec filtrage et statistiques"""
        # Titre et boutons de contrôle
        header_frame = ctk.CTkFrame(self.history_tab, fg_color="transparent")
        header_frame.pack(fill='x', padx=20, pady=10)
        
        history_title = ctk.CTkLabel(
            header_frame, 
            text="📋 Historique des envois", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        history_title.pack(side='left')
        
        # Boutons de contrôle à droite
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side='right')
        
        refresh_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 Actualiser",
            command=self.refresh_history,
            height=30,
            width=100,
            font=ctk.CTkFont(size=10, weight="bold")
        )
        refresh_btn.pack(side='left', padx=(0, 10))
        
        clear_btn = ctk.CTkButton(
            controls_frame,
            text="🗑️ Vider",
            command=self.clear_history,
            height=30,
            width=80,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=("red", "darkred"),
            hover_color=("darkred", "red")
        )
        clear_btn.pack(side='left')
        
        # Filtres
        filter_frame = ctk.CTkFrame(self.history_tab, corner_radius=10)
        filter_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        filter_label = ctk.CTkLabel(filter_frame, text="🔍 Filtres:", font=ctk.CTkFont(size=12, weight="bold"))
        filter_label.pack(anchor='w', padx=10, pady=(10, 5))
        
        filter_controls = ctk.CTkFrame(filter_frame, fg_color="transparent")
        filter_controls.pack(fill='x', padx=10, pady=(0, 10))
        
        # Filtre par statut
        status_label = ctk.CTkLabel(filter_controls, text="Statut:", font=ctk.CTkFont(size=10))
        status_label.pack(side='left', padx=(0, 5))
        
        self.status_filter = ctk.CTkComboBox(
            filter_controls,
            values=["Tous", "Succès", "Échec"],
            command=self.filter_history,
            width=100,
            height=25,
            font=ctk.CTkFont(size=10)
        )
        self.status_filter.pack(side='left', padx=(0, 20))
        
        # Filtre par téléphone
        phone_label = ctk.CTkLabel(filter_controls, text="Téléphone:", font=ctk.CTkFont(size=10))
        phone_label.pack(side='left', padx=(0, 5))
        
        self.phone_filter = ctk.CTkEntry(
            filter_controls,
            placeholder_text="Filtrer par numéro...",
            width=150,
            height=25,
            font=ctk.CTkFont(size=10)
        )
        self.phone_filter.pack(side='left', padx=(0, 10))
        self.phone_filter.bind('<KeyRelease>', lambda e: self.filter_history())
        
        # Statistiques
        stats_frame = ctk.CTkFrame(self.history_tab, corner_radius=10)
        stats_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        stats_label = ctk.CTkLabel(stats_frame, text="📊 Statistiques:", font=ctk.CTkFont(size=12, weight="bold"))
        stats_label.pack(anchor='w', padx=10, pady=(10, 5))
        
        self.stats_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        self.stats_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Tableau d'historique
        history_table_frame = ctk.CTkFrame(self.history_tab, corner_radius=10)
        history_table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Style du tableau
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("History.Treeview", 
                       background="#2b2b2b",
                       foreground="white",
                       rowheight=25,
                       fieldbackground="#2b2b2b")
        style.configure("History.Treeview.Heading",
                       background="#1f538d",
                       foreground="white",
                       relief="flat")
        style.map("History.Treeview",
                 background=[('selected', '#144870')])
        
        # Colonnes du tableau
        columns = ("Date/Heure", "Fichier", "Téléphone", "Statut", "Type", "Erreur")
        
        self.history_tree = ttk.Treeview(
            history_table_frame, 
            columns=columns, 
            show='headings', 
            height=15,
            style="History.Treeview"
        )
        
        # Configuration des colonnes
        self.history_tree.heading("Date/Heure", text="Date/Heure")
        self.history_tree.heading("Fichier", text="Fichier")
        self.history_tree.heading("Téléphone", text="Téléphone")
        self.history_tree.heading("Statut", text="Statut")
        self.history_tree.heading("Type", text="Type")
        self.history_tree.heading("Erreur", text="Erreur")
        
        self.history_tree.column("Date/Heure", width=150, minwidth=140)
        self.history_tree.column("Fichier", width=200, minwidth=150)
        self.history_tree.column("Téléphone", width=120, minwidth=100)
        self.history_tree.column("Statut", width=80, minwidth=70)
        self.history_tree.column("Type", width=70, minwidth=60)
        self.history_tree.column("Erreur", width=200, minwidth=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(history_table_frame, orient="vertical", command=self.history_tree.yview)
        h_scrollbar = ttk.Scrollbar(history_table_frame, orient="horizontal", command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Placement des widgets
        self.history_tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        v_scrollbar.grid(row=0, column=1, sticky='ns', pady=10)
        h_scrollbar.grid(row=1, column=0, sticky='ew', padx=10)
        
        history_table_frame.grid_rowconfigure(0, weight=1)
        history_table_frame.grid_columnconfigure(0, weight=1)
        
        # Charger l'historique initial
        self.refresh_history()
    
    def create_antispam_tab_content(self):
        """Crée l'onglet de configuration anti-spam"""
        # Widget de configuration anti-spam
        self.antispam_config_widget = AntiSpamConfigWidget(
            self.antispam_tab, 
            self.anti_spam_manager,
            on_config_change=self.on_antispam_config_change
        )
        self.antispam_config_widget.pack(fill="both", expand=True, padx=10, pady=10)
    
    def on_antispam_config_change(self, new_config):
        """Callback appelé lors du changement de configuration anti-spam"""
        logger.info("antispam_config_updated", 
                   max_daily=new_config.max_messages_per_day,
                   max_hourly=new_config.max_messages_per_hour,
                   pattern=new_config.behavior_pattern.value)
    
    def create_widgets(self):
        """Crée l'interface utilisateur moderne avec barres de chargement"""
        # Configuration du thème
        self.root.configure(fg_color=("#f0f0f0", "#212121"))
        
        # Titre principal avec version
        title_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        title_frame.pack(pady=20)
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="📊 Excel vers WhatsApp Pro", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack()
        
        version_label = ctk.CTkLabel(
            title_frame,
            text="Version 2.2 - Barres de Chargement Animées & Feedback Temps Réel",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        version_label.pack()
        
        # Status global avec animation
        self.status_indicator = StatusIndicator(
            self.root,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_indicator.pack(pady=(0, 10))
        
        # Section de sélection de fichier
        self.file_section = self._create_file_section()
        
        # Section de configuration API (repliable)
        self.api_section = self._create_api_section()
        
        # Barre de progression avancée intégrée
        self.progress_frame = ProgressFrame(self.root)
        
        # Overlay de progression simple pour petits volumes
        self.simple_overlay = SimpleProgressOverlay(self.root, corner_radius=10)
        
        # Section des colonnes
        self.columns_section = self._create_columns_section()
        
        # Section d'affichage des données
        self.data_section = self._create_data_section()
    
    def _create_file_section(self) -> ctk.CTkFrame:
        """Crée la section de sélection de fichier"""
        file_frame = ctk.CTkFrame(self.main_tab, corner_radius=15)
        file_frame.pack(pady=10, padx=30, fill='x')
        
        file_label = ctk.CTkLabel(
            file_frame, 
            text="📁 Fichier Excel", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        file_label.pack(anchor='w', padx=20, pady=(15, 10))
        
        # Conteneur pour le champ et boutons
        input_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        input_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        self.file_entry = ValidatedEntry(
            input_frame,
            placeholder_text="Sélectionnez un fichier Excel (.xlsx, .xls)...",
            validator=DataValidator.validate_excel_file,
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.file_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        # Boutons
        buttons_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        buttons_frame.pack(side='right')
        
        browse_btn = ctk.CTkButton(
            buttons_frame, 
            text="📂 Parcourir", 
            command=self.browse_file,
            height=40,
            width=100,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        browse_btn.pack(side='left', padx=(0, 5))
        
        load_btn = ctk.CTkButton(
            buttons_frame, 
            text="📄 Charger", 
            command=self.load_file_with_progress,
            height=40,
            width=100,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        load_btn.pack(side='left')
        
        return file_frame
    
    def _create_api_section(self) -> CollapsibleSection:
        """Crée la section de configuration API"""
        api_section = CollapsibleSection(self.main_tab, "📱 Configuration UltraMsg API")
        api_section.pack(fill='x', padx=30, pady=10)
        
        content = api_section.get_content_frame()
        
        # Container principal
        main_container = ctk.CTkFrame(content, fg_color="transparent")
        main_container.pack(fill='x', padx=15, pady=10)
        
        # Ligne 1: Identifiants API
        creds_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        creds_frame.pack(fill='x', pady=(0, 15))
        
        # Instance ID
        left_frame = ctk.CTkFrame(creds_frame, fg_color="transparent")
        left_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        ctk.CTkLabel(left_frame, text="🔑 Instance ID:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor='w', pady=(0, 5))
        self.instance_entry = ValidatedEntry(
            left_frame,
            placeholder_text="Votre Instance ID UltraMsg...",
            validator=lambda x: (len(x.strip()) >= 5, "Instance ID requis"),
            height=35
        )
        self.instance_entry.pack(fill='x')
        
        # Token
        right_frame = ctk.CTkFrame(creds_frame, fg_color="transparent")
        right_frame.pack(side='right', fill='x', expand=True, padx=(10, 0))
        
        ctk.CTkLabel(right_frame, text="🔐 Token API:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor='w', pady=(0, 5))
        self.token_entry = ValidatedEntry(
            right_frame,
            placeholder_text="Votre Token API...",
            validator=lambda x: (len(x.strip()) >= 10, "Token trop court") if x.strip() else (True, ""),
            height=35
        )
        # Configurer l'entry pour masquer le token
        self.token_entry.entry.configure(show="*")
        self.token_entry.pack(fill='x')
        
        # Ligne 2: Configuration message
        message_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        message_frame.pack(fill='x', pady=(0, 15))
        
        # Colonne numéros
        phone_frame = ctk.CTkFrame(message_frame, fg_color="transparent")
        phone_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        ctk.CTkLabel(phone_frame, text="📞 Colonne numéros:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor='w', pady=(0, 5))
        self.phone_column_combo = ctk.CTkComboBox(
            phone_frame, 
            variable=self.phone_column,
            values=["Chargez un fichier Excel d'abord"], 
            height=35, 
            state="readonly"
        )
        self.phone_column_combo.pack(fill='x')
        
        # Message personnalisé
        msg_frame = ctk.CTkFrame(message_frame, fg_color="transparent")
        msg_frame.pack(side='right', fill='x', expand=True, padx=(10, 0))
        
        self.message_composer = MessageComposer(msg_frame)
        self.message_composer.pack(fill='both', expand=True)
        
        # Ligne 3: Image optionnelle
        image_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        image_frame.pack(fill='x', pady=(0, 15))
        
        ctk.CTkLabel(image_frame, text="🖼️ Image (optionnel):", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor='w', pady=(0, 5))
        
        image_input_frame = ctk.CTkFrame(image_frame, fg_color="transparent")
        image_input_frame.pack(fill='x')
        
        self.image_entry = ValidatedEntry(
            image_input_frame,
            placeholder_text="Sélectionner une image à joindre...",
            validator=DataValidator.validate_image_file,
            height=35
        )
        self.image_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_image_btn = ctk.CTkButton(
            image_input_frame, 
            text="📂 Image", 
            command=self.browse_image, 
            height=35, 
            width=80
        )
        browse_image_btn.pack(side='right')
        
        # Ligne 4: Options et contrôles
        control_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        control_frame.pack(fill='x')
        
        # Checkbox
        include_data_cb = ctk.CTkCheckBox(
            control_frame, 
            text="📊 Inclure données Excel", 
            variable=self.include_excel_data,
            font=ctk.CTkFont(size=11)
        )
        include_data_cb.pack(side='left')
        
        # Status de connexion
        self.api_status = StatusIndicator(
            control_frame,
            font=ctk.CTkFont(size=11)
        )
        self.api_status.pack(side='left', padx=(20, 0))
        
        # Boutons d'action
        action_buttons = ctk.CTkFrame(control_frame, fg_color="transparent")
        action_buttons.pack(side='right')
        
        test_btn = ctk.CTkButton(
            action_buttons, 
            text="🧪 Test API", 
            command=self.test_api_connection,
            height=35, 
            width=100,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        test_btn.pack(side='left', padx=(0, 10))
        
        self.send_btn = ctk.CTkButton(
            action_buttons, 
            text="🚀 Envoyer", 
            command=self.start_bulk_send_optimized,
            height=35, 
            width=100,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#1f538d", "#14375e")
        )
        self.send_btn.pack(side='left')
        
        return api_section
    
    def _create_columns_section(self) -> ctk.CTkFrame:
        """Crée la section de sélection des colonnes"""
        columns_frame = ctk.CTkFrame(self.main_tab, corner_radius=15)
        columns_frame.pack(fill='x', padx=30, pady=10)
        
        # Titre
        columns_label = ctk.CTkLabel(
            columns_frame, 
            text="📋 Sélection des colonnes", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        columns_label.pack(anchor='w', padx=20, pady=(15, 10))
        
        # Frame scrollable pour les checkboxes
        self.columns_scroll_frame = ctk.CTkScrollableFrame(
            columns_frame, 
            height=120,
            corner_radius=10
        )
        self.columns_scroll_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # Boutons d'action
        action_frame = ctk.CTkFrame(columns_frame, fg_color="transparent")
        action_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        buttons_left = ctk.CTkFrame(action_frame, fg_color="transparent")
        buttons_left.pack(side='left')
        
        select_all_btn = ctk.CTkButton(
            buttons_left, 
            text="✅ Tout", 
            command=self.select_all_columns,
            height=30,
            width=80,
            font=ctk.CTkFont(size=11)
        )
        select_all_btn.pack(side='left', padx=(0, 5))
        
        deselect_all_btn = ctk.CTkButton(
            buttons_left, 
            text="❌ Rien", 
            command=self.deselect_all_columns,
            height=30,
            width=80,
            font=ctk.CTkFont(size=11)
        )
        deselect_all_btn.pack(side='left', padx=(0, 5))
        
        show_data_btn = ctk.CTkButton(
            action_frame, 
            text="👁️ Aperçu des données", 
            command=self.show_selected_data,
            height=30,
            width=150,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        show_data_btn.pack(side='right')
        
        # Masquer par défaut
        columns_frame.pack_forget()
        return columns_frame
    
    def _create_data_section(self) -> ctk.CTkFrame:
        """Crée la section d'affichage des données"""
        data_frame = ctk.CTkFrame(self.main_tab, corner_radius=15)
        data_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        # Titre
        data_label = ctk.CTkLabel(
            data_frame, 
            text="📊 Aperçu des données", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        data_label.pack(anchor='w', padx=20, pady=(15, 10))
        
        # Table de données
        self.data_table = DataTable(data_frame)
        self.data_table.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        # Masquer par défaut
        data_frame.pack_forget()
        return data_frame
    
    def _sync_ui_with_variables(self):
        """Synchronise l'interface avec les variables"""
        if hasattr(self, 'file_entry'):
            current_file = self.file_entry.get()
            if current_file != self.selected_file.get():
                self.selected_file.set(current_file)
        
        if hasattr(self, 'instance_entry'):
            current_instance = self.instance_entry.get()
            if current_instance != self.instance_id.get():
                self.instance_id.set(current_instance)
        
        if hasattr(self, 'token_entry'):
            current_token = self.token_entry.get()
            if current_token != self.token.get():
                self.token.set(current_token)
        
        if hasattr(self, 'image_entry'):
            current_image = self.image_entry.get()
            if current_image != self.selected_image.get():
                self.selected_image.set(current_image)
    
    def browse_file(self):
        """Ouvre le dialogue de sélection de fichier Excel"""
        try:
            filename = filedialog.askopenfilename(
                title="Sélectionner un fichier Excel",
                filetypes=[
                    ("Fichiers Excel", "*.xlsx *.xls"), 
                    ("Excel 2007+", "*.xlsx"),
                    ("Excel 97-2003", "*.xls"),
                    ("Tous les fichiers", "*.*")
                ]
            )
            if filename:
                self.selected_file.set(filename)
                self.file_entry.set(filename)
                logger.info("file_selected", file_path=filename)
        except Exception as e:
            logger.error("file_browse_error", error=str(e))
            messagebox.showerror("Erreur", f"Erreur lors de la sélection: {str(e)}")
    
    def browse_image(self):
        """Ouvre le dialogue de sélection d'image"""
        try:
            filename = filedialog.askopenfilename(
                title="Sélectionner une image",
                filetypes=[
                    ("Images supportées", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                    ("JPEG", "*.jpg *.jpeg"),
                    ("PNG", "*.png"),
                    ("GIF", "*.gif"),
                    ("BMP", "*.bmp"),
                    ("WebP", "*.webp"),
                    ("Tous les fichiers", "*.*")
                ]
            )
            if filename:
                is_valid, message = DataValidator.validate_image_file(filename)
                if is_valid:
                    self.selected_image.set(filename)
                    self.image_entry.set(filename)
                    logger.info("image_selected", file_path=filename, size_info=message)
                else:
                    messagebox.showerror("Image invalide", message)
        except Exception as e:
            logger.error("image_browse_error", error=str(e))
            messagebox.showerror("Erreur", f"Erreur lors de la sélection: {str(e)}")
    
    def load_file_with_progress(self):
        """Charge un fichier Excel avec barre de progression animée"""
        self._sync_ui_with_variables()
        
        file_path = self.selected_file.get()
        if not file_path:
            self.status_indicator.set_status('error', 'Aucun fichier sélectionné')
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier Excel.")
            return
        
        # Afficher la progression
        self.simple_overlay.show("🔄 Chargement du fichier Excel...")
        
        # Charger dans un thread pour ne pas bloquer l'UI
        def load_thread():
            try:
                time.sleep(0.5)  # Simulation du temps de chargement
                self.simple_overlay.update(25, 100, "Validation du fichier...")
                
                is_valid, validation_message = DataValidator.validate_excel_file(file_path)
                if not is_valid:
                    self.root.after(0, lambda: self._handle_file_error(validation_message))
                    return
                
                self.simple_overlay.update(50, 100, "Lecture des données...")
                time.sleep(0.3)
                
                self.df = pd.read_excel(file_path)
                
                if self.df.empty:
                    self.root.after(0, lambda: self._handle_file_error("Le fichier Excel est vide"))
                    return
                
                self.simple_overlay.update(75, 100, "Analyse des colonnes...")
                time.sleep(0.2)
                
                # Finaliser dans le thread principal
                self.root.after(0, lambda: self._finalize_file_load(file_path))
                
            except Exception as e:
                self.root.after(0, lambda: self._handle_file_error(f"Erreur lors du chargement: {str(e)}"))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def _finalize_file_load(self, file_path: str):
        """Finalise le chargement du fichier dans le thread principal"""
        try:
            self.simple_overlay.update(100, 100, "✅ Chargement terminé!")
            time.sleep(0.5)
            self.simple_overlay.hide()
            
            self.create_column_checkboxes()
            self.update_phone_column_options()
            self.columns_section.pack(fill='x', padx=30, pady=10)
            
            logger.log_file_loaded(file_path, len(self.df), len(self.df.columns))
            self.status_indicator.set_status('success', f'Fichier chargé: {len(self.df)} lignes')
            
            # Afficher une alerte pour les gros volumes avec animations
            if len(self.df) > 5000:
                messagebox.showinfo(
                    "⚡ Gros Volume Détecté",
                    f"📊 {len(self.df)} lignes détectées\n\n"
                    f"🎨 Interface avec barres de chargement avancées:\n"
                    f"• Animations fluides en temps réel\n"
                    f"• Statistiques détaillées\n"
                    f"• Feedback visuel intelligent\n"
                    f"• Contrôles interactifs\n\n"
                    f"L'envoi bénéficiera de toutes les optimisations visuelles."
                )
            elif len(self.df) > 100:
                messagebox.showinfo(
                    "📈 Volume Moyen Détecté",
                    f"📊 {len(self.df)} lignes détectées\n\n"
                    f"🎯 Interface avec progression détaillée:\n"
                    f"• Barres de progression multiples\n"
                    f"• Statistiques temps réel\n"
                    f"• Journal d'activité animé\n\n"
                    f"Parfait pour un suivi détaillé de l'envoi."
                )
            else:
                messagebox.showinfo(
                    "✅ Fichier Chargé",
                    f"Chargement réussi !\n\n"
                    f"📊 {len(self.df)} lignes\n"
                    f"📋 {len(self.df.columns)} colonnes\n\n"
                    f"🚀 Envoi rapide avec progression simple."
                )
            
        except Exception as e:
            self._handle_file_error(f"Erreur lors de la finalisation: {str(e)}")
    
    def _handle_file_error(self, error_msg: str):
        """Gère les erreurs de chargement de fichier"""
        self.simple_overlay.hide()
        self.status_indicator.set_status('error', 'Erreur de chargement')
        logger.error("file_load_error", error=error_msg)
        messagebox.showerror("Erreur", error_msg)
    
    def load_file(self):
        """Méthode de fallback pour la compatibilité"""
        self.load_file_with_progress()
    
    def create_column_checkboxes(self):
        """Crée les checkboxes pour la sélection des colonnes"""
        for widget in self.columns_scroll_frame.winfo_children():
            widget.destroy()
        
        self.column_vars.clear()
        
        if self.df is None or self.df.empty:
            return
        
        container = ctk.CTkFrame(self.columns_scroll_frame, fg_color="transparent")
        container.pack(fill='x', padx=5, pady=5)
        
        num_display_cols = min(3, max(1, len(self.df.columns) // 10 + 1))
        display_frames = []
        
        for i in range(num_display_cols):
            frame = ctk.CTkFrame(container, fg_color="transparent")
            frame.pack(side='left', fill='both', expand=True, padx=2)
            display_frames.append(frame)
        
        for i, column in enumerate(self.df.columns):
            var = tk.BooleanVar(value=True)
            self.column_vars[column] = var
            
            frame_index = i % num_display_cols
            parent_frame = display_frames[frame_index]
            
            dtype_str = str(self.df[column].dtype)
            if dtype_str.startswith('object'):
                dtype_icon = "📝"
            elif 'int' in dtype_str or 'float' in dtype_str:
                dtype_icon = "🔢"
            elif 'date' in dtype_str.lower():
                dtype_icon = "📅"
            else:
                dtype_icon = "❓"
            
            checkbox_text = f"{dtype_icon} {column}"
            if len(checkbox_text) > 25:
                checkbox_text = checkbox_text[:22] + "..."
            
            cb = ctk.CTkCheckBox(
                parent_frame,
                text=checkbox_text,
                variable=var,
                font=ctk.CTkFont(size=10)
            )
            cb.pack(anchor='w', padx=5, pady=2)
        
        logger.info("columns_created", count=len(self.df.columns))
    
    def update_phone_column_options(self):
        """Met à jour les options de colonnes pour les numéros de téléphone"""
        if self.df is not None and not self.df.empty:
            columns = list(self.df.columns)
            self.phone_column_combo.configure(values=columns)
            
            auto_selected = False
            phone_keywords = ['phone', 'tel', 'mobile', 'numero', 'number', 'contact']
            
            for col in columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in phone_keywords):
                    self.phone_column_combo.set(col)
                    self.phone_column.set(col)
                    auto_selected = True
                    logger.info("auto_phone_column_selected", column=col)
                    break
            
            if not auto_selected and columns:
                self.phone_column_combo.set(columns[0])
                self.phone_column.set(columns[0])
        else:
            self.phone_column_combo.configure(values=["Aucune donnée disponible"])
            self.phone_column_combo.set("Aucune donnée disponible")
    
    def select_all_columns(self):
        for var in self.column_vars.values():
            var.set(True)
        logger.info("all_columns_selected")
    
    def deselect_all_columns(self):
        for var in self.column_vars.values():
            var.set(False)
        logger.info("all_columns_deselected")
    
    def show_selected_data(self):
        """Affiche les données des colonnes sélectionnées"""
        if self.df is None or self.df.empty:
            self.status_indicator.set_status('error', 'Aucune donnée chargée')
            messagebox.showerror("Erreur", "Veuillez d'abord charger un fichier Excel.")
            return
        
        selected_columns = [col for col, var in self.column_vars.items() if var.get()]
        
        if not selected_columns:
            self.status_indicator.set_status('warning', 'Aucune colonne sélectionnée')
            messagebox.showwarning("Attention", "Veuillez sélectionner au moins une colonne.")
            return
        
        try:
            self.display_data(selected_columns)
            logger.info("data_preview_shown", columns_count=len(selected_columns))
        except Exception as e:
            error_msg = f"Erreur lors de l'affichage: {str(e)}"
            self.status_indicator.set_status('error', 'Erreur d\'affichage')
            logger.error("data_display_error", error=str(e))
            messagebox.showerror("Erreur", error_msg)
    
    def display_data(self, columns: List[str]):
        """Affiche les données sélectionnées dans un tableau moderne"""
        self.data_section.pack(fill='both', expand=True, padx=30, pady=10)
        selected_data = self.df[columns]
        self.data_table.load_data(selected_data, columns, max_rows=1000)
        self.status_indicator.set_status('success', f'Aperçu: {len(columns)} colonnes')
    
    def test_api_connection(self):
        """Teste la connexion API avec validation complète"""
        try:
            self._sync_ui_with_variables()
            
            instance_id = self.instance_id.get().strip()
            token = self.token.get().strip()
            
            is_valid, validation_msg = DataValidator.validate_api_credentials(instance_id, token)
            if not is_valid:
                self.api_status.set_status('error', 'Identifiants invalides')
                messagebox.showerror("❌ Identifiants invalides", validation_msg)
                return
            
            if self.df is None or self.df.empty:
                self.api_status.set_status('warning', 'Aucune donnée')
                messagebox.showwarning("⚠️ Aucune donnée", "Veuillez d'abord charger un fichier Excel.")
                return
            
            phone_column_name = self.phone_column.get()
            if not phone_column_name or phone_column_name not in self.df.columns:
                self.api_status.set_status('warning', 'Colonne manquante')
                messagebox.showwarning("⚠️ Colonne manquante", "Veuillez sélectionner une colonne de numéros de téléphone.")
                return
            
            test_phone = None
            for _, row in self.df.iterrows():
                phone_raw = str(row[phone_column_name]).strip()
                if phone_raw and phone_raw.lower() not in ['nan', 'none', '']:
                    if PhoneValidator.is_valid_phone(phone_raw):
                        test_phone = phone_raw
                        break
            
            if not test_phone:
                self.api_status.set_status('error', 'Aucun numéro valide')
                messagebox.showerror("❌ Aucun numéro valide", "Aucun numéro de téléphone valide trouvé dans la colonne sélectionnée.")
                return
            
            self.api_status.set_status('info', 'Test en cours...')
            self.whatsapp_client = WhatsAppClient(instance_id, token)
            self.bulk_sender = BulkSender(self.whatsapp_client)
            
            success, message = self.whatsapp_client.test_connection(test_phone)
            
            if success:
                self.api_status.set_status('success', 'API fonctionnelle')
                messagebox.showinfo(
                    "✅ Test réussi !", 
                    f"L'API fonctionne parfaitement !\n\n"
                    f"📱 Numéro testé: {PhoneValidator.format_for_whatsapp(test_phone)}\n"
                    f"📨 Message envoyé avec succès\n\n"
                    f"🎨 Système de barres de chargement prêt pour l'envoi optimisé."
                )
            else:
                self.api_status.set_status('error', 'Test échoué')
                messagebox.showerror("❌ Test échoué", f"Le test a échoué:\n\n{message}")
        
        except Exception as e:
            error_msg = f"Erreur lors du test: {str(e)}"
            self.api_status.set_status('error', 'Erreur test')
            logger.error("api_test_error", error=str(e))
            messagebox.showerror("❌ Erreur", error_msg)
    
    def start_bulk_send_optimized(self):
        """Démarre l'envoi en masse avec système de barres de chargement intelligent"""
        if self.is_sending:
            messagebox.showwarning("⚠️ Envoi en cours", "Un envoi est déjà en cours. Veuillez patienter.")
            return
        
        try:
            self._sync_ui_with_variables()
            
            validation_errors = self._validate_bulk_send_data()
            if validation_errors:
                messagebox.showerror("❌ Données invalides", "\n".join(validation_errors))
                return
            
            messages_data = self._prepare_messages_data()
            if not messages_data:
                messagebox.showerror("❌ Aucune donnée", "Aucun message à envoyer après validation.")
                return
            
            if not self.bulk_sender:
                if not self.whatsapp_client:
                    self.whatsapp_client = WhatsAppClient(
                        self.instance_id.get().strip(),
                        self.token.get().strip(),
                        rate_limit=0.8
                    )
                self.bulk_sender = BulkSender(self.whatsapp_client)
            
            # Sélection intelligente de l'interface selon le volume
            total = len(messages_data)
            if total > 1000:
                # Gros volume - Interface dédiée avec contrôles avancés
                self._show_bulk_send_dialog(messages_data)
            elif total > 100:
                # Volume moyen - Progression détaillée avec statistiques
                self._start_detailed_bulk_send(messages_data)
            else:
                # Petit volume - Progression simple et rapide
                self._start_simple_bulk_send(messages_data)
        
        except Exception as e:
            error_msg = f"Erreur lors de la préparation: {str(e)}"
            logger.error("bulk_send_preparation_error", error=str(e))
            messagebox.showerror("❌ Erreur", error_msg)
    
    def _show_bulk_send_dialog(self, messages_data: List[tuple]):
        """Affiche le dialog d'envoi optimisé pour gros volumes"""
        try:
            dialog = BulkSendDialog(self.root, self.bulk_sender, messages_data)
            logger.info("bulk_send_dialog_opened", total_messages=len(messages_data))
            
        except Exception as e:
            error_msg = f"Erreur lors de l'ouverture du dialog: {str(e)}"
            logger.error("bulk_send_dialog_error", error=str(e))
            messagebox.showerror("❌ Erreur", error_msg)
    
    def _start_detailed_bulk_send(self, messages_data: List[tuple]):
        """Démarre un envoi avec progression détaillée pour volumes moyens"""
        if not self._confirm_bulk_send(len(messages_data)):
            return
        
        try:
            # Créer et afficher le dialog de progression détaillée
            self.detailed_progress = DetailedProgressDialog(
                self.root,
                f"Envoi en Masse - {len(messages_data)} messages"
            )
            
            # Démarrer l'envoi
            self.is_sending = True
            self.send_btn.configure(text="🔄 Envoi...", state="disabled")
            
            thread = threading.Thread(
                target=self._execute_detailed_bulk_send,
                args=(messages_data,),
                daemon=True
            )
            thread.start()
            
        except Exception as e:
            error_msg = f"Erreur lors de l'ouverture du dialog: {str(e)}"
            logger.error("detailed_progress_error", error=str(e))
            messagebox.showerror("❌ Erreur", error_msg)
    
    def _start_simple_bulk_send(self, messages_data: List[tuple]):
        """Démarre un envoi simple pour les petits volumes"""
        if not self._confirm_bulk_send(len(messages_data)):
            return
        
        self.is_sending = True
        self.send_btn.configure(text="🔄 Envoi...", state="disabled")
        
        thread = threading.Thread(
            target=self._execute_simple_bulk_send,
            args=(messages_data,),
            daemon=True
        )
        thread.start()
    
    def _execute_detailed_bulk_send(self, messages_data: List[tuple]):
        """Exécute un envoi avec progression détaillée"""
        try:
            file_path = self.selected_file.get()
            file_hash = self.get_file_hash(file_path) if file_path else None
            
            # Callbacks pour la progression détaillée
            def progress_callback(completed, total, status):
                self.root.after(0, lambda: self.detailed_progress.update_progress(
                    completed, total, status
                ))
            
            def status_callback(msg):
                self.root.after(0, lambda: self.detailed_progress.add_log(msg))
            
            # Exécuter l'envoi avec protection anti-spam personnalisée
            session = self._execute_bulk_send_with_antispam(
                messages_data,
                progress_callback,
                status_callback
            )
            
            # Traiter les résultats
            self.root.after(0, lambda: self._handle_detailed_bulk_send_results(session))
            
        except Exception as e:
            error_msg = f"Erreur lors de l'envoi: {str(e)}"
            logger.error("detailed_bulk_send_execution_error", error=str(e))
            self.root.after(0, lambda: self._handle_detailed_bulk_send_error(error_msg))
    
    def _execute_simple_bulk_send(self, messages_data: List[tuple]):
        """Exécute un envoi simple avec overlay de progression"""
        try:
            file_path = self.selected_file.get()
            file_hash = self.get_file_hash(file_path) if file_path else None
            
            # Utiliser la barre de progression intégrée
            self.root.after(0, lambda: self.progress_frame.show("Envoi des messages..."))
            
            def progress_callback(completed, total, status):
                self.root.after(0, lambda: self.progress_frame.update(
                    completed, total, status
                ))
            
            # Exécuter l'envoi avec protection anti-spam
            session = self._execute_bulk_send_with_antispam(
                messages_data,
                progress_callback,
                lambda msg: self.root.after(0, lambda: self.progress_frame.progress_label.configure(text=msg))
            )
            
            self.root.after(0, lambda: self._handle_simple_bulk_send_results(session))
            
        except Exception as e:
            error_msg = f"Erreur lors de l'envoi: {str(e)}"
            logger.error("simple_bulk_send_execution_error", error=str(e))
            self.root.after(0, lambda: self._handle_simple_bulk_send_error(error_msg))
    
    def _handle_detailed_bulk_send_results(self, session):
        """Traite les résultats de l'envoi détaillé"""
        try:
            self.is_sending = False
            self.send_btn.configure(text="🚀 Envoyer", state="normal")
            
            # Mettre à jour les statistiques finales dans le dialog
            stats = self.bulk_sender.get_session_stats(session)
            self.detailed_progress.set_success_count(session.successful)
            self.detailed_progress.set_error_count(session.failed)
            
            # Ajouter un log de fin
            if session.failed == 0:
                self.detailed_progress.add_log("✅ Envoi terminé avec succès !")
                self.status_indicator.set_status('success', f"Envoi terminé: {session.successful}/{session.total_messages}")
            else:
                self.detailed_progress.add_log(f"⚠️ Envoi terminé avec {session.failed} erreurs")
                self.status_indicator.set_status('warning', f"Envoi terminé avec erreurs: {session.successful}/{session.total_messages}")
            
            # Actualiser l'historique dans l'onglet
            self.refresh_history()
            
        except Exception as e:
            logger.error("detailed_bulk_send_results_error", error=str(e))
            self._handle_detailed_bulk_send_error(f"Erreur lors du traitement des résultats: {str(e)}")
    
    def _handle_detailed_bulk_send_error(self, error_msg: str):
        """Gère les erreurs d'envoi détaillé"""
        self.is_sending = False
        self.send_btn.configure(text="🚀 Envoyer", state="normal")
        self.status_indicator.set_status('error', 'Erreur d\'envoi')
        
        # Ajouter l'erreur au log du dialog
        if hasattr(self, 'detailed_progress'):
            self.detailed_progress.add_log(f"❌ Erreur: {error_msg}")
        
        messagebox.showerror("❌ Erreur d'envoi", error_msg)
    
    def _handle_simple_bulk_send_results(self, session):
        """Traite les résultats de l'envoi simple"""
        try:
            self.progress_frame.hide()
            self.is_sending = False
            self.send_btn.configure(text="🚀 Envoyer", state="normal")
            
            stats = self.bulk_sender.get_session_stats(session)
            self._show_simple_sending_report(stats)
            
            if session.failed == 0:
                self.status_indicator.set_status('success', f"Envoi terminé: {session.successful}/{session.total_messages}")
            else:
                self.status_indicator.set_status('warning', f"Envoi terminé avec erreurs: {session.successful}/{session.total_messages}")
            
            # Actualiser l'historique dans l'onglet
            self.refresh_history()
        
        except Exception as e:
            logger.error("simple_bulk_send_results_error", error=str(e))
            self._handle_simple_bulk_send_error(f"Erreur lors du traitement des résultats: {str(e)}")
    
    def _handle_simple_bulk_send_error(self, error_msg: str):
        """Gère les erreurs d'envoi simple"""
        self.progress_frame.hide()
        self.is_sending = False
        self.send_btn.configure(text="🚀 Envoyer", state="normal")
        self.status_indicator.set_status('error', 'Erreur d\'envoi')
        messagebox.showerror("❌ Erreur d'envoi", error_msg)
    
    def _show_simple_sending_report(self, stats: Dict):
        """Affiche le rapport d'envoi simple"""
        report_title = "📊 Rapport d'envoi"
        
        if stats['failed'] == 0:
            report_msg = (
                f"✅ Envoi terminé avec succès !\n\n"
                f"📊 Total envoyé: {stats['successful']} messages\n"
                f"🎯 Taux de réussite: {stats['success_rate']:.1f}%\n"
                f"🚀 Débit moyen: {stats.get('messages_per_second', 0):.1f} msg/sec"
            )
            messagebox.showinfo(report_title, report_msg)
        else:
            report_msg = (
                f"⚠️ Envoi terminé avec erreurs\n\n"
                f"✅ Réussis: {stats['successful']}\n"
                f"❌ Échecs: {stats['failed']}\n"
                f"📊 Total: {stats['total']}\n"
                f"🎯 Taux de réussite: {stats['success_rate']:.1f}%"
            )
            messagebox.showwarning(report_title, report_msg)
    
    def _validate_bulk_send_data(self) -> List[str]:
        """Valide toutes les données nécessaires pour l'envoi en masse"""
        errors = []
        
        instance_id = self.instance_id.get().strip()
        token = self.token.get().strip()
        is_valid, msg = DataValidator.validate_api_credentials(instance_id, token)
        if not is_valid:
            errors.append(f"API: {msg}")
        
        if self.df is None or self.df.empty:
            errors.append("Aucun fichier Excel chargé")
            return errors
        
        phone_column = self.phone_column.get()
        if not phone_column or phone_column not in self.df.columns:
            errors.append("Colonne de numéros de téléphone non sélectionnée")
        
        if self.include_excel_data.get():
            selected_columns = [col for col, var in self.column_vars.items() if var.get()]
            if not selected_columns:
                errors.append("Aucune colonne de données sélectionnée")
        
        image_path = self.selected_image.get()
        if image_path:
            is_valid, msg = DataValidator.validate_image_file(image_path)
            if not is_valid:
                errors.append(f"Image: {msg}")
        
        return errors
    
    def _prepare_messages_data(self) -> List[tuple]:
        """Prépare les données pour l'envoi en masse en évitant les doublons"""
        messages = []
        phone_column = self.phone_column.get()
        user_message = self.message_composer.get_message()
        image_path = self.selected_image.get() if self.selected_image.get() else None
        
        # Obtenir le hash du fichier pour la vérification des doublons
        file_path = self.selected_file.get()
        file_hash = self.get_file_hash(file_path) if file_path else None
        
        selected_columns = []
        if self.include_excel_data.get():
            selected_columns = [col for col, var in self.column_vars.items() if var.get()]
        
        skipped_count = 0
        
        for idx, row in self.df.iterrows():
            phone_raw = str(row[phone_column]).strip()
            
            if not phone_raw or phone_raw.lower() in ['nan', 'none', '']:
                continue
            
            if not PhoneValidator.is_valid_phone(phone_raw):
                logger.warning("invalid_phone_skipped", phone=phone_raw, row=idx)
                continue
            
            # Vérifier les doublons si on a un hash de fichier
            formatted_phone = PhoneValidator.format_for_whatsapp(phone_raw)
            if file_hash and self.is_number_sent(file_hash, formatted_phone):
                logger.info("duplicate_phone_skipped", phone=formatted_phone, file_hash=file_hash[:8])
                skipped_count += 1
                continue
            
            message = user_message
            if selected_columns:
                data_lines = []
                for col in selected_columns:
                    try:
                        # Assurer que col est bien une chaîne
                        col_name = str(col) if col is not None else "Unknown"
                        value = str(row[col]) if pd.notna(row[col]) else "N/A"
                        data_line = f"{col_name}: {value}"
                        data_lines.append(data_line)
                    except Exception as e:
                        logger.warning("data_line_creation_error", col=col, error=str(e))
                        continue
                
                if data_lines:
                    # Vérifier que tous les éléments sont des chaînes
                    data_lines = [str(line) for line in data_lines]
                    message += "\n\n📋 Données:\n" + "\n".join(data_lines)
            
            messages.append((formatted_phone, message, image_path))
        
        # Logger les informations sur les doublons
        if skipped_count > 0:
            logger.info("duplicates_filtered", skipped=skipped_count, total_messages=len(messages))
            self.status_indicator.set_status('info', f'Préparé: {len(messages)} messages ({skipped_count} doublons ignorés)')
        else:
            self.status_indicator.set_status('success', f'Préparé: {len(messages)} messages')
        
        return messages
    
    def _confirm_bulk_send(self, total_messages: int) -> bool:
        """Demande confirmation avant l'envoi en masse avec description des barres de chargement et vérifications anti-spam"""
        # Vérifications anti-spam
        can_proceed, reason, warnings = self.check_antispam_limits_before_bulk_send(total_messages)
        
        if not can_proceed:
            messagebox.showerror("🚨 Protection Anti-Spam", f"Envoi bloqué par la protection anti-spam:\n\n{reason}")
            return False
        
        # Préparer le message avec les avertissements anti-spam
        antispam_section = ""
        if warnings:
            antispam_section = f"\n🛡️ ALERTES ANTI-SPAM:\n" + "\n".join(warnings) + "\n"
        
        if total_messages > 1000:
            confirm_msg = (
                f"🚀 Envoi en Masse - GROS VOLUME\n\n"
                f"📊 Nombre de messages: {total_messages}\n"
                f"💬 Type: {'Image + Texte' if self.selected_image.get() else 'Texte uniquement'}\n"
                f"📋 Données incluses: {'Oui' if self.include_excel_data.get() else 'Non'}\n\n"
                f"🎨 Interface dédiée avec barres avancées:\n"
                f"• Barres de progression multiples animées\n"
                f"• Contrôles interactifs (Pause/Reprise)\n"
                f"• Statistiques temps réel\n"
                f"• Configuration des paramètres\n"
                f"• Historique complet avec anti-doublons\n"
                f"{antispam_section}"
                f"⚠️ Cette opération peut prendre plusieurs heures.\n"
                f"Êtes-vous sûr de vouloir continuer ?"
            )
        elif total_messages > 100:
            confirm_msg = (
                f"🚀 Envoi en Masse - VOLUME MOYEN\n\n"
                f"📊 Nombre de messages: {total_messages}\n"
                f"💬 Type: {'Image + Texte' if self.selected_image.get() else 'Texte uniquement'}\n"
                f"📋 Données incluses: {'Oui' if self.include_excel_data.get() else 'Non'}\n\n"
                f"📈 Interface avec progression détaillée:\n"
                f"• Barres de progression animées\n"
                f"• Statistiques temps réel (débit, ETA)\n"
                f"• Journal d'activité en direct\n"
                f"• Compteurs de succès/échecs\n"
                f"• Historique et prévention des doublons\n"
                f"{antispam_section}"
                f"Êtes-vous sûr de vouloir continuer ?"
            )
        else:
            confirm_msg = (
                f"🚀 Confirmation d'envoi\n\n"
                f"📊 Nombre de messages: {total_messages}\n"
                f"💬 Type: {'Image + Texte' if self.selected_image.get() else 'Texte uniquement'}\n"
                f"📋 Données incluses: {'Oui' if self.include_excel_data.get() else 'Non'}\n\n"
                f"⚡ Envoi rapide avec barre de progression animée\n"
                f"• Progression fluide temps réel\n"
                f"• Statistiques de débit\n"
                f"• Changement de couleur selon l'avancement\n"
                f"• Enregistrement dans l'historique\n"
                f"{antispam_section}"
                f"Êtes-vous sûr de vouloir continuer ?"
            )
        
        return messagebox.askyesno("Confirmation", confirm_msg)
    
    def save_config(self):
        """Sauvegarde la configuration de manière sécurisée"""
        try:
            config_data = {
                'instance_id': self.instance_id.get(),
                'token': self.token.get(),
                'phone_column': self.phone_column.get(),
                'selected_image': self.selected_image.get(),
                'include_excel_data': self.include_excel_data.get(),
                'api_visible': getattr(self.api_section, 'is_open', tk.BooleanVar()).get() if hasattr(self, 'api_section') else False
            }
            
            if hasattr(self, 'message_composer'):
                config_data['user_message'] = self.message_composer.get_message()
            
            self.config_manager.update(config_data)
            
        except Exception as e:
            logger.error("config_save_error", error=str(e))
    
    def load_config(self):
        """Charge la configuration sauvegardée"""
        try:
            config = self.config_manager.get_all()
            
            self.instance_id.set(config.get('instance_id', ''))
            self.token.set(config.get('token', ''))
            self.phone_column.set(config.get('phone_column', ''))
            self.selected_image.set(config.get('selected_image', ''))
            self.include_excel_data.set(config.get('include_excel_data', True))
            
            if hasattr(self, 'instance_entry'):
                self.instance_entry.set(config.get('instance_id', ''))
            
            if hasattr(self, 'token_entry'):
                self.token_entry.set(config.get('token', ''))
            
            if hasattr(self, 'image_entry'):
                self.image_entry.set(config.get('selected_image', ''))
            
            if hasattr(self, 'message_composer'):
                message = config.get('user_message', 'Bonjour,\n\nVoici les informations demandées.\n\nCordialement.')
                self.message_composer.set_message(message)
            
            api_visible = config.get('api_visible', False)
            if hasattr(self, 'api_section'):
                self.api_section.set_open(api_visible)
            
            logger.info("config_loaded")
            
        except Exception as e:
            logger.error("config_load_error", error=str(e))
    
    def on_config_change(self, *args):
        """Sauvegarde automatique lors des changements"""
        self.root.after_idle(self.save_config)
    
    def on_closing(self):
        """Gestionnaire de fermeture de l'application"""
        try:
            self.save_config()
            
            if self.is_sending:
                self.is_sending = False
            
            # Nettoyer les anciennes sessions
            if self.bulk_sender:
                self.bulk_sender.cleanup_old_sessions()
            
            logger.info("app_closed")
            
        except Exception as e:
            logger.error("app_closing_error", error=str(e))
        
        finally:
            self.root.destroy()
    
    # ============================================================================
    # MÉTHODES ANTI-SPAM INTELLIGENTES
    # ============================================================================
    
    def wait_with_antispam_protection(self, phone_number: str = "", update_callback=None):
        """
        Attendre avec protection anti-spam intelligente
        Returns: (can_proceed, reason)
        """
        try:
            # Vérifier si on peut envoyer
            can_send, reason, delay = self.anti_spam_manager.can_send_message()
            
            if not can_send:
                if update_callback:
                    update_callback(f"⏸️ Protection anti-spam: {reason}")
                
                # Attendre le délai recommandé avec mise à jour visuelle
                self._countdown_wait(delay, f"⏸️ Attente anti-spam: {reason}", update_callback)
                
                # Re-vérifier après l'attente
                can_send, reason, delay = self.anti_spam_manager.can_send_message()
                if not can_send:
                    return False, f"Toujours bloqué: {reason}"
            
            # Calculer le délai intelligent pour ce message
            smart_delay = self.anti_spam_manager.calculate_intelligent_delay()
            
            if update_callback:
                update_callback(f"⏱️ Délai intelligent: {smart_delay}s pour {phone_number}")
            
            # Attendre avec compte à rebours
            self._countdown_wait(smart_delay, f"⏱️ Délai anti-spam intelligent", update_callback)
            
            return True, "Envoi autorisé"
            
        except Exception as e:
            logger.error("antispam_wait_error", error=str(e), phone=phone_number)
            return True, f"Erreur anti-spam (continue): {str(e)}"
    
    def _countdown_wait(self, duration: int, base_message: str, update_callback=None):
        """Attendre avec compte à rebours visuel"""
        if duration <= 0:
            return
        
        for remaining in range(duration, 0, -1):
            if not self.is_sending:  # Arrêt si annulé
                break
                
            # Formater le temps restant
            minutes = remaining // 60
            seconds = remaining % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            
            # Mettre à jour le callback si fourni
            if update_callback:
                update_callback(f"{base_message} - {time_str}")
            
            # Attendre 1 seconde
            time.sleep(1)
    
    def record_message_result_with_antispam(self, phone: str, success: bool, delivered: bool = True, error: str = None):
        """Enregistre le résultat d'un message avec mise à jour anti-spam"""
        try:
            # Enregistrer dans l'historique normal
            file_path = self.selected_file.get()
            file_hash = self.get_file_hash(file_path) if file_path else None
            message_type = "image" if self.selected_image.get() else "text"
            status = "success" if success else "failed"
            
            self.add_to_history(file_path, file_hash, phone, status, message_type, error)
            
            if success and file_hash:
                self.add_sent_number(file_hash, phone)
            
            # Enregistrer dans le système anti-spam
            self.anti_spam_manager.record_message_sent(success, delivered)
            
            # Mettre à jour le widget de statut
            if hasattr(self, 'antispam_status_widget'):
                self.root.after(0, lambda: self.antispam_status_widget.update_status())
            
        except Exception as e:
            logger.error("antispam_record_error", error=str(e), phone=phone)
    
    def check_antispam_limits_before_bulk_send(self, message_count: int) -> Tuple[bool, str, List[str]]:
        """
        Vérifie les limites anti-spam avant un envoi en masse
        Returns: (can_proceed, reason, warnings)
        """
        warnings = []
        
        try:
            today_stats = self.anti_spam_manager.get_today_stats()
            config = self.anti_spam_manager.config
            risk_analysis = self.anti_spam_manager.get_risk_analysis()
            
            # Vérification limite quotidienne
            remaining_today = config.max_messages_per_day - today_stats.messages_sent
            if message_count > remaining_today:
                if remaining_today <= 0:
                    return False, f"Limite quotidienne atteinte ({config.max_messages_per_day})", warnings
                else:
                    warnings.append(f"⚠️ Seulement {remaining_today} messages restants aujourd'hui")
                    warnings.append(f"📊 {message_count - remaining_today} messages seront reportés demain")
            
            # Vérification niveau de risque
            risk_level = risk_analysis["risk_level"]
            if risk_level == "critical":
                return False, "🚨 Niveau de risque CRITIQUE - Envoi bloqué pour protection", warnings
            elif risk_level == "high":
                warnings.append("🟠 Niveau de risque ÉLEVÉ - Délais très longs appliqués")
            elif risk_level == "medium":
                warnings.append("🟡 Niveau de risque MOYEN - Délais renforcés")
            
            # Vérification heures de travail
            if not self.anti_spam_manager.is_within_working_hours():
                warnings.append("🕐 Hors heures de travail - Simulation comportement humain")
            
            # Estimation du temps total
            estimated_time = self._estimate_total_send_time_with_antispam(message_count)
            if estimated_time > 3600:  # Plus d'1 heure
                hours = estimated_time // 3600
                warnings.append(f"⏱️ Temps estimé: ~{hours}h (avec pauses anti-spam)")
            
            return True, "Vérifications anti-spam OK", warnings
            
        except Exception as e:
            logger.error("antispam_check_error", error=str(e))
            return True, f"Erreur vérification (continue): {str(e)}", warnings
    
    def _estimate_total_send_time_with_antispam(self, message_count: int) -> int:
        """Estime le temps total d'envoi avec protections anti-spam"""
        try:
            config = self.anti_spam_manager.config
            risk_level = self.anti_spam_manager.calculate_risk_level()
            
            # Délai moyen par message
            avg_delay = (config.min_delay_between_messages + config.max_delay_between_messages) // 2
            
            # Ajustements selon le risque
            if risk_level.value == "high":
                avg_delay *= 2
            elif risk_level.value == "medium":
                avg_delay *= 1.5
            
            # Pauses longues
            long_pauses = message_count // config.long_pause_after_count
            long_pause_time = long_pauses * (config.long_pause_min + config.long_pause_max) // 2
            
            # Temps de base pour les messages
            base_time = message_count * 5  # 5s par message
            
            return base_time + (avg_delay * message_count) + long_pause_time
            
        except Exception:
            return message_count * 60  # Fallback: 1 minute par message
    
    def _execute_bulk_send_with_antispam(self, messages_data: List[tuple], progress_callback, status_callback):
        """Exécute un envoi en masse avec protection anti-spam complète"""
        from dataclasses import dataclass
        
        @dataclass
        class BulkSession:
            total_messages: int = 0
            successful: int = 0
            failed: int = 0
            results: List = None
            
            def __post_init__(self):
                if self.results is None:
                    self.results = []
        
        session = BulkSession(total_messages=len(messages_data))
        
        try:
            for i, (phone, message, image_path) in enumerate(messages_data, 1):
                if not self.is_sending:  # Arrêt si annulé
                    break
                
                # Mise à jour du progrès
                if progress_callback:
                    progress_callback(i-1, len(messages_data), f"Préparation envoi à {phone}")
                
                # Protection anti-spam avec attente intelligente
                can_proceed, reason = self.wait_with_antispam_protection(
                    phone, 
                    lambda msg: status_callback(msg) if status_callback else None
                )
                
                if not can_proceed:
                    # Enregistrer l'échec
                    self.record_message_result_with_antispam(phone, False, False, reason)
                    session.failed += 1
                    continue
                
                # Mise à jour du progrès
                if progress_callback:
                    progress_callback(i-1, len(messages_data), f"Envoi à {phone}...")
                
                # Envoyer le message
                try:
                    if image_path and os.path.exists(image_path):
                        result = self.whatsapp_client.send_image_message(phone, image_path, message)
                    else:
                        result = self.whatsapp_client.send_text_message(phone, message)
                    
                    # Enregistrer le résultat
                    if result.success:
                        self.record_message_result_with_antispam(phone, True, True)
                        session.successful += 1
                        if status_callback:
                            status_callback(f"✅ Envoyé à {phone}")
                    else:
                        self.record_message_result_with_antispam(phone, False, False, result.error)
                        session.failed += 1
                        if status_callback:
                            status_callback(f"❌ Échec pour {phone}: {result.error}")
                    
                    session.results.append(result)
                    
                except Exception as e:
                    error_msg = f"Erreur envoi: {str(e)}"
                    self.record_message_result_with_antispam(phone, False, False, error_msg)
                    session.failed += 1
                    if status_callback:
                        status_callback(f"❌ Erreur pour {phone}: {error_msg}")
                
                # Vérifier les pauses longues recommandées
                should_pause, pause_duration = self.anti_spam_manager.should_take_long_pause()
                if should_pause and i < len(messages_data):  # Pas de pause après le dernier
                    self.anti_spam_manager.record_pause(pause_duration)
                    if status_callback:
                        status_callback(f"⏸️ Pause longue recommandée: {pause_duration//60}min")
                    self._countdown_wait(
                        pause_duration, 
                        "⏸️ Pause longue anti-spam",
                        lambda msg: status_callback(msg) if status_callback else None
                    )
                
                # Mise à jour finale du progrès
                if progress_callback:
                    progress_callback(i, len(messages_data), f"Complété: {session.successful} succès, {session.failed} échecs")
            
            return session
            
        except Exception as e:
            logger.error("bulk_send_antispam_error", error=str(e))
            raise e
    
    # ============================================================================
    # MÉTHODES DE GESTION DE L'HISTORIQUE ET DES DOUBLONS
    # ============================================================================
    
    def get_file_hash(self, file_path):
        """Générer un hash unique pour identifier un fichier Excel"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return file_hash
        except Exception:
            return None
    
    def load_sent_numbers(self):
        """Charger les numéros déjà traités depuis le fichier de sauvegarde"""
        try:
            if self.sent_numbers_file.exists():
                with open(self.sent_numbers_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception:
            return {}
    
    def save_sent_numbers(self):
        """Sauvegarder les numéros traités dans le fichier"""
        try:
            with open(self.sent_numbers_file, 'w', encoding='utf-8') as f:
                json.dump(self.sent_numbers, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error("sent_numbers_save_error", error=str(e))
    
    def add_sent_number(self, file_hash, phone_number):
        """Ajouter un numéro à la liste des traités pour un fichier donné"""
        if file_hash not in self.sent_numbers:
            self.sent_numbers[file_hash] = []
        if phone_number not in self.sent_numbers[file_hash]:
            self.sent_numbers[file_hash].append(phone_number)
            self.save_sent_numbers()
    
    def is_number_sent(self, file_hash, phone_number):
        """Vérifier si un numéro a déjà été traité pour un fichier donné"""
        return file_hash in self.sent_numbers and phone_number in self.sent_numbers[file_hash]
    
    def load_history(self):
        """Charger l'historique détaillé depuis le fichier"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception:
            return []
    
    def save_history(self):
        """Sauvegarder l'historique dans le fichier"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error("history_save_error", error=str(e))
    
    def add_to_history(self, file_path, file_hash, phone_number, status, message_type="text", error_msg=None):
        """Ajouter une entrée à l'historique"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "file_hash": file_hash,
            "phone_number": phone_number,
            "status": status,  # "success" ou "failed"
            "message_type": message_type,
            "error_message": error_msg
        }
        self.history.append(entry)
        self.save_history()
    
    def refresh_history(self):
        """Actualise l'affichage de l'historique"""
        # Vider le tableau
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Recharger l'historique depuis le fichier
        self.history = self.load_history()
        
        # Trier par date (plus récent en premier)
        sorted_history = sorted(self.history, key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Remplir le tableau
        for entry in sorted_history:
            timestamp = entry.get('timestamp', '')
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00') if 'Z' in timestamp else timestamp)
                formatted_date = dt.strftime("%d/%m/%Y %H:%M")
            except:
                formatted_date = timestamp[:16] if timestamp else 'N/A'
            
            file_name = Path(entry.get('file_path', '')).name if entry.get('file_path') else 'N/A'
            phone = entry.get('phone_number', 'N/A')
            status = "✅ Succès" if entry.get('status') == 'success' else "❌ Échec"
            message_type = entry.get('message_type', 'text').capitalize()
            error = entry.get('error_message', '') or ''
            
            if len(error) > 50:
                error = error[:47] + "..."
            
            self.history_tree.insert('', 'end', values=(
                formatted_date, file_name, phone, status, message_type, error
            ))
        
        # Mettre à jour les statistiques
        self.update_statistics()
    
    def update_statistics(self):
        """Met à jour les statistiques de l'historique"""
        # Vider les statistiques actuelles
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        if not self.history:
            stats_text = ctk.CTkLabel(
                self.stats_frame,
                text="Aucune donnée disponible",
                font=ctk.CTkFont(size=11)
            )
            stats_text.pack(side='left')
            return
        
        # Calculer les statistiques
        total = len(self.history)
        success = sum(1 for h in self.history if h.get('status') == 'success')
        failed = total - success
        
        # Types de messages
        text_messages = sum(1 for h in self.history if h.get('message_type') == 'text')
        image_messages = total - text_messages
        
        # Afficher les statistiques
        stats = [
            f"📊 Total: {total}",
            f"✅ Succès: {success}",
            f"❌ Échecs: {failed}",
            f"📝 Texte: {text_messages}",
            f"🖼️ Images: {image_messages}"
        ]
        
        if total > 0:
            success_rate = (success / total) * 100
            stats.append(f"🎯 Taux: {success_rate:.1f}%")
        
        for stat in stats:
            stat_label = ctk.CTkLabel(
                self.stats_frame,
                text=stat,
                font=ctk.CTkFont(size=11)
            )
            stat_label.pack(side='left', padx=(0, 20))
    
    def filter_history(self, *args):
        """Filtre l'historique selon les critères"""
        # Vider le tableau
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Obtenir les filtres
        status_filter = self.status_filter.get()
        phone_filter = self.phone_filter.get().lower()
        
        # Filtrer les données
        filtered_history = []
        for entry in self.history:
            # Filtre par statut
            if status_filter == "Succès" and entry.get('status') != 'success':
                continue
            if status_filter == "Échec" and entry.get('status') == 'success':
                continue
            
            # Filtre par téléphone
            if phone_filter and phone_filter not in entry.get('phone_number', '').lower():
                continue
            
            filtered_history.append(entry)
        
        # Trier par date (plus récent en premier)
        sorted_history = sorted(filtered_history, key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Remplir le tableau avec les données filtrées
        for entry in sorted_history:
            timestamp = entry.get('timestamp', '')
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00') if 'Z' in timestamp else timestamp)
                formatted_date = dt.strftime("%d/%m/%Y %H:%M")
            except:
                formatted_date = timestamp[:16] if timestamp else 'N/A'
            
            file_name = Path(entry.get('file_path', '')).name if entry.get('file_path') else 'N/A'
            phone = entry.get('phone_number', 'N/A')
            status = "✅ Succès" if entry.get('status') == 'success' else "❌ Échec"
            message_type = entry.get('message_type', 'text').capitalize()
            error = entry.get('error_message', '') or ''
            
            if len(error) > 50:
                error = error[:47] + "..."
            
            self.history_tree.insert('', 'end', values=(
                formatted_date, file_name, phone, status, message_type, error
            ))
    
    def clear_history(self):
        """Vide l'historique après confirmation"""
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir vider tout l'historique ?\nCette action est irréversible."):
            self.history = []
            self.save_history()
            self.refresh_history()
            messagebox.showinfo("Historique vidé", "L'historique a été vidé avec succès.")


def main():
    """Point d'entrée principal de l'application"""
    try:
        root = ctk.CTk()
        app = ExcelWhatsAppApp(root)
        
        logger.info("app_mainloop_started", version="2.2")
        root.mainloop()
        
    except Exception as e:
        logger.error("app_startup_error", error=str(e))
        try:
            messagebox.showerror(
                "Erreur de démarrage",
                f"Impossible de démarrer l'application:\n\n{str(e)}"
            )
        except:
            print(f"Erreur critique: {str(e)}")
    
    finally:
        logger.info("app_terminated")


if __name__ == "__main__":
    main()