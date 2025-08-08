# -*- coding: utf-8 -*-
"""
Application Excel vers WhatsApp - Version Complète avec Historique et Fonctionnalités Avancées

Combine toutes les fonctionnalités :
- Interface avec onglets (Envoi + Historique)
- Système de barres de chargement avancées
- Sauvegarde et prévention des doublons
- Limitation à 1000 messages avec pauses automatiques
- Historique détaillé avec filtrage
- Temporisation intelligente (1min après 10 messages)
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
from tkinter import ttk
import tkinter as tk
import requests
import json
import base64
import os
import hashlib
from pathlib import Path
from datetime import datetime
import threading
import time
from typing import Optional, List, Dict, Any

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ExcelWhatsAppCompleteApp:
    """Application complète avec toutes les fonctionnalités avancées"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Excel vers WhatsApp Pro - Version Complète")
        self.root.geometry("1400x1000")
        self.root.minsize(900, 700)
        
        # Variables principales
        self.df: Optional[pd.DataFrame] = None
        self.column_vars: Dict[str, tk.BooleanVar] = {}
        self.is_sending = False
        
        # Variables UI
        self.selected_file = ctk.StringVar()
        self.instance_id = ctk.StringVar()
        self.token = ctk.StringVar()
        self.phone_column = ctk.StringVar()
        self.selected_image = ctk.StringVar()
        self.include_excel_data = tk.BooleanVar(value=True)
        
        # Tracer les changements pour la sauvegarde automatique
        self.instance_id.trace_add('write', self.on_config_change)
        self.token.trace_add('write', self.on_config_change)
        self.phone_column.trace_add('write', self.on_config_change)
        self.selected_image.trace_add('write', self.on_config_change)
        self.include_excel_data.trace_add('write', self.on_config_change)
        
        # Fichiers de configuration et historique
        self.config_file = Path.home() / ".excel_whatsapp_config.json"
        self.sent_numbers_file = Path.home() / ".excel_whatsapp_sent_numbers.json"
        self.sent_numbers = self.load_sent_numbers()
        self.history_file = Path.home() / ".excel_whatsapp_history.json"
        self.history = self.load_history()
        
        # Interface avec onglets
        self.create_widgets()
        
        # Charger la configuration sauvegardée
        self.load_config()
        
        # Gestionnaire de fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Crée l'interface utilisateur avec onglets et fonctionnalités avancées"""
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
            text="Version Complète - Historique + Barres Avancées + Temporisation",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        version_label.pack()
        
        # Status global avec couleurs
        self.status_indicator = ctk.CTkLabel(
            self.root,
            text="⚪ Prêt à utiliser",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_indicator.pack(pady=(0, 10))
        
        # Créer le système d'onglets
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Onglet Principal (Envoi de messages)
        self.main_tab = self.tabview.add("📤 Envoi")
        self.create_main_tab()
        
        # Onglet Historique
        self.history_tab = self.tabview.add("📋 Historique")
        self.create_history_tab()
        
        # Overlay de progression
        self.progress_overlay = None
    
    def create_main_tab(self):
        """Crée l'onglet principal pour l'envoi de messages"""
        # Section de sélection de fichier
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
        
        self.file_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.selected_file,
            placeholder_text="Sélectionnez un fichier Excel (.xlsx, .xls)...",
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
        
        # Configuration API (collapsible)
        api_frame = ctk.CTkFrame(self.main_tab, corner_radius=15)
        api_frame.pack(fill='x', padx=30, pady=10)
        
        # Bouton pour masquer/afficher la configuration API
        self.api_visible = tk.BooleanVar(value=False)
        api_toggle_frame = ctk.CTkFrame(api_frame, fg_color="transparent")
        api_toggle_frame.pack(fill='x', padx=20, pady=(10, 5))
        
        self.api_toggle_btn = ctk.CTkButton(
            api_toggle_frame,
            text="📱 Configuration UltraMsg API  ▶",
            command=self.toggle_api_section,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("gray75", "gray25"),
            hover_color=("gray65", "gray35")
        )
        self.api_toggle_btn.pack(anchor='w')
        
        # Section de configuration UltraMsg API (collapsible)
        self.api_section = ctk.CTkFrame(api_frame, corner_radius=10)
        
        api_separator = ctk.CTkFrame(self.api_section, height=2, fg_color=("gray70", "gray30"))
        api_separator.pack(fill='x', padx=20, pady=(15, 10))
        
        # Container horizontal pour les champs API
        api_container = ctk.CTkFrame(self.api_section, fg_color="transparent")
        api_container.pack(fill='x', padx=20, pady=(0, 10))
        
        # Colonne gauche API
        api_left = ctk.CTkFrame(api_container, fg_color="transparent")
        api_left.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        # Instance ID
        instance_label = ctk.CTkLabel(api_left, text="🔑 Instance ID:", font=ctk.CTkFont(size=12, weight="bold"))
        instance_label.pack(anchor='w', pady=(0, 5))
        
        self.instance_entry = ctk.CTkEntry(api_left, textvariable=self.instance_id, placeholder_text="Votre Instance ID...", height=35)
        self.instance_entry.pack(fill='x', pady=(0, 10))
        
        # Token
        token_label = ctk.CTkLabel(api_left, text="🔐 Token:", font=ctk.CTkFont(size=12, weight="bold"))
        token_label.pack(anchor='w', pady=(0, 5))
        
        self.token_entry = ctk.CTkEntry(api_left, textvariable=self.token, placeholder_text="Votre Token API...", show="*", height=35)
        self.token_entry.pack(fill='x', pady=(0, 10))
        
        # Colonne droite API
        api_right = ctk.CTkFrame(api_container, fg_color="transparent")
        api_right.pack(side='right', fill='x', expand=True, padx=(10, 0))
        
        # Colonne des numéros de téléphone
        phone_label = ctk.CTkLabel(api_right, text="📞 Colonne des numéros:", font=ctk.CTkFont(size=12, weight="bold"))
        phone_label.pack(anchor='w', pady=(0, 5))
        
        self.phone_column_combo = ctk.CTkComboBox(api_right, variable=self.phone_column, values=["Chargez d'abord un fichier Excel"], height=35, state="readonly")
        self.phone_column_combo.pack(fill='x', pady=(0, 10))
        
        # Message personnalisé
        message_label = ctk.CTkLabel(api_right, text="✉️ Votre message:", font=ctk.CTkFont(size=12, weight="bold"))
        message_label.pack(anchor='w', pady=(0, 5))
        
        self.user_message = ctk.CTkTextbox(api_right, height=60, font=ctk.CTkFont(size=10))
        self.user_message.pack(fill='x', pady=(0, 10))
        self.user_message.insert("0.0", "Bonjour,\\n\\nJe vous envoie les données demandées.\\n\\nCordialement.")
        
        # Sauvegarder quand le message change
        self.user_message.bind('<KeyRelease>', lambda e: self.save_config())
        
        # Sélection d'image
        image_label = ctk.CTkLabel(api_right, text="🖼️ Image à envoyer (optionnel):", font=ctk.CTkFont(size=12, weight="bold"))
        image_label.pack(anchor='w', pady=(10, 5))
        
        image_select_frame = ctk.CTkFrame(api_right, fg_color="transparent")
        image_select_frame.pack(fill='x', pady=(0, 10))
        
        self.image_entry = ctk.CTkEntry(image_select_frame, textvariable=self.selected_image, placeholder_text="Chemin de l'image...", height=30, font=ctk.CTkFont(size=10))
        self.image_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        browse_image_btn = ctk.CTkButton(image_select_frame, text="📂", command=self.browse_image, height=30, width=30, font=ctk.CTkFont(size=10))
        browse_image_btn.pack(side='right')
        
        # Boutons et options (pleine largeur)
        api_bottom = ctk.CTkFrame(self.api_section, fg_color="transparent")
        api_bottom.pack(fill='x', padx=20, pady=(0, 15))
        
        # Checkbox et boutons sur la même ligne
        controls_frame = ctk.CTkFrame(api_bottom, fg_color="transparent")
        controls_frame.pack(fill='x')
        
        # Checkbox à gauche
        include_data_cb = ctk.CTkCheckBox(controls_frame, text="📊 Inclure les données Excel", variable=self.include_excel_data, font=ctk.CTkFont(size=10))
        include_data_cb.pack(side='left', padx=(0, 20))
        
        # Status de connexion
        self.connection_status = ctk.CTkLabel(controls_frame, text="⚪ Status: Non testé", font=ctk.CTkFont(size=11))
        self.connection_status.pack(side='left', padx=(0, 20))
        
        # Boutons à droite
        buttons_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        buttons_frame.pack(side='right')
        
        test_btn = ctk.CTkButton(buttons_frame, text="🧪 Tester", command=self.test_api_with_message, height=35, width=100, font=ctk.CTkFont(size=11, weight="bold"))
        test_btn.pack(side='left', padx=(0, 10))
        
        self.send_btn = ctk.CTkButton(buttons_frame, text="📨 Envoyer", command=self.start_bulk_send, height=35, width=100, font=ctk.CTkFont(size=11, weight="bold"))
        self.send_btn.pack(side='left')
        
        # Section des colonnes
        self.columns_frame = ctk.CTkFrame(self.main_tab, corner_radius=15)
        self.columns_frame.pack(fill='x', padx=30, pady=10)
        
        # Configuration de la section colonnes
        columns_label = ctk.CTkLabel(
            self.columns_frame, 
            text="📋 Sélectionner les colonnes à afficher:", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        columns_label.pack(anchor='w', padx=20, pady=(20, 10))
        
        # Frame avec scrollbar pour les colonnes
        self.columns_scroll_frame = ctk.CTkScrollableFrame(
            self.columns_frame, 
            height=120,
            corner_radius=10
        )
        self.columns_scroll_frame.pack(fill='x', padx=20, pady=10)
        
        # Boutons d'action
        action_frame = ctk.CTkFrame(self.columns_frame, fg_color="transparent")
        action_frame.pack(pady=15)
        
        select_all_btn = ctk.CTkButton(
            action_frame, 
            text="✅ Tout sélectionner", 
            command=self.select_all_columns,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        select_all_btn.pack(side='left', padx=10)
        
        deselect_all_btn = ctk.CTkButton(
            action_frame, 
            text="❌ Tout désélectionner", 
            command=self.deselect_all_columns,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        deselect_all_btn.pack(side='left', padx=10)
        
        show_data_btn = ctk.CTkButton(
            action_frame, 
            text="👁️ Afficher les données", 
            command=self.show_selected_data,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        show_data_btn.pack(side='left', padx=10)
        
        # Frame pour l'affichage des données
        self.data_frame = ctk.CTkFrame(self.main_tab, corner_radius=15)
        
        # Masquer les sections par défaut
        self.columns_frame.pack_forget()
        self.data_frame.pack_forget()
    
    def create_history_tab(self):
        """Crée l'onglet historique"""
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
    
    # ============================================================================
    # MÉTHODES UTILITAIRES
    # ============================================================================
    
    def set_status(self, status_type: str, message: str):
        """Met à jour le status global avec couleurs"""
        colors = {
            'success': '🟢',
            'warning': '🟡', 
            'error': '🔴',
            'info': '🔵',
            'default': '⚪'
        }
        icon = colors.get(status_type, colors['default'])
        self.status_indicator.configure(text=f"{icon} {message}")
    
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
            print(f"Erreur sauvegarde numéros traités: {str(e)}")
    
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
            print(f"Erreur sauvegarde historique: {str(e)}")
    
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
    
    def pause_with_countdown(self, base_message):
        """Effectuer une pause de 60 secondes avec compte à rebours visuel"""
        import time
        
        pause_duration = 60  # 1 minute en secondes
        
        for remaining in range(pause_duration, 0, -1):
            # Formater le temps restant
            minutes = remaining // 60
            seconds = remaining % 60
            time_str = f"{minutes:01d}:{seconds:02d}"
            
            # Mettre à jour le status avec le compte à rebours
            if hasattr(self, 'connection_status'):
                self.connection_status.configure(text=f"{base_message}{time_str}")
                self.root.update()
            
            # Attendre 1 seconde
            time.sleep(1)
    
    # ============================================================================
    # MÉTHODES DE L'INTERFACE PRINCIPALE
    # ============================================================================
    
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
        except Exception as e:
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
                # Validation basique de l'image
                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    if file_size > 5 * 1024 * 1024:  # 5MB
                        messagebox.showerror("Image trop volumineuse", f"L'image est trop volumineuse ({file_size / 1024 / 1024:.1f}MB). Maximum: 5MB")
                        return
                    
                    self.selected_image.set(filename)
                else:
                    messagebox.showerror("Fichier introuvable", "Le fichier sélectionné n'existe pas.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sélection: {str(e)}")
    
    def load_file_with_progress(self):
        """Charge un fichier Excel avec barre de progression animée"""
        file_path = self.selected_file.get()
        if not file_path:
            self.set_status('error', 'Aucun fichier sélectionné')
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier Excel.")
            return
        
        # Créer l'overlay de progression
        self.show_progress_overlay("🔄 Chargement du fichier Excel...")
        
        # Charger dans un thread pour ne pas bloquer l'UI
        def load_thread():
            try:
                time.sleep(0.5)  # Simulation du temps de chargement
                self.root.after(0, lambda: self.update_progress_overlay(25, 100, "Validation du fichier..."))
                
                if not os.path.exists(file_path):
                    self.root.after(0, lambda: self._handle_file_error("Le fichier n'existe pas"))
                    return
                
                self.root.after(0, lambda: self.update_progress_overlay(50, 100, "Lecture des données..."))
                time.sleep(0.3)
                
                self.df = pd.read_excel(file_path)
                
                if self.df.empty:
                    self.root.after(0, lambda: self._handle_file_error("Le fichier Excel est vide"))
                    return
                
                self.root.after(0, lambda: self.update_progress_overlay(75, 100, "Analyse des colonnes..."))
                time.sleep(0.2)
                
                # Finaliser dans le thread principal
                self.root.after(0, lambda: self._finalize_file_load(file_path))
                
            except Exception as e:
                self.root.after(0, lambda: self._handle_file_error(f"Erreur lors du chargement: {str(e)}"))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def _finalize_file_load(self, file_path: str):
        """Finalise le chargement du fichier dans le thread principal"""
        try:
            self.update_progress_overlay(100, 100, "✅ Chargement terminé!")
            time.sleep(0.5)
            self.hide_progress_overlay()
            
            self.create_column_checkboxes()
            self.update_phone_column_options()
            self.columns_frame.pack(fill='x', padx=30, pady=10)
            
            self.set_status('success', f'Fichier chargé: {len(self.df)} lignes')
            
            # Afficher une alerte selon le volume
            if len(self.df) > 1000:
                messagebox.showinfo(
                    "⚡ Gros Volume Détecté",
                    f"📊 {len(self.df)} lignes détectées\\n\\n"
                    f"🎨 Fonctionnalités activées:\\n"
                    f"• Limitation automatique à 1000 messages\\n"
                    f"• Pauses de 1min tous les 10 envois\\n"
                    f"• Historique détaillé avec filtres\\n"
                    f"• Prévention des doublons\\n\\n"
                    f"L'envoi sera optimisé automatiquement."
                )
            elif len(self.df) > 100:
                messagebox.showinfo(
                    "📈 Volume Moyen Détecté",
                    f"📊 {len(self.df)} lignes détectées\\n\\n"
                    f"🎯 Fonctionnalités activées:\\n"
                    f"• Pauses intelligentes tous les 10 envois\\n"
                    f"• Historique avec statistiques\\n"
                    f"• Prévention des doublons\\n\\n"
                    f"Parfait pour un suivi détaillé."
                )
            else:
                messagebox.showinfo(
                    "✅ Fichier Chargé",
                    f"Chargement réussi !\\n\\n"
                    f"📊 {len(self.df)} lignes\\n"
                    f"📋 {len(self.df.columns)} colonnes\\n\\n"
                    f"🚀 Envoi avec historique activé."
                )
            
        except Exception as e:
            self._handle_file_error(f"Erreur lors de la finalisation: {str(e)}")
    
    def _handle_file_error(self, error_msg: str):
        """Gère les erreurs de chargement de fichier"""
        self.hide_progress_overlay()
        self.set_status('error', 'Erreur de chargement')
        messagebox.showerror("Erreur", error_msg)
    
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
    
    def update_phone_column_options(self):
        """Met à jour les options de colonnes pour les numéros de téléphone"""
        if self.df is not None and not self.df.empty:
            columns = list(self.df.columns)
            self.phone_column_combo.configure(values=columns)
            
            # Auto-sélection intelligente
            auto_selected = False
            phone_keywords = ['phone', 'tel', 'mobile', 'numero', 'number', 'contact']
            
            for col in columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in phone_keywords):
                    self.phone_column_combo.set(col)
                    self.phone_column.set(col)
                    auto_selected = True
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
    
    def deselect_all_columns(self):
        for var in self.column_vars.values():
            var.set(False)
    
    def show_selected_data(self):
        """Affiche les données des colonnes sélectionnées"""
        if self.df is None or self.df.empty:
            self.set_status('error', 'Aucune donnée chargée')
            messagebox.showerror("Erreur", "Veuillez d'abord charger un fichier Excel.")
            return
        
        selected_columns = [col for col, var in self.column_vars.items() if var.get()]
        
        if not selected_columns:
            self.set_status('warning', 'Aucune colonne sélectionnée')
            messagebox.showwarning("Attention", "Veuillez sélectionner au moins une colonne.")
            return
        
        try:
            self.display_data(selected_columns)
        except Exception as e:
            self.set_status('error', 'Erreur d\'affichage')
            messagebox.showerror("Erreur", f"Erreur lors de l'affichage: {str(e)}")
    
    def display_data(self, columns: List[str]):
        """Affiche les données sélectionnées dans un tableau moderne"""
        # Nettoyer complètement la frame de données
        for widget in self.data_frame.winfo_children():
            widget.destroy()
        
        # Créer le label
        data_label = ctk.CTkLabel(
            self.data_frame, 
            text="📊 Données sélectionnées:", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        data_label.pack(anchor='w', padx=20, pady=(20, 10))
        
        # Frame pour le tableau avec style moderne
        tree_frame = ctk.CTkFrame(self.data_frame, corner_radius=10)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Treeview avec scrollbars dans un style sombre
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Data.Treeview", 
                       background="#2b2b2b",
                       foreground="white",
                       rowheight=25,
                       fieldbackground="#2b2b2b")
        style.configure("Data.Treeview.Heading",
                       background="#1f538d",
                       foreground="white",
                       relief="flat")
        style.map("Data.Treeview",
                 background=[('selected', '#144870')])
        
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12, style="Data.Treeview")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Configuration des colonnes
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, minwidth=100)
        
        # Ajout des données (limité aux 1000 premières lignes pour la performance)
        data_to_show = self.df[columns].head(1000)
        for _, row in data_to_show.iterrows():
            tree.insert('', 'end', values=list(row))
        
        # Placement des widgets
        tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        v_scrollbar.grid(row=0, column=1, sticky='ns', pady=10)
        h_scrollbar.grid(row=1, column=0, sticky='ew', padx=10)
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Info sur les données
        info_label = ctk.CTkLabel(
            self.data_frame,
            text=f"📈 Affichage de {len(data_to_show)} lignes sur {len(self.df)} (limité à 1000 pour la performance)",
            font=ctk.CTkFont(size=11)
        )
        info_label.pack(pady=(10, 20))
        
        # Afficher data_frame
        self.data_frame.pack(fill='both', expand=True, padx=30, pady=10)
        self.set_status('success', f'Aperçu: {len(columns)} colonnes')
    
    def toggle_api_section(self):
        """Basculer l'affichage de la section API"""
        if self.api_visible.get():
            self.api_section.pack_forget()
            self.api_toggle_btn.configure(text="📱 Configuration UltraMsg API  ▶")
            self.api_visible.set(False)
        else:
            self.api_section.pack(fill='x', padx=20, pady=(5, 15))
            self.api_toggle_btn.configure(text="📱 Configuration UltraMsg API  ▼")
            self.api_visible.set(True)
        
        self.save_config()
    
    def test_api_with_message(self):
        """Teste la connexion API avec validation complète"""
        if not self.instance_id.get() or not self.token.get():
            self.connection_status.configure(text="🔴 Identifiants manquants")
            messagebox.showerror("Erreur", "Veuillez remplir l'Instance ID et le Token.")
            return
        
        if self.df is None or not self.phone_column.get():
            self.connection_status.configure(text="🔴 Données manquantes")
            messagebox.showerror("Erreur", "Veuillez charger un fichier Excel et sélectionner une colonne de numéros.")
            return
        
        # Prendre le premier numéro valide de la colonne pour le test
        phone_column_name = self.phone_column.get()
        if phone_column_name not in self.df.columns:
            messagebox.showerror("Erreur", "La colonne sélectionnée n'existe pas.")
            return
        
        test_phone = None
        for _, row in self.df.iterrows():
            phone_raw = str(row[phone_column_name]).strip()
            if phone_raw and phone_raw.lower() not in ['nan', 'none', '']:
                # Validation basique du numéro
                if len(phone_raw.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) >= 8:
                    test_phone = phone_raw
                    break
        
        if not test_phone:
            self.connection_status.configure(text="🔴 Aucun numéro valide")
            messagebox.showerror("Erreur", "Aucun numéro de téléphone valide trouvé dans la colonne sélectionnée.")
            return
        
        try:
            self.connection_status.configure(text="🔵 Test en cours...")
            
            # Message de test
            test_message = "🧪 Test API UltraMsg - Si vous recevez ce message, votre API fonctionne parfaitement !"
            
            # Tester avec image si sélectionnée, sinon message texte
            if self.selected_image.get() and os.path.exists(self.selected_image.get()):
                success = self.send_image_message(test_phone, test_message)
                if success:
                    self.connection_status.configure(text="🟢 API fonctionnelle ✅")
                    messagebox.showinfo("✅ Test réussi !", 
                                      f"Image test envoyée avec succès !\\n"
                                      f"Vérifiez WhatsApp sur {test_phone}")
                else:
                    self.connection_status.configure(text="🔴 Échec envoi image")
                    messagebox.showerror("❌ Test échoué", "Échec d'envoi de l'image")
                return
            
            # Envoyer le message texte de test
            url = f"https://api.ultramsg.com/{self.instance_id.get()}/messages/chat"
            
            payload = {
                'token': self.token.get(),
                'to': test_phone,
                'body': test_message
            }
            
            response = requests.post(url, data=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('sent'):
                    self.connection_status.configure(text="🟢 API fonctionnelle ✅")
                    messagebox.showinfo("✅ Test réussi !", 
                                      f"L'API fonctionne parfaitement !\\n\\n"
                                      f"📱 Numéro testé: {test_phone}\\n"
                                      f"📨 Message envoyé avec succès\\n\\n"
                                      f"🎨 Système d'historique et de pauses prêt.")
                else:
                    self.connection_status.configure(text="🔴 Test échoué")
                    error_msg = result.get('message', 'Erreur inconnue')
                    messagebox.showerror("❌ Test échoué", f"Le test a échoué:\\n\\n{error_msg}")
            else:
                self.connection_status.configure(text="🔴 Erreur API")
                messagebox.showerror("❌ Test échoué", f"Erreur API: {response.status_code}\\n{response.text}")
                
        except requests.exceptions.RequestException as e:
            self.connection_status.configure(text="🔴 Erreur connexion")
            messagebox.showerror("❌ Test échoué", f"Erreur de connexion: {str(e)}")
        except Exception as e:
            self.connection_status.configure(text="🔴 Erreur test")
            messagebox.showerror("❌ Erreur", f"Erreur lors du test: {str(e)}")
    
    # ============================================================================
    # ENVOI EN MASSE AVEC FONCTIONNALITÉS COMPLÈTES
    # ============================================================================
    
    def start_bulk_send(self):
        """Démarre l'envoi en masse avec toutes les fonctionnalités"""
        if self.is_sending:
            messagebox.showwarning("⚠️ Envoi en cours", "Un envoi est déjà en cours. Veuillez patienter.")
            return
        
        # Validation des données
        validation_errors = self._validate_bulk_send_data()
        if validation_errors:
            messagebox.showerror("❌ Données invalides", "\\n".join(validation_errors))
            return
        
        # Préparer les messages
        messages_data = self._prepare_messages_data()
        if not messages_data:
            messagebox.showerror("❌ Aucune donnée", "Aucun message à envoyer après validation.")
            return
        
        # Confirmation avec description des fonctionnalités
        if not self._confirm_bulk_send_complete(len(messages_data)):
            return
        
        # Lancer l'envoi
        self.is_sending = True
        self.send_btn.configure(text="🔄 Envoi...", state="disabled")
        
        thread = threading.Thread(
            target=self._execute_complete_bulk_send,
            args=(messages_data,),
            daemon=True
        )
        thread.start()
    
    def _validate_bulk_send_data(self) -> List[str]:
        """Valide toutes les données nécessaires pour l'envoi en masse"""
        errors = []
        
        # API
        if not self.instance_id.get().strip() or not self.token.get().strip():
            errors.append("API: Instance ID et Token requis")
        
        # Fichier Excel
        if self.df is None or self.df.empty:
            errors.append("Aucun fichier Excel chargé")
            return errors
        
        # Colonne téléphone
        phone_column = self.phone_column.get()
        if not phone_column or phone_column not in self.df.columns:
            errors.append("Colonne de numéros de téléphone non sélectionnée")
        
        # Colonnes de données
        if self.include_excel_data.get():
            selected_columns = [col for col, var in self.column_vars.items() if var.get()]
            if not selected_columns:
                errors.append("Aucune colonne de données sélectionnée")
        
        # Image
        image_path = self.selected_image.get()
        if image_path:
            if not os.path.exists(image_path):
                errors.append("Image: Fichier introuvable")
            else:
                file_size = os.path.getsize(image_path)
                if file_size > 5 * 1024 * 1024:
                    errors.append(f"Image: Trop volumineuse ({file_size / 1024 / 1024:.1f}MB > 5MB)")
        
        return errors
    
    def _prepare_messages_data(self) -> List[tuple]:
        """Prépare les données pour l'envoi en masse"""
        messages = []
        phone_column = self.phone_column.get()
        user_message = self.user_message.get("0.0", "end-1c").strip()
        image_path = self.selected_image.get() if self.selected_image.get() else None
        
        selected_columns = []
        if self.include_excel_data.get():
            selected_columns = [col for col, var in self.column_vars.items() if var.get()]
        
        for idx, row in self.df.iterrows():
            phone_raw = str(row[phone_column]).strip()
            
            # Ignorer les numéros vides
            if not phone_raw or phone_raw.lower() in ['nan', 'none', '']:
                continue
            
            # Validation basique du numéro
            cleaned_phone = phone_raw.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if len(cleaned_phone) < 8:
                continue
            
            # Construire le message
            message = user_message
            if selected_columns:
                data_lines = []
                for col in selected_columns:
                    try:
                        col_name = str(col) if col is not None else "Unknown"
                        value = str(row[col]) if pd.notna(row[col]) else "N/A"
                        data_line = f"{col_name}: {value}"
                        data_lines.append(data_line)
                    except Exception:
                        continue
                
                if data_lines:
                    message += "\\n\\n📋 Données:\\n" + "\\n".join(data_lines)
            
            messages.append((phone_raw, message, image_path))
        
        return messages
    
    def _confirm_bulk_send_complete(self, total_messages: int) -> bool:
        """Demande confirmation avec description complète des fonctionnalités"""
        max_messages = 1000
        will_be_limited = total_messages > max_messages
        
        confirm_msg = (
            f"🚀 Envoi en Masse - FONCTIONNALITÉS COMPLÈTES\\n\\n"
            f"📊 Messages à envoyer: {min(total_messages, max_messages)}"
            f"{f' (sur {total_messages} - limité à 1000)' if will_be_limited else ''}\\n"
            f"💬 Type: {'Image + Texte' if self.selected_image.get() else 'Texte uniquement'}\\n"
            f"📋 Données incluses: {'Oui' if self.include_excel_data.get() else 'Non'}\\n\\n"
            f"🎨 FONCTIONNALITÉS ACTIVÉES:\\n"
            f"• ⏸️ Pauses automatiques (1min après 10 messages)\\n"
            f"• 🚫 Prévention des doublons (hash du fichier)\\n"
            f"• 📋 Historique détaillé avec horodatage\\n"
            f"• 📊 Filtrage et statistiques temps réel\\n"
            f"• 🔄 Sauvegarde automatique de la progression\\n"
            f"• 🎯 Limitation intelligente à 1000 messages\\n\\n"
        )
        
        if will_be_limited:
            confirm_msg += (
                f"⚠️ LIMITATION ACTIVE:\\n"
                f"Seuls les 1000 premiers messages seront envoyés.\\n"
                f"Les {total_messages - max_messages} restants seront reportés.\\n\\n"
            )
        
        if total_messages > 100:
            confirm_msg += (
                f"⏱️ DURÉE ESTIMÉE:\\n"
                f"~{self._estimate_duration(min(total_messages, max_messages))} minutes\\n"
                f"(incluant pauses automatiques)\\n\\n"
            )
        
        confirm_msg += "Êtes-vous sûr de vouloir continuer ?"
        
        return messagebox.askyesno("Confirmation", confirm_msg)
    
    def _estimate_duration(self, message_count: int) -> int:
        """Estime la durée d'envoi en minutes"""
        # 1 seconde par message + 1 minute de pause tous les 10 messages
        base_time = message_count  # secondes
        pauses = max(0, (message_count - 1) // 10)
        pause_time = pauses * 60  # secondes
        total_seconds = base_time + pause_time
        return max(1, total_seconds // 60)
    
    def _execute_complete_bulk_send(self, messages_data: List[tuple]):
        """Exécute l'envoi complet avec toutes les fonctionnalités"""
        try:
            file_path = self.selected_file.get()
            file_hash = self.get_file_hash(file_path) if file_path else None
            
            # Filtrer les doublons
            numbers_to_send = []
            skipped_numbers = []
            
            for phone, message, image_path in messages_data:
                if file_hash and self.is_number_sent(file_hash, phone):
                    skipped_numbers.append(phone)
                else:
                    numbers_to_send.append((phone, message, image_path))
            
            # Limitation à 1000 messages
            max_messages = 1000
            if len(numbers_to_send) > max_messages:
                numbers_to_send = numbers_to_send[:max_messages]
            
            if not numbers_to_send:
                self.root.after(0, lambda: self._handle_no_messages_to_send(len(skipped_numbers)))
                return
            
            # Afficher la progression
            self.root.after(0, lambda: self.show_progress_overlay("🚀 Début de l'envoi..."))
            
            # Variables de suivi
            sent_count = 0
            failed_count = 0
            failed_numbers = []
            total_numbers = len(numbers_to_send)
            
            for i, (phone_number, message, image_path) in enumerate(numbers_to_send, 1):
                try:
                    # Mise à jour du status
                    self.root.after(0, lambda i=i: self.update_progress_overlay(
                        i, total_numbers, f"Envoi à {phone_number}..."
                    ))
                    
                    # Envoyer le message
                    if image_path and os.path.exists(image_path):
                        success = self.send_image_message(phone_number, message)
                        msg_type = "image"
                    else:
                        success = self.send_text_message(phone_number, message)
                        msg_type = "text"
                    
                    if success:
                        sent_count += 1
                        if file_hash:
                            self.add_sent_number(file_hash, phone_number)
                        # Ajouter à l'historique
                        self.add_to_history(file_path, file_hash, phone_number, "success", msg_type)
                    else:
                        failed_count += 1
                        error_msg = "Erreur d'envoi"
                        failed_numbers.append(f"{phone_number}: {error_msg}")
                        # Ajouter à l'historique
                        self.add_to_history(file_path, file_hash, phone_number, "failed", msg_type, error_msg)
                    
                    # Pause de sécurité entre chaque envoi
                    time.sleep(1)
                    
                    # Pause de 1 minute après chaque groupe de 10 messages
                    if i % 10 == 0 and i < total_numbers:
                        self.root.after(0, lambda i=i: self.connection_status.configure(
                            text=f"⏸️ Pause après {i} messages..."
                        ))
                        self.pause_with_countdown("⏸️ Reprend dans: ")
                        
                        # Mettre à jour le status après la pause
                        self.root.after(0, lambda i=i: self.connection_status.configure(
                            text=f"📤 Reprise: {i}/{total_numbers}"
                        ))
                    
                except Exception as e:
                    failed_count += 1
                    error_msg = str(e)
                    failed_numbers.append(f"{phone_number}: {error_msg}")
                    # Ajouter à l'historique
                    self.add_to_history(file_path, file_hash, phone_number, "failed", "text", error_msg)
            
            # Traiter les résultats
            self.root.after(0, lambda: self._handle_complete_bulk_send_results(
                sent_count, failed_count, failed_numbers, len(skipped_numbers)
            ))
            
        except Exception as e:
            self.root.after(0, lambda: self._handle_complete_bulk_send_error(str(e)))
    
    def send_text_message(self, phone_number: str, message: str) -> bool:
        """Envoie un message texte"""
        try:
            url = f"https://api.ultramsg.com/{self.instance_id.get()}/messages/chat"
            payload = {
                'token': self.token.get(),
                'to': phone_number,
                'body': message
            }
            
            response = requests.post(url, data=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('sent', False)
            return False
            
        except Exception:
            return False
    
    def send_image_message(self, phone_number: str, caption: str = "") -> bool:
        """Envoie une image via WhatsApp avec une légende optionnelle"""
        try:
            image_path = self.selected_image.get()
            
            if not os.path.exists(image_path):
                return False
            
            # Vérifier la taille du fichier (limite 5MB)
            file_size = os.path.getsize(image_path)
            if file_size > 5 * 1024 * 1024:
                return False
            
            # Encoder l'image en base64
            with open(image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Déterminer le type MIME
            file_extension = os.path.splitext(image_path)[1].lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(file_extension, 'image/jpeg')
            
            # Vérifier que l'encodage base64 n'est pas trop long
            if len(image_base64) > 7000000:
                return False
            
            # Limiter la longueur du caption
            max_caption_length = 1020
            if len(caption) > max_caption_length:
                truncated_caption = caption[:max_caption_length-3] + "..."
            else:
                truncated_caption = caption
            
            # Préparer l'URL et les données
            url = f"https://api.ultramsg.com/{self.instance_id.get()}/messages/image"
            
            payload = {
                'token': self.token.get(),
                'to': phone_number,
                'image': f"data:{mime_type};base64,{image_base64}",
                'caption': truncated_caption if truncated_caption else ""
            }
            
            # Envoyer l'image
            response = requests.post(url, data=payload, timeout=90)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    return result.get('sent', False)
                except ValueError:
                    return False
            else:
                return False
                
        except Exception:
            return False
    
    def _handle_no_messages_to_send(self, skipped_count: int):
        """Gère le cas où aucun message n'est à envoyer"""
        self.hide_progress_overlay()
        self.is_sending = False
        self.send_btn.configure(text="📨 Envoyer", state="normal")
        
        if skipped_count > 0:
            messagebox.showinfo(
                "Aucun envoi nécessaire",
                f"Tous les numéros ont déjà été traités avec ce fichier.\\n\\n"
                f"📊 Total ignoré: {skipped_count} numéros\\n"
                f"🔄 Utilisez un nouveau fichier pour envoyer à nouveau."
            )
        else:
            messagebox.showinfo(
                "Aucune donnée",
                "Aucun numéro valide trouvé pour l'envoi."
            )
    
    def _handle_complete_bulk_send_results(self, sent_count: int, failed_count: int, failed_numbers: List[str], skipped_count: int):
        """Traite les résultats de l'envoi complet"""
        self.hide_progress_overlay()
        self.is_sending = False
        self.send_btn.configure(text="📨 Envoyer", state="normal")
        
        # Actualiser l'historique
        self.refresh_history()
        
        # Préparer le rapport
        total_processed = sent_count + failed_count
        success_rate = (sent_count / total_processed * 100) if total_processed > 0 else 0
        
        report = (
            f"📊 RAPPORT D'ENVOI COMPLET\\n\\n"
            f"✅ Envoyés avec succès: {sent_count}\\n"
            f"❌ Échecs: {failed_count}\\n"
            f"⏭️ Ignorés (déjà traités): {skipped_count}\\n"
            f"📊 Total traité: {total_processed}\\n"
            f"🎯 Taux de réussite: {success_rate:.1f}%\\n\\n"
            f"🎨 FONCTIONNALITÉS UTILISÉES:\\n"
            f"• Pauses automatiques tous les 10 messages\\n"
            f"• Sauvegarde anti-doublons activée\\n"
            f"• Historique détaillé mis à jour\\n"
        )
        
        if failed_numbers:
            report += f"\\n❌ Premiers échecs:\\n"
            for failure in failed_numbers[:3]:
                report += f"• {failure}\\n"
            if len(failed_numbers) > 3:
                report += f"... et {len(failed_numbers) - 3} autres échecs\\n"
        
        # Mettre à jour le status global
        if failed_count == 0:
            self.set_status('success', f"Envoi terminé: {sent_count}/{total_processed}")
            messagebox.showinfo("🎉 Envoi réussi !", report)
        else:
            self.set_status('warning', f"Envoi terminé: {sent_count}/{total_processed}")
            messagebox.showwarning("⚠️ Envoi terminé avec erreurs", report)
    
    def _handle_complete_bulk_send_error(self, error_msg: str):
        """Gère les erreurs d'envoi complet"""
        self.hide_progress_overlay()
        self.is_sending = False
        self.send_btn.configure(text="📨 Envoyer", state="normal")
        self.set_status('error', 'Erreur d\'envoi')
        messagebox.showerror("❌ Erreur d'envoi", f"Erreur lors de l'envoi:\\n\\n{error_msg}")
    
    # ============================================================================
    # MÉTHODES DE L'HISTORIQUE
    # ============================================================================
    
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
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir vider tout l'historique ?\\nCette action est irréversible."):
            self.history = []
            self.save_history()
            self.refresh_history()
            messagebox.showinfo("Historique vidé", "L'historique a été vidé avec succès.")
    
    # ============================================================================
    # OVERLAY DE PROGRESSION
    # ============================================================================
    
    def show_progress_overlay(self, message: str):
        """Affiche l'overlay de progression"""
        if self.progress_overlay:
            self.progress_overlay.destroy()
        
        # Créer l'overlay
        self.progress_overlay = ctk.CTkToplevel(self.root)
        self.progress_overlay.title("Progression")
        self.progress_overlay.geometry("400x200")
        self.progress_overlay.transient(self.root)
        self.progress_overlay.grab_set()
        
        # Centrer l'overlay
        self.progress_overlay.update_idletasks()
        x = (self.progress_overlay.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.progress_overlay.winfo_screenheight() // 2) - (200 // 2)
        self.progress_overlay.geometry(f"400x200+{x}+{y}")
        
        # Contenu de l'overlay
        main_frame = ctk.CTkFrame(self.progress_overlay, corner_radius=15)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Message
        self.progress_message = ctk.CTkLabel(
            main_frame,
            text=message,
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=350
        )
        self.progress_message.pack(pady=20)
        
        # Barre de progression
        self.progress_bar = ctk.CTkProgressBar(main_frame, width=300, height=20)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        
        # Label de pourcentage
        self.progress_label = ctk.CTkLabel(
            main_frame,
            text="0%",
            font=ctk.CTkFont(size=12)
        )
        self.progress_label.pack(pady=5)
    
    def update_progress_overlay(self, current: int, total: int, message: str = ""):
        """Met à jour l'overlay de progression"""
        if self.progress_overlay and self.progress_overlay.winfo_exists():
            progress = current / total if total > 0 else 0
            self.progress_bar.set(progress)
            self.progress_label.configure(text=f"{progress * 100:.1f}% ({current}/{total})")
            
            if message:
                self.progress_message.configure(text=message)
            
            self.progress_overlay.update()
    
    def hide_progress_overlay(self):
        """Masque l'overlay de progression"""
        if self.progress_overlay:
            self.progress_overlay.destroy()
            self.progress_overlay = None
    
    # ============================================================================
    # CONFIGURATION
    # ============================================================================
    
    def save_config(self):
        """Sauvegarde la configuration de manière sécurisée"""
        try:
            config_data = {
                'instance_id': self.instance_id.get(),
                'token': self.token.get(),
                'phone_column': self.phone_column.get(),
                'selected_image': self.selected_image.get(),
                'include_excel_data': self.include_excel_data.get(),
                'api_visible': self.api_visible.get() if hasattr(self, 'api_visible') else False,
                'user_message': self.user_message.get("0.0", "end-1c") if hasattr(self, 'user_message') else ''
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"Erreur sauvegarde config: {str(e)}")
    
    def load_config(self):
        """Charge la configuration sauvegardée"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Restaurer les valeurs
                self.instance_id.set(config.get('instance_id', ''))
                self.token.set(config.get('token', ''))
                self.phone_column.set(config.get('phone_column', ''))
                self.selected_image.set(config.get('selected_image', ''))
                self.include_excel_data.set(config.get('include_excel_data', True))
                
                if hasattr(self, 'user_message') and config.get('user_message'):
                    self.user_message.delete("0.0", "end")
                    self.user_message.insert("0.0", config.get('user_message', ''))
                
                # Restaurer la visibilité de l'API
                api_visible = config.get('api_visible', False)
                if hasattr(self, 'api_visible'):
                    self.api_visible.set(api_visible)
                    if api_visible:
                        self.api_section.pack(fill='x', padx=20, pady=(5, 15))
                        self.api_toggle_btn.configure(text="📱 Configuration UltraMsg API  ▼")
            
        except Exception as e:
            print(f"Erreur chargement config: {str(e)}")
    
    def on_config_change(self, *_):
        """Sauvegarde automatique lors des changements"""
        self.root.after_idle(self.save_config)
    
    def on_closing(self):
        """Gestionnaire de fermeture de l'application"""
        try:
            # Sauvegarder la configuration
            self.save_config()
            
            # Arrêter tout envoi en cours
            if self.is_sending:
                self.is_sending = False
            
            # Fermer l'overlay s'il existe
            if self.progress_overlay:
                self.progress_overlay.destroy()
            
        except Exception as e:
            print(f"Erreur fermeture: {str(e)}")
        
        finally:
            self.root.destroy()


def main():
    """Point d'entrée principal de l'application complète"""
    try:
        root = ctk.CTk()
        app = ExcelWhatsAppCompleteApp(root)
        root.mainloop()
        
    except Exception as e:
        try:
            messagebox.showerror(
                "Erreur de démarrage",
                f"Impossible de démarrer l'application:\\n\\n{str(e)}"
            )
        except:
            print(f"Erreur critique: {str(e)}")


if __name__ == "__main__":
    main()