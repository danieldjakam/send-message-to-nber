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
from typing import Optional, List, Dict, Any

# Imports des modules personnalisés
from config.config_manager import ConfigManager
from api.whatsapp_client import WhatsAppClient, MessageResult
from api.bulk_sender import BulkSender
from utils.validators import PhoneValidator, DataValidator
from utils.logger import logger
from utils.exceptions import *
from utils.anti_spam_manager import AntiSpamManager
from ui.components import (
    StatusIndicator, ProgressFrame, CollapsibleSection, 
    ValidatedEntry, DataTable, MessageComposer
)
from ui.bulk_send_dialog import BulkSendDialog
from ui.progress_widgets import DetailedProgressDialog, SimpleProgressOverlay
from ui.sent_numbers_dialog import SentNumbersDialog
from ui.anti_spam_config_widget import UserCustomizableAntiSpamWidget

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
        
        # Système anti-spam
        self.anti_spam_manager = AntiSpamManager()
        self.anti_spam_widget: Optional[UserCustomizableAntiSpamWidget] = None
        
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
            command=self.load_file_with_progress,
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
        test_btn.pack(side='left', padx=(0, 5))
        
        history_btn = ctk.CTkButton(
            action_buttons, 
            text="📚 Historique", 
            command=self.show_sent_numbers_dialog,
            height=35, 
            width=90,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=("#8B4513", "#A0522D")
        )
        history_btn.pack(side='left', padx=(0, 3))
        
        config_btn = ctk.CTkButton(
            action_buttons, 
            text="⚙️ Config", 
            command=self.show_config_dialog,
            height=35, 
            width=80,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=("#4B0082", "#6A0DAD")
        )
        config_btn.pack(side='left', padx=(0, 3))
        
        antispam_btn = ctk.CTkButton(
            action_buttons, 
            text="🛡️ Anti-Spam", 
            command=self.show_anti_spam_config,
            height=35, 
            width=90,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=("#DC143C", "#B22222")
        )
        antispam_btn.pack(side='left', padx=(0, 5))
        
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
        
        validate_btn = ctk.CTkButton(
            action_frame, 
            text="📱 Valider numéros", 
            command=self.validate_phone_numbers,
            height=30,
            width=120,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#FF8C00", "#FF4500")
        )
        validate_btn.pack(side='right', padx=(0, 10))
        
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
    
    def validate_phone_numbers(self):
        """Valide les numéros de téléphone dans le fichier chargé"""
        if self.df is None or self.df.empty:
            self.status_indicator.set_status('error', 'Aucune donnée chargée')
            messagebox.showerror("Erreur", "Veuillez d'abord charger un fichier Excel.")
            return
        
        phone_column = self.phone_column.get()
        if not phone_column or phone_column not in self.df.columns:
            self.status_indicator.set_status('warning', 'Colonne manquante')
            messagebox.showwarning("Attention", "Veuillez sélectionner une colonne de numéros de téléphone.")
            return
        
        try:
            total_phones = 0
            valid_phones = 0
            invalid_phones = []
            processing_errors = []
            
            for idx, row in self.df.iterrows():
                # Utiliser la nouvelle méthode de nettoyage
                original_value = row[phone_column]
                phone_cleaned = self._extract_clean_phone_number(original_value)
                
                # Compter seulement les cellules non vides dans Excel
                if pd.notna(original_value) and str(original_value).strip():
                    total_phones += 1
                    
                    if not phone_cleaned:
                        # Le numéro n'a pas pu être nettoyé (format invalide)
                        suggestion = self._get_phone_format_suggestions(original_value)
                        processing_errors.append({
                            'ligne': idx + 2,
                            'original': str(original_value),
                            'erreur': suggestion
                        })
                        continue
                    
                    if PhoneValidator.is_valid_phone(phone_cleaned):
                        valid_phones += 1
                    else:
                        invalid_phones.append({
                            'ligne': idx + 2,
                            'original': str(original_value),
                            'numero_nettoye': phone_cleaned
                        })
            
            invalid_count = len(invalid_phones)
            error_count = len(processing_errors)
            total_problematic = invalid_count + error_count
            valid_percentage = (valid_phones / total_phones * 100) if total_phones > 0 else 0
            
            # Préparer le rapport
            report_msg = f"📊 Rapport de validation des numéros\\n\\n"
            report_msg += f"📱 Total analysé: {total_phones} numéros\\n"
            report_msg += f"✅ Valides: {valid_phones} ({valid_percentage:.1f}%)\\n"
            
            if error_count > 0:
                report_msg += f"⚠️ Erreurs de format: {error_count}\\n"
            if invalid_count > 0:
                report_msg += f"❌ Invalides: {invalid_count}\\n"
            
            report_msg += f"\\n"
            
            # Détails des erreurs de format
            if error_count > 0:
                report_msg += f"🔧 Erreurs de format (premiers 3):\\n"
                for i, error in enumerate(processing_errors[:3]):
                    original_short = error['original'][:20] + "..." if len(error['original']) > 20 else error['original']
                    report_msg += f"  • Ligne {error['ligne']}: {original_short} ({error['erreur']})\\n"
                
                if error_count > 3:
                    report_msg += f"  ... et {error_count - 3} autres\\n"
                report_msg += f"\\n"
            
            # Détails des numéros invalides
            if invalid_count > 0:
                report_msg += f"🔍 Numéros invalides (premiers 3):\\n"
                for i, invalid in enumerate(invalid_phones[:3]):
                    report_msg += f"  • Ligne {invalid['ligne']}: {invalid['numero_nettoye']} (depuis: {invalid['original'][:15]}...)\\n"
                
                if invalid_count > 3:
                    report_msg += f"  ... et {invalid_count - 3} autres\\n"
                report_msg += f"\\n"
            
            if total_problematic > 0:
                report_msg += f"💡 Ces {total_problematic} numéros seront automatiquement ignorés lors de l'envoi.\\n\\n"
                report_msg += f"🔧 Conseils pour corriger dans Excel:\\n"
                report_msg += f"• Format → Cellules → Catégorie: 'Texte' (évite la notation scientifique)\\n"
                report_msg += f"• Supprimer les virgules dans les numéros (650,153,059 → 650153059)\\n"
                report_msg += f"• Utiliser le format international: +237XXXXXXXXX"
            
            # Afficher le rapport
            if total_problematic == 0:
                messagebox.showinfo("✅ Validation réussie", report_msg)
                self.status_indicator.set_status('success', f'Tous les numéros sont valides')
            else:
                messagebox.showwarning("⚠️ Numéros invalides détectés", report_msg)
                self.status_indicator.set_status('warning', f'{total_problematic} numéros problématiques')
            
            logger.info("phone_validation_completed", 
                       total=total_phones, 
                       valid=valid_phones, 
                       invalid=invalid_count,
                       format_errors=error_count,
                       valid_percentage=valid_percentage)
                       
        except Exception as e:
            error_msg = f"Erreur lors de la validation: {str(e)}"
            self.status_indicator.set_status('error', 'Erreur de validation')
            logger.error("phone_validation_error", error=str(e))
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
                phone_raw = self._extract_clean_phone_number(row[phone_column_name])
                if phone_raw and PhoneValidator.is_valid_phone(phone_raw):
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
            # Callbacks pour la progression détaillée
            def progress_callback(completed, total, status):
                self.root.after(0, lambda: self.detailed_progress.update_progress(
                    completed, total, status
                ))
            
            def status_callback(msg):
                self.root.after(0, lambda: self.detailed_progress.add_log(msg))
            
            # Exécuter l'envoi
            session = self.bulk_sender.send_bulk_optimized(
                messages_data,
                progress_callback=progress_callback,
                status_callback=status_callback
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
            # Utiliser la barre de progression intégrée
            self.root.after(0, lambda: self.progress_frame.show("Envoi des messages..."))
            
            def progress_callback(completed, total, status):
                self.root.after(0, lambda: self.progress_frame.update(
                    completed, total, status
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
    
    def _handle_detailed_bulk_send_results(self, session):
        """Traite les résultats de l'envoi détaillé"""
        try:
            self.is_sending = False
            self.send_btn.configure(text="🚀 Envoyer", state="normal")
            
            # Mettre à jour les statistiques finales dans le dialog
            stats = self.bulk_sender.get_session_stats(session)
            
            # Utiliser les stats pour éviter les erreurs d'attributs
            failed_count = stats.get('failed', session.failed if hasattr(session, 'failed') else 0)
            successful_count = stats.get('successful', session.successful if hasattr(session, 'successful') else 0)
            total_count = stats.get('total', session.total_messages if hasattr(session, 'total_messages') else 0)
            
            self.detailed_progress.set_success_count(successful_count)
            self.detailed_progress.set_error_count(failed_count)
            
            # Ajouter un log de fin
            if failed_count == 0:
                self.detailed_progress.add_log("✅ Envoi terminé avec succès !")
                self.status_indicator.set_status('success', f"Envoi terminé: {successful_count}/{total_count}")
            else:
                self.detailed_progress.add_log(f"⚠️ Envoi terminé avec {failed_count} erreurs")
                self.status_indicator.set_status('warning', f"Envoi terminé avec erreurs: {successful_count}/{total_count}")
            
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
            
            # Utiliser les stats plutôt que les attributs directs
            failed_count = stats.get('failed', session.failed if hasattr(session, 'failed') else 0)
            successful_count = stats.get('successful', session.successful if hasattr(session, 'successful') else 0)
            total_count = stats.get('total', session.total_messages if hasattr(session, 'total_messages') else 0)
            
            if failed_count == 0:
                self.status_indicator.set_status('success', f"Envoi terminé: {successful_count}/{total_count}")
            else:
                self.status_indicator.set_status('warning', f"Envoi terminé avec erreurs: {successful_count}/{total_count}")
        
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
    
    def _extract_clean_phone_number(self, phone_value) -> str:
        """Extrait et nettoie un numéro de téléphone depuis Excel avec gestion avancée"""
        if pd.isna(phone_value) or phone_value is None:
            return ""
        
        # Convertir en string et nettoyer les espaces
        phone_str = str(phone_value).strip()
        
        # Vérifier si c'est vide ou des valeurs nulles
        if not phone_str or phone_str.lower() in ['nan', 'none', 'null', '']:
            return ""
        
        # Supprimer les séparateurs de milliers d'Excel (virgules, espaces)
        # Exemples: "650,153,059" → "650153059", "650 153 059" → "650153059"
        phone_str = phone_str.replace(',', '').replace(' ', '')
        
        # Gérer les formats Excel avec points décimaux (ex: "650153059.0")
        if phone_str.endswith('.0'):
            phone_str = phone_str[:-2]
        
        # Gérer les nombres en notation scientifique (ex: 6.55474776e+17)
        if 'e+' in phone_str.lower() or 'e-' in phone_str.lower():
            try:
                # Convertir en float puis en int pour éviter la notation scientifique
                float_val = float(phone_str)
                if float_val.is_integer() and float_val > 0:
                    phone_str = str(int(float_val))
                else:
                    return ""  # Nombre non valide
            except (ValueError, OverflowError):
                return ""
        
        # Gérer les formats avec tirets ou autres séparateurs
        # Ex: "650-153-059", "650.153.059", "650 153 059"
        import re
        if phone_str.startswith('+'):
            # Conserver le + international et nettoyer le reste
            prefix = '+'
            number_part = phone_str[1:]
            # Supprimer tous les caractères non numériques
            cleaned_number = re.sub(r'[^\d]', '', number_part)
            cleaned = prefix + cleaned_number
        else:
            # Supprimer tous les caractères non numériques
            cleaned = re.sub(r'[^\d]', '', phone_str)
        
        # Vérifier la longueur (numéros de téléphone valides : 8 à 15 chiffres)
        if cleaned.startswith('+'):
            digits_only = cleaned[1:]
        else:
            digits_only = cleaned
        
        if len(digits_only) < 8 or len(digits_only) > 15:
            return ""  # Longueur invalide
        
        # Éviter les numéros qui sont clairement des erreurs
        if digits_only == '0' * len(digits_only):
            return ""  # Que des zéros
        
        # Éviter les numéros avec trop de chiffres répétés (probablement une erreur)
        if len(set(digits_only)) == 1:  # Tous les chiffres identiques
            return ""
        
        # Gestion intelligente des préfixes pays
        if not cleaned.startswith('+'):
            if len(digits_only) == 9 and digits_only.startswith('6'):
                # Numéro camerounais mobile probable (6xxxxxxxx)
                cleaned = '+237' + digits_only
            elif len(digits_only) == 10 and digits_only.startswith('65'):
                # Numéro camerounais avec 0 initial omis (65xxxxxxx)
                cleaned = '+237' + digits_only
            elif len(digits_only) == 12 and digits_only.startswith('237'):
                # Numéro avec préfixe 237 mais sans +
                cleaned = '+' + digits_only
        
        return cleaned
    
    def _get_phone_format_suggestions(self, original_value: str, cleaned_value: str = "") -> str:
        """Fournit des suggestions pour corriger les formats de numéros"""
        if not original_value or str(original_value).strip() in ['nan', 'none', 'null', '']:
            return "Cellule vide"
        
        original_str = str(original_value).strip()
        
        # Détecter le problème spécifique
        if ',' in original_str:
            return f"Séparateurs de milliers détectés. Utilisez: {original_str.replace(',', '')}"
        elif ' ' in original_str and len(original_str.replace(' ', '')) > 8:
            return f"Espaces détectés. Utilisez: {original_str.replace(' ', '')}"
        elif 'e+' in original_str.lower() or 'e-' in original_str.lower():
            return "Notation scientifique - reformatez la cellule Excel en 'Texte'"
        elif len(original_str) > 15:
            return "Trop long pour un numéro de téléphone"
        elif cleaned_value and len(set(cleaned_value.replace('+', ''))) == 1:
            return "Tous les chiffres sont identiques"
        else:
            return "Format non reconnu"
    
    def _format_delay_text(self, seconds: float) -> str:
        """Formate le délai en texte lisible"""
        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds} secondes"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            if remaining_seconds == 0:
                return f"{minutes} minutes"
            else:
                return f"{minutes}min {remaining_seconds}s"
        else:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            if remaining_minutes == 0:
                return f"{hours} heures"
            else:
                return f"{hours}h {remaining_minutes}min"
    
    def _prepare_messages_data(self) -> List[tuple]:
        """Prépare les données pour l'envoi en masse"""
        messages = []
        phone_column = self.phone_column.get()
        user_message = self.message_composer.get_message()
        image_path = self.selected_image.get() if self.selected_image.get() else None
        
        selected_columns = []
        if self.include_excel_data.get():
            selected_columns = [col for col, var in self.column_vars.items() if var.get()]
        
        skipped_empty = 0
        skipped_invalid = 0
        
        for idx, row in self.df.iterrows():
            # Meilleure extraction du numéro depuis Excel
            phone_raw = self._extract_clean_phone_number(row[phone_column])
            
            if not phone_raw:
                skipped_empty += 1
                continue
            
            if not PhoneValidator.is_valid_phone(phone_raw):
                skipped_invalid += 1
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
            
            messages.append((phone_raw, message, image_path))
        
        # Log de résumé pour éviter le spam dans les logs
        if skipped_empty > 0 or skipped_invalid > 0:
            logger.info("phone_processing_summary", 
                       total_processed=len(self.df),
                       messages_created=len(messages),
                       skipped_empty=skipped_empty,
                       skipped_invalid=skipped_invalid)
        
        return messages
    
    def _confirm_bulk_send(self, total_messages: int) -> bool:
        """Demande confirmation avant l'envoi en masse avec description des barres de chargement"""
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
                f"• Configuration des paramètres\n\n"
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
                f"• Compteurs de succès/échecs\n\n"
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
                f"• Changement de couleur selon l'avancement\n\n"
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
    
    def show_sent_numbers_dialog(self):
        """Affiche le dialog de gestion des numéros envoyés"""
        try:
            if not self.bulk_sender:
                if not self.whatsapp_client:
                    # Créer une instance temporaire juste pour accéder aux numéros
                    from api.bulk_sender import BulkSender
                    from api.whatsapp_client import WhatsAppClient
                    temp_client = WhatsAppClient("temp", "temp")
                    self.bulk_sender = BulkSender(temp_client)
                else:
                    self.bulk_sender = BulkSender(self.whatsapp_client)
            
            # Créer le dialog
            dialog = SentNumbersDialog(self.root, self.bulk_sender)
            
        except Exception as e:
            error_msg = f"Erreur lors de l'ouverture de l'historique: {str(e)}"
            logger.error("sent_numbers_dialog_error", error=str(e))
            messagebox.showerror("❌ Erreur", error_msg)
    
    def show_config_dialog(self):
        """Affiche le dialog de configuration des paramètres d'envoi"""
        try:
            if not self.bulk_sender:
                if not self.whatsapp_client:
                    from api.bulk_sender import BulkSender
                    from api.whatsapp_client import WhatsAppClient
                    temp_client = WhatsAppClient("temp", "temp")
                    self.bulk_sender = BulkSender(temp_client)
                else:
                    self.bulk_sender = BulkSender(self.whatsapp_client)
            
            # Dialog simple pour la configuration
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("⚙️ Configuration d'Envoi")
            dialog.geometry("500x400")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Centrer la fenêtre
            x = (dialog.winfo_screenwidth() // 2) - (250)
            y = (dialog.winfo_screenheight() // 2) - (200)
            dialog.geometry(f"500x400+{x}+{y}")
            
            # Titre
            title_label = ctk.CTkLabel(
                dialog,
                text="⚙️ Configuration des Paramètres d'Envoi",
                font=ctk.CTkFont(size=18, weight="bold")
            )
            title_label.pack(pady=20)
            
            # Frame principal
            main_frame = ctk.CTkFrame(dialog, corner_radius=15)
            main_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
            
            # Configuration actuelle
            current_frame = ctk.CTkFrame(main_frame, corner_radius=10)
            current_frame.pack(fill='x', padx=20, pady=(20, 10))
            
            ctk.CTkLabel(
                current_frame,
                text="📊 Configuration des Délais d'Envoi",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(pady=(10, 5))
            
            # Variables pour les paramètres
            import tkinter as tk
            delay_var = tk.DoubleVar(value=self.bulk_sender.message_delay)
            burst_var = tk.IntVar(value=self.bulk_sender.message_burst_limit)
            pause_var = tk.IntVar(value=self.bulk_sender.burst_pause_duration)
            
            # Délai entre messages
            delay_frame = ctk.CTkFrame(current_frame, fg_color="transparent")
            delay_frame.pack(fill='x', padx=10, pady=5)
            
            ctk.CTkLabel(delay_frame, text="⏱️ Délai entre messages:", font=ctk.CTkFont(size=12)).pack(anchor='w')
            delay_slider = ctk.CTkSlider(delay_frame, from_=1, to=3600, variable=delay_var, number_of_steps=60)
            delay_slider.pack(fill='x', pady=2)
            delay_label = ctk.CTkLabel(delay_frame, text=self._format_delay_text(delay_var.get()), font=ctk.CTkFont(size=10))
            delay_label.pack(anchor='w')
            def on_delay_change(v):
                delay_label.configure(text=self._format_delay_text(float(v)))
                # Sauvegarde automatique avec un léger délai pour éviter le spam
                self.root.after(500, auto_save_config)
            
            delay_slider.configure(command=on_delay_change)
            
            # Messages par série
            burst_frame = ctk.CTkFrame(current_frame, fg_color="transparent")
            burst_frame.pack(fill='x', padx=10, pady=5)
            
            ctk.CTkLabel(burst_frame, text="🚀 Messages par série:", font=ctk.CTkFont(size=12)).pack(anchor='w')
            burst_slider = ctk.CTkSlider(burst_frame, from_=5, to=50, variable=burst_var, number_of_steps=45)
            burst_slider.pack(fill='x', pady=2)
            burst_label = ctk.CTkLabel(burst_frame, text=f"{burst_var.get()} messages", font=ctk.CTkFont(size=10))
            burst_label.pack(anchor='w')
            def on_burst_change(v):
                burst_label.configure(text=f"{int(float(v))} messages")
                self.root.after(500, auto_save_config)
            
            burst_slider.configure(command=on_burst_change)
            
            # Pause entre séries
            pause_frame = ctk.CTkFrame(current_frame, fg_color="transparent")
            pause_frame.pack(fill='x', padx=10, pady=5)
            
            ctk.CTkLabel(pause_frame, text="⏸️ Pause entre séries:", font=ctk.CTkFont(size=12)).pack(anchor='w')
            pause_slider = ctk.CTkSlider(pause_frame, from_=10, to=300, variable=pause_var, number_of_steps=58)
            pause_slider.pack(fill='x', pady=2)
            pause_label = ctk.CTkLabel(pause_frame, text=f"{pause_var.get()} secondes", font=ctk.CTkFont(size=10))
            pause_label.pack(anchor='w')
            def on_pause_change(v):
                pause_label.configure(text=f"{int(float(v))} secondes")
                self.root.after(500, auto_save_config)
            
            pause_slider.configure(command=on_pause_change)
            
            # Info frame
            info_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=("#1E90FF", "#4682B4"))
            info_frame.pack(fill='x', padx=20, pady=10)
            
            ctk.CTkLabel(
                info_frame,
                text="💡 Exemples: 2s = Rapide | 30s = Modéré | 300s = 5min | 3600s = 1 heure | Max: 1 heure",
                font=ctk.CTkFont(size=11),
                text_color="white",
                wraplength=400
            ).pack(pady=8)
            
            # Boutons d'action
            buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            buttons_frame.pack(fill='x', padx=20, pady=10)
            
            def auto_save_config():
                """Sauvegarde automatique des paramètres dès modification"""
                try:
                    self.bulk_sender.configure_sending_parameters(
                        message_delay=delay_var.get(),
                        burst_limit=int(burst_var.get()),
                        burst_pause=int(pause_var.get())
                    )
                    # Sauvegarde silencieuse - pas de popup
                except Exception as e:
                    print(f"Erreur sauvegarde auto: {e}")
            
            def apply_config():
                # Appliquer et confirmer
                auto_save_config()
                messagebox.showinfo("✅ Configuration appliquée", 
                                  f"Paramètres actifs:\\n"
                                  f"• Délai: {self._format_delay_text(delay_var.get())}\\n"
                                  f"• Série: {burst_var.get()} messages\\n"
                                  f"• Pause: {pause_var.get()}s entre séries")
            
            def reset_to_fast():
                # Configuration avec 5 minutes entre messages (nouvelle configuration par défaut)
                delay_var.set(300.0)
                burst_var.set(1)
                pause_var.set(10)
                # Mise à jour des labels
                delay_label.configure(text=self._format_delay_text(300.0))
                burst_label.configure(text="1 message")
                pause_label.configure(text="10 secondes")
                # Sauvegarde automatique
                auto_save_config()
            
            def reset_to_5min_pause():
                # Configuration avec pause de 5 minutes après chaque message
                delay_var.set(300.0)  # 5 minutes
                burst_var.set(1)      # 1 message par série
                pause_var.set(10)     # Pause courte entre séries (peu utilisée)
                # Mise à jour des labels
                delay_label.configure(text=self._format_delay_text(300.0))
                burst_label.configure(text="1 message")
                pause_label.configure(text="10 secondes")
                # Sauvegarde automatique
                auto_save_config()
            
            def reset_to_moderate():
                # Configuration modérée avec pauses raisonnables
                delay_var.set(30.0)
                burst_var.set(10)
                pause_var.set(60)
                # Mise à jour des labels
                delay_label.configure(text=self._format_delay_text(30.0))
                burst_label.configure(text="10 messages")
                pause_label.configure(text="60 secondes")
                # Sauvegarde automatique
                auto_save_config()
            
            ctk.CTkButton(
                buttons_frame,
                text="🛡️ Sécurisé",
                command=reset_to_fast,
                height=35,
                width=80,
                fg_color=("#32CD32", "#228B22")
            ).pack(side='left', padx=(0, 3))
            
            ctk.CTkButton(
                buttons_frame,
                text="🕐 Modéré",
                command=reset_to_moderate,
                height=35,
                width=70,
                fg_color=("#FFA500", "#FF8C00")
            ).pack(side='left', padx=3)
            
            ctk.CTkButton(
                buttons_frame,
                text="⏳ 5min",
                command=reset_to_5min_pause,
                height=35,
                width=60,
                fg_color=("#9370DB", "#8A2BE2")
            ).pack(side='left', padx=3)
            
            # Espace entre les boutons et le bouton fermer
            ctk.CTkFrame(buttons_frame, width=20, fg_color="transparent").pack(side='left')
            
            ctk.CTkButton(
                buttons_frame,
                text="❌ Fermer",
                command=dialog.destroy,
                height=35,
                width=80
            ).pack(side='right')
            
            dialog.focus()
            
        except Exception as e:
            error_msg = f"Erreur lors de l'ouverture de la configuration: {str(e)}"
            logger.error("config_dialog_error", error=str(e))
            messagebox.showerror("❌ Erreur", error_msg)
    
    def show_anti_spam_config(self):
        """Affiche la fenêtre de configuration anti-spam"""
        try:
            # Créer la fenêtre de configuration anti-spam
            antispam_window = ctk.CTkToplevel(self.root)
            antispam_window.title("🛡️ Configuration Anti-Spam Avancée")
            antispam_window.geometry("900x700")
            antispam_window.resizable(True, True)
            antispam_window.transient(self.root)
            antispam_window.grab_set()
            
            # Centrer la fenêtre
            x = (antispam_window.winfo_screenwidth() // 2) - 450
            y = (antispam_window.winfo_screenheight() // 2) - 350
            antispam_window.geometry(f"900x700+{x}+{y}")
            
            # Créer le widget anti-spam
            self.anti_spam_widget = UserCustomizableAntiSpamWidget(
                antispam_window, 
                self.anti_spam_manager
            )
            self.anti_spam_widget.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Callbacks pour le widget
            def on_config_change():
                """Callback appelé quand la configuration change"""
                logger.info("anti_spam_config_changed")
                # Optionnel: mettre à jour d'autres composants
            
            def on_test_config(can_send, reason, delay):
                """Callback appelé lors du test de configuration"""
                logger.info("anti_spam_config_tested", 
                           can_send=can_send, reason=reason, delay=delay)
            
            self.anti_spam_widget.on_config_change = on_config_change
            self.anti_spam_widget.on_test_config = on_test_config
            
            antispam_window.focus()
            
        except Exception as e:
            error_msg = f"Erreur lors de l'ouverture de la configuration anti-spam: {str(e)}"
            logger.error("anti_spam_config_dialog_error", error=str(e))
            messagebox.showerror("❌ Erreur", error_msg)
    
    def wait_with_antispam_protection(self, phone_number: str = "", update_callback=None):
        """
        Méthode d'attente avec protection anti-spam intelligent
        Intègre la logique anti-spam dans le processus d'envoi
        """
        try:
            can_send, reason, delay = self.anti_spam_manager.can_send_message(phone_number)
            
            if not can_send:
                # Envoi bloqué - attendre le délai recommandé
                self._countdown_wait(delay, f"⏸️ Attente anti-spam: {reason}", update_callback)
                return False
            
            if delay > 0:
                # Envoi autorisé avec délai - appliquer le délai intelligent
                delay_text = self._format_delay_text(delay)
                self._countdown_wait(delay, f"🕐 Délai anti-spam: {delay_text}", update_callback)
            
            # Enregistrer l'envoi pour les statistiques
            self.anti_spam_manager.record_message_sent(phone_number)
            
            return True
            
        except Exception as e:
            logger.error("anti_spam_wait_error", error=str(e))
            if update_callback:
                update_callback(f"❌ Erreur anti-spam: {str(e)}")
            return True  # Continuer en cas d'erreur pour ne pas bloquer complètement
    
    def _countdown_wait(self, seconds: int, status_message: str, update_callback=None):
        """
        Compte à rebours visuel pour l'attente anti-spam
        """
        if update_callback:
            for remaining in range(seconds, 0, -1):
                if not self.is_sending:  # Arrêter si l'envoi est annulé
                    break
                
                time_text = self._format_delay_text(remaining)
                update_callback(f"{status_message} - Reste: {time_text}")
                time.sleep(1)
            
            # Indiquer que l'attente est terminée
            update_callback(f"{status_message} - Terminé ✅")
        else:
            # Attente simple sans callback
            time.sleep(seconds)
    
    def get_anti_spam_recommendations(self, file_path: str = "", total_messages: int = 0) -> dict:
        """
        Obtient les recommandations anti-spam pour un envoi donné
        """
        try:
            return self.anti_spam_manager.get_recommendations(file_path, total_messages)
        except Exception as e:
            logger.error("anti_spam_recommendations_error", error=str(e))
            return {
                'error': str(e),
                'suggestions': ['❌ Erreur lors de l\'analyse anti-spam']
            }
    
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
    
    def show_sent_numbers_dialog(self):
        """Affiche le dialog de gestion des numéros envoyés"""
        try:
            if not self.bulk_sender:
                if not self.whatsapp_client:
                    # Créer une instance temporaire juste pour accéder aux numéros
                    from api.bulk_sender import BulkSender
                    from api.whatsapp_client import WhatsAppClient
                    temp_client = WhatsAppClient("temp", "temp")
                    self.bulk_sender = BulkSender(temp_client)
                else:
                    self.bulk_sender = BulkSender(self.whatsapp_client)
            
            # Créer le dialog
            dialog = SentNumbersDialog(self.root, self.bulk_sender)
            
        except Exception as e:
            error_msg = f"Erreur lors de l'ouverture de l'historique: {str(e)}"
            logger.error("sent_numbers_dialog_error", error=str(e))
            messagebox.showerror("❌ Erreur", error_msg)


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