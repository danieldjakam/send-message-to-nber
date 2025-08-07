# -*- coding: utf-8 -*-
"""
Application Excel vers WhatsApp - Version optimisée pour gros volumes (10k+ messages)

Cette version résout les problèmes de plantage lors de l'envoi à grande échelle
avec des améliorations de performance et de stabilité.

Version: 2.1 - Optimisée pour gros volumes
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
from tkinter import ttk
import tkinter as tk
import threading
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

# Imports des modules personnalisés
from config.config_manager import ConfigManager
from api.whatsapp_client import WhatsAppClient, MessageResult
from api.bulk_sender import BulkSender
from utils.validators import PhoneValidator, DataValidator
from utils.logger import logger
from utils.exceptions import *
from ui.components import (
    StatusIndicator, ProgressFrame, CollapsibleSection, 
    ValidatedEntry, DataTable, MessageComposer
)
from ui.bulk_send_dialog import BulkSendDialog

# Configuration globale
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ExcelWhatsAppApp:
    """Application principale Excel vers WhatsApp optimisée pour gros volumes"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Excel vers WhatsApp Pro - Optimisé Gros Volumes")
        self.root.geometry("1200x900")
        self.root.minsize(800, 600)
        
        # Configuration et logger
        self.config_manager = ConfigManager()
        logger.info("app_started", version="2.1")
        
        # Variables principales
        self.df: Optional[pd.DataFrame] = None
        self.whatsapp_client: Optional[WhatsAppClient] = None
        self.bulk_sender: Optional[BulkSender] = None
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
        self._setup_config_traces()
        
        # Interface utilisateur
        self.create_widgets()
        
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
    
    def create_widgets(self):
        """Crée l'interface utilisateur moderne"""
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
            text="Version 2.1 - Optimisé Gros Volumes (10k+ messages)",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        version_label.pack()
        
        # Status global
        self.status_indicator = StatusIndicator(
            self.root,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_indicator.pack(pady=(0, 10))
        
        # Section de sélection de fichier
        self.file_section = self._create_file_section()
        
        # Section de configuration API (repliable)
        self.api_section = self._create_api_section()
        
        # Barre de progression
        self.progress_frame = ProgressFrame(self.root)
        
        # Section des colonnes
        self.columns_section = self._create_columns_section()
        
        # Section d'affichage des données
        self.data_section = self._create_data_section()
    
    def _create_file_section(self) -> ctk.CTkFrame:
        """Crée la section de sélection de fichier"""
        file_frame = ctk.CTkFrame(self.root, corner_radius=15)
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
            command=self.load_file,
            height=40,
            width=100,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        load_btn.pack(side='left')
        
        return file_frame
    
    def _create_api_section(self) -> CollapsibleSection:
        """Crée la section de configuration API"""
        api_section = CollapsibleSection(self.root, "📱 Configuration UltraMsg API")
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
        columns_frame = ctk.CTkFrame(self.root, corner_radius=15)
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
        data_frame = ctk.CTkFrame(self.root, corner_radius=15)
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
    
    def load_file(self):
        """Charge un fichier Excel avec validation complète"""
        self._sync_ui_with_variables()
        
        file_path = self.selected_file.get()
        if not file_path:
            self.status_indicator.set_status('error', 'Aucun fichier sélectionné')
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier Excel.")
            return
        
        try:
            self.status_indicator.set_status('info', 'Chargement du fichier...')
            
            is_valid, validation_message = DataValidator.validate_excel_file(file_path)
            if not is_valid:
                self.status_indicator.set_status('error', 'Fichier invalide')
                messagebox.showerror("Fichier invalide", validation_message)
                return
            
            self.df = pd.read_excel(file_path)
            
            if self.df.empty:
                raise FileError("Le fichier Excel est vide")
            
            self.create_column_checkboxes()
            self.update_phone_column_options()
            self.columns_section.pack(fill='x', padx=30, pady=10)
            
            logger.log_file_loaded(file_path, len(self.df), len(self.df.columns))
            self.status_indicator.set_status('success', f'Fichier chargé: {len(self.df)} lignes')
            
            # Afficher une alerte pour les gros volumes
            if len(self.df) > 5000:
                messagebox.showinfo(
                    "⚠️ Gros Volume Détecté",
                    f"📊 {len(self.df)} lignes détectées\\n\\n"
                    f"🚀 Optimisation automatique activée:\\n"
                    f"• Traitement par batches\\n"
                    f"• Interface dédiée pour gros volumes\\n"
                    f"• Gestion mémoire optimisée\\n\\n"
                    f"L'envoi sera géré de manière optimale."
                )
            else:
                messagebox.showinfo(
                    "✅ Fichier chargé", 
                    f"Chargement réussi !\\n\\n"
                    f"📊 {len(self.df)} lignes\\n"
                    f"📋 {len(self.df.columns)} colonnes"
                )
            
        except Exception as e:
            error_msg = f"Erreur lors du chargement: {str(e)}"
            self.status_indicator.set_status('error', 'Erreur de chargement')
            logger.error("file_load_error", file_path=file_path, error=str(e))
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
                    f"L'API fonctionne parfaitement !\\n\\n"
                    f"📱 Numéro testé: {PhoneValidator.format_for_whatsapp(test_phone)}\\n"
                    f"📨 Message envoyé avec succès\\n\\n"
                    f"🚀 Prêt pour l'envoi en masse optimisé."
                )
            else:
                self.api_status.set_status('error', 'Test échoué')
                messagebox.showerror("❌ Test échoué", f"Le test a échoué:\\n\\n{message}")
        
        except Exception as e:
            error_msg = f"Erreur lors du test: {str(e)}"
            self.api_status.set_status('error', 'Erreur test')
            logger.error("api_test_error", error=str(e))
            messagebox.showerror("❌ Erreur", error_msg)
    
    def start_bulk_send_optimized(self):
        """Démarre l'envoi en masse optimisé pour de gros volumes"""
        if self.is_sending:
            messagebox.showwarning("⚠️ Envoi en cours", "Un envoi est déjà en cours. Veuillez patienter.")
            return
        
        try:
            self._sync_ui_with_variables()
            
            validation_errors = self._validate_bulk_send_data()
            if validation_errors:
                messagebox.showerror("❌ Données invalides", "\\n".join(validation_errors))
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
            
            # Pour les gros volumes (>1000), utiliser le dialog optimisé
            if len(messages_data) > 1000:
                self._show_bulk_send_dialog(messages_data)
            else:
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
    
    def _execute_simple_bulk_send(self, messages_data: List[tuple]):
        """Exécute un envoi simple dans un thread séparé"""
        try:
            self.root.after(0, lambda: self.progress_frame.show("Envoi des messages en cours..."))
            
            def progress_callback(completed, total):
                progress = completed / total if total > 0 else 0
                self.root.after(0, lambda: self.progress_frame.update(
                    completed, total, 
                    f"Envoi {completed}/{total} - {progress*100:.1f}%"
                ))
            
            session = self.bulk_sender.send_bulk_optimized(
                messages_data,
                progress_callback=progress_callback,
                status_callback=lambda msg: self.root.after(0, lambda: self.progress_frame.progress_label.configure(text=msg))
            )
            
            self.root.after(0, lambda: self._handle_simple_bulk_send_results(session))
            
        except Exception as e:
            error_msg = f"Erreur lors de l'envoi: {str(e)}"
            logger.error("simple_bulk_send_execution_error", error=str(e))
            self.root.after(0, lambda: self._handle_simple_bulk_send_error(error_msg))
    
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
                f"✅ Envoi terminé avec succès !\\n\\n"
                f"📊 Total envoyé: {stats['successful']} messages\\n"
                f"🎯 Taux de réussite: {stats['success_rate']:.1f}%"
            )
            messagebox.showinfo(report_title, report_msg)
        else:
            report_msg = (
                f"⚠️ Envoi terminé avec erreurs\\n\\n"
                f"✅ Réussis: {stats['successful']}\\n"
                f"❌ Échecs: {stats['failed']}\\n"
                f"📊 Total: {stats['total']}\\n"
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
        """Prépare les données pour l'envoi en masse"""
        messages = []
        phone_column = self.phone_column.get()
        user_message = self.message_composer.get_message()
        image_path = self.selected_image.get() if self.selected_image.get() else None
        
        selected_columns = []
        if self.include_excel_data.get():
            selected_columns = [col for col, var in self.column_vars.items() if var.get()]
        
        for idx, row in self.df.iterrows():
            phone_raw = str(row[phone_column]).strip()
            
            if not phone_raw or phone_raw.lower() in ['nan', 'none', '']:
                continue
            
            if not PhoneValidator.is_valid_phone(phone_raw):
                logger.warning("invalid_phone_skipped", phone=phone_raw, row=idx)
                continue
            
            message = user_message
            if selected_columns:
                data_lines = []
                for col in selected_columns:
                    value = str(row[col]) if pd.notna(row[col]) else "N/A"
                    data_lines.append(f"{col}: {value}")
                
                if data_lines:
                    message += "\\n\\n📋 Données:\\n" + "\\n".join(data_lines)
            
            messages.append((phone_raw, message, image_path))
        
        return messages
    
    def _confirm_bulk_send(self, total_messages: int) -> bool:
        """Demande confirmation avant l'envoi en masse"""
        if total_messages > 5000:
            confirm_msg = (
                f"🚀 Envoi en Masse - GROS VOLUME\\n\\n"
                f"📊 Nombre de messages: {total_messages}\\n"
                f"💬 Type: {'Image + Texte' if self.selected_image.get() else 'Texte uniquement'}\\n"
                f"📋 Données incluses: {'Oui' if self.include_excel_data.get() else 'Non'}\\n\\n"
                f"⚡ Mode optimisé activé pour gros volumes:\\n"
                f"• Traitement par batches de 50 messages\\n"
                f"• Threading intelligent (max 3 threads)\\n"
                f"• Gestion mémoire optimisée\\n"
                f"• Possibilité de pause/reprise\\n\\n"
                f"⚠️ Cette opération peut prendre plusieurs heures.\\n"
                f"Êtes-vous sûr de vouloir continuer ?"
            )
        else:
            confirm_msg = (
                f"🚀 Confirmation d'envoi en masse\\n\\n"
                f"📊 Nombre de messages: {total_messages}\\n"
                f"💬 Type: {'Image + Texte' if self.selected_image.get() else 'Texte uniquement'}\\n"
                f"📋 Données incluses: {'Oui' if self.include_excel_data.get() else 'Non'}\\n\\n"
                f"⚠️ Cette action enverra des messages à tous les destinataires.\\n"
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
                message = config.get('user_message', 'Bonjour,\\n\\nVoici les informations demandées.\\n\\nCordialement.')
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


def main():
    """Point d'entrée principal de l'application"""
    try:
        root = ctk.CTk()
        app = ExcelWhatsAppApp(root)
        
        logger.info("app_mainloop_started", version="2.1")
        root.mainloop()
        
    except Exception as e:
        logger.error("app_startup_error", error=str(e))
        try:
            messagebox.showerror(
                "Erreur de démarrage",
                f"Impossible de démarrer l'application:\\n\\n{str(e)}"
            )
        except:
            print(f"Erreur critique: {str(e)}")
    
    finally:
        logger.info("app_terminated")


if __name__ == "__main__":
    main()