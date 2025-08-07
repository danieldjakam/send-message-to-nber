# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
from tkinter import ttk
import tkinter as tk
import requests
import json
import base64
import os
from pathlib import Path

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ExcelReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Lecteur de Fichiers Excel - Interface Moderne")
        self.root.geometry("1000x800")
        
        # Variables
        self.df = None
        self.selected_file = ctk.StringVar()
        self.column_vars = {}
        
        # Variables UltraMsg API
        self.instance_id = ctk.StringVar()
        self.token = ctk.StringVar()
        
        # Ajouter les callbacks de sauvegarde automatique
        self.instance_id.trace_add('write', self.on_config_change)
        self.token.trace_add('write', self.on_config_change)
        
        # Fichier de configuration
        self.config_file = Path.home() / ".excel_whatsapp_config.json"
        
        # Interface
        self.create_widgets()
        
        # Charger la configuration sauvegardée
        self.load_config()
        
        # Sauvegarder à la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        # Configuration du thème
        self.root.configure(fg_color=("#f0f0f0", "#212121"))
        
        # Titre principal
        title_label = ctk.CTkLabel(
            self.root, 
            text="📊 Lecteur de Fichiers Excel", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=30)
        
        # Frame pour la sélection de fichier
        file_frame = ctk.CTkFrame(self.root, corner_radius=15)
        file_frame.pack(pady=20, padx=30, fill='x')
        
        file_label = ctk.CTkLabel(
            file_frame, 
            text="📁 Sélectionner un fichier Excel:", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        file_label.pack(anchor='w', padx=20, pady=(20, 10))
        
        file_select_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_select_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        self.file_entry = ctk.CTkEntry(
            file_select_frame, 
            textvariable=self.selected_file, 
            placeholder_text="Chemin du fichier Excel...",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.file_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            file_select_frame, 
            text="📂 Parcourir", 
            command=self.browse_file,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        browse_btn.pack(side='right')
        
        load_btn = ctk.CTkButton(
            file_frame, 
            text="📄 Charger le fichier", 
            command=self.load_file,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        load_btn.pack(pady=(10, 10))
        
        # Bouton pour masquer/afficher la configuration API
        self.api_visible = tk.BooleanVar(value=False)
        api_toggle_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
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
        self.api_section = ctk.CTkFrame(file_frame, corner_radius=10)
        # Ne pas l'afficher par défaut
        
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
        
        self.phone_column = ctk.StringVar()
        self.phone_column.trace_add('write', self.on_config_change)
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
        
        self.selected_image = ctk.StringVar()
        self.selected_image.trace_add('write', self.on_config_change)
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
        self.include_excel_data = ctk.BooleanVar(value=True)
        self.include_excel_data.trace_add('write', self.on_config_change)
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
        
        send_btn = ctk.CTkButton(buttons_frame, text="📨 Envoyer", command=self.send_whatsapp_data, height=35, width=100, font=ctk.CTkFont(size=11, weight="bold"))
        send_btn.pack(side='left')
        
        # Conteneur pour les colonnes
        self.columns_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.columns_container.pack(fill='both', expand=True, padx=30, pady=(10, 20))
        
        # Frame pour la sélection des colonnes
        self.columns_frame = ctk.CTkFrame(self.columns_container, corner_radius=15)
        self.columns_frame.pack(fill='both', expand=True)
        
        # Configuration de la section colonnes
        columns_label = ctk.CTkLabel(
            self.columns_frame, 
            text="📋 Sélectionner les colonnes à afficher:", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        columns_label.pack(anchor='w', padx=20, pady=(20, 10))
        
        # Frame avec scrollbar pour les colonnes
        columns_scroll_frame = ctk.CTkScrollableFrame(
            self.columns_frame, 
            height=200,
            corner_radius=10
        )
        columns_scroll_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.scrollable_columns_frame = columns_scroll_frame
        
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
        self.data_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.data_frame.pack(pady=20, padx=30, fill='both', expand=True)
        
        data_label = ctk.CTkLabel(
            self.data_frame, 
            text="📊 Données sélectionnées:", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        data_label.pack(anchor='w', padx=20, pady=(20, 10))
        
        # Masquer seulement data_frame au début
        self.data_frame.pack_forget()
    
    def toggle_api_section(self):
        """Basculer l'affichage de la section API"""
        if self.api_visible.get():
            # Masquer la section API
            self.api_section.pack_forget()
            self.api_toggle_btn.configure(text="📱 Configuration UltraMsg API  ▶")
            self.api_visible.set(False)
        else:
            # Afficher la section API
            self.api_section.pack(fill='x', padx=20, pady=(5, 15))
            self.api_toggle_btn.configure(text="📱 Configuration UltraMsg API  ▼")
            self.api_visible.set(True)
        
        # Sauvegarder l'état
        self.save_config()
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Sélectionner un fichier Excel",
            filetypes=[("Fichiers Excel", "*.xlsx *.xls"), ("Tous les fichiers", "*.*")]
        )
        if filename:
            self.selected_file.set(filename)
    
    def browse_image(self):
        filename = filedialog.askopenfilename(
            title="Sélectionner une image",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("GIF", "*.gif"),
                ("Tous les fichiers", "*.*")
            ]
        )
        if filename:
            self.selected_image.set(filename)
    
    def load_file(self):
        if not self.selected_file.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier Excel.")
            return
        
        try:
            self.df = pd.read_excel(self.selected_file.get())
            self.create_column_checkboxes()
            self.update_phone_column_options()
            # main_container est déjà visible - pas besoin de le réafficher
            messagebox.showinfo("Succès", f"Fichier chargé avec succès!\\n{len(self.df)} lignes et {len(self.df.columns)} colonnes trouvées.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement du fichier:\\n{str(e)}")
    
    def create_column_checkboxes(self):
        for widget in self.scrollable_columns_frame.winfo_children():
            widget.destroy()
        
        self.column_vars.clear()
        
        # Créer un frame pour organiser les checkboxes en colonnes
        checkboxes_container = ctk.CTkFrame(self.scrollable_columns_frame, fg_color="transparent")
        checkboxes_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Créer les colonnes
        left_column = ctk.CTkFrame(checkboxes_container, fg_color="transparent")
        right_column = ctk.CTkFrame(checkboxes_container, fg_color="transparent")
        
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 5))
        right_column.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        for i, column in enumerate(self.df.columns):
            var = ctk.BooleanVar(value=True)
            self.column_vars[column] = var
            
            # Alterner entre les colonnes gauche et droite
            parent_frame = left_column if i % 2 == 0 else right_column
            
            cb = ctk.CTkCheckBox(
                parent_frame,
                text=f"{column} ({self.df[column].dtype})",
                variable=var,
                font=ctk.CTkFont(size=11)
            )
            cb.pack(anchor='w', padx=10, pady=3)
    
    def update_phone_column_options(self):
        """Mettre à jour les options de colonnes pour les numéros de téléphone"""
        if self.df is not None:
            columns = list(self.df.columns)
            self.phone_column_combo.configure(values=columns)
            if columns:
                self.phone_column_combo.set(columns[0])  # Sélectionner la première colonne par défaut
    
    def select_all_columns(self):
        for var in self.column_vars.values():
            var.set(True)
    
    def deselect_all_columns(self):
        for var in self.column_vars.values():
            var.set(False)
    
    def show_selected_data(self):
        if self.df is None:
            messagebox.showerror("Erreur", "Aucun fichier chargé.")
            return
        
        selected_columns = [col for col, var in self.column_vars.items() if var.get()]
        
        if not selected_columns:
            messagebox.showwarning("Attention", "Veuillez sélectionner au moins une colonne.")
            return
        
        self.display_data(selected_columns)
    
    def display_data(self, columns):
        # Nettoyer complètement la frame de données
        for widget in self.data_frame.winfo_children():
            widget.destroy()
        
        # Créer le label une seule fois
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
        style.configure("Treeview", 
                       background="#2b2b2b",
                       foreground="white",
                       rowheight=25,
                       fieldbackground="#2b2b2b")
        style.configure("Treeview.Heading",
                       background="#1f538d",
                       foreground="white",
                       relief="flat")
        style.map("Treeview",
                 background=[('selected', '#144870')])
        
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
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
        
        # Info sur les données avec style moderne
        info_label = ctk.CTkLabel(
            self.data_frame,
            text=f"📈 Affichage de {len(data_to_show)} lignes sur {len(self.df)} (limité à 1000 pour la performance)",
            font=ctk.CTkFont(size=11)
        )
        info_label.pack(pady=(10, 20))
        
        # Afficher data_frame en bas sans masquer la section API
        self.data_frame.pack(pady=(10, 20), padx=30, fill='both', expand=False)
    
    def test_api_with_message(self):
        """Tester l'API en envoyant un message test au premier numéro de la colonne"""
        if not self.instance_id.get() or not self.token.get():
            messagebox.showerror("Erreur", "Veuillez remplir l'Instance ID et le Token.")
            return
        
        if self.df is None or not self.phone_column.get():
            messagebox.showerror("Erreur", "Veuillez charger un fichier Excel et sélectionner une colonne de numéros.")
            return
        
        # Prendre le premier numéro de la colonne pour le test
        phone_column_name = self.phone_column.get()
        if phone_column_name not in self.df.columns:
            messagebox.showerror("Erreur", "La colonne sélectionnée n'existe pas.")
            return
        
        first_phone = str(self.df[phone_column_name].iloc[0]).strip()
        if not first_phone or first_phone == 'nan':
            messagebox.showerror("Erreur", "Le premier numéro de la colonne est vide.")
            return
        
        try:
            # Message de test
            test_message = "🧪 Test API UltraMsg - Si vous recevez ce message, votre API fonctionne parfaitement !"
            
            # Tester avec image si sélectionnée, sinon message texte
            if self.selected_image.get() and os.path.exists(self.selected_image.get()):
                success = self.send_image_message(first_phone, test_message)
                if success:
                    self.connection_status.configure(text="🟢 Status: API fonctionnelle ✅")
                    messagebox.showinfo("✅ Test réussi !", 
                                      f"Image test envoyée avec succès !\\n"
                                      f"Vérifiez WhatsApp sur {first_phone}")
                else:
                    self.connection_status.configure(text="🔴 Status: Échec d'envoi")
                    messagebox.showerror("❌ Test échoué", "Échec d'envoi de l'image")
                return
            
            # Envoyer le message texte de test
            url = f"https://api.ultramsg.com/{self.instance_id.get()}/messages/chat"
            
            payload = {
                'token': self.token.get(),
                'to': first_phone,
                'body': test_message
            }
            
            response = requests.post(url, data=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('sent'):
                    self.connection_status.configure(text="🟢 Status: API fonctionnelle ✅")
                    messagebox.showinfo("✅ Test réussi !", 
                                      f"Message test envoyé avec succès !\\n"
                                      f"Vérifiez WhatsApp sur {first_phone}")
                else:
                    self.connection_status.configure(text="🔴 Status: Échec d'envoi")
                    error_msg = result.get('message', 'Erreur inconnue')
                    messagebox.showerror("❌ Test échoué", f"Échec d'envoi: {error_msg}")
            else:
                self.connection_status.configure(text="🔴 Status: Erreur API")
                messagebox.showerror("❌ Test échoué", f"Erreur API: {response.status_code}\\n{response.text}")
                
        except requests.exceptions.RequestException as e:
            self.connection_status.configure(text="🔴 Status: Erreur de connexion")
            messagebox.showerror("❌ Test échoué", f"Erreur de connexion: {str(e)}")
    
    def send_whatsapp_data(self):
        """Envoyer le message à tous les numéros de la colonne sélectionnée"""
        if not self.instance_id.get() or not self.token.get():
            messagebox.showerror("Erreur", "Veuillez configurer l'API UltraMsg d'abord.")
            return
        
        if self.df is None:
            messagebox.showerror("Erreur", "Veuillez charger un fichier Excel d'abord.")
            return
        
        if not self.phone_column.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner une colonne de numéros de téléphone.")
            return
        
        # Récupérer les colonnes sélectionnées pour les données
        selected_columns = []
        if self.include_excel_data.get():
            selected_columns = [col for col, var in self.column_vars.items() if var.get()]
            if not selected_columns:
                messagebox.showwarning("Attention", "Veuillez sélectionner au moins une colonne de données ou décocher 'Inclure les données Excel'.")
                return
        
        # Confirmation avant envoi massif
        phone_column_name = self.phone_column.get()
        phone_numbers = self.df[phone_column_name].dropna().astype(str).str.strip()
        valid_numbers = phone_numbers[phone_numbers != ''].tolist()
        
        if not valid_numbers:
            messagebox.showerror("Erreur", "Aucun numéro de téléphone valide trouvé dans la colonne sélectionnée.")
            return
        
        # Demander confirmation
        confirm = messagebox.askyesno(
            "Confirmation d'envoi massif", 
            f"Vous allez envoyer le message à {len(valid_numbers)} numéros.\\n"
            f"Êtes-vous sûr de vouloir continuer ?\\n\\n"
            f"Premiers numéros: {', '.join(valid_numbers[:3])}{'...' if len(valid_numbers) > 3 else ''}"
        )
        
        if not confirm:
            return
        
        try:
            # Récupérer le message personnalisé de l'utilisateur
            user_message = self.user_message.get("0.0", "end-1c").strip()
            
            # Variables pour le suivi
            sent_count = 0
            failed_count = 0
            failed_numbers = []
            
            # Barre de progression (simulation avec print pour l'instant)
            total_numbers = len(valid_numbers)
            
            for i, phone_number in enumerate(valid_numbers, 1):
                try:
                    # Construire le message pour ce destinataire
                    if self.include_excel_data.get() and selected_columns:
                        # Récupérer les données pour cette ligne
                        row_data = self.df[self.df[phone_column_name].astype(str).str.strip() == phone_number]
                        if not row_data.empty:
                            row_data_selected = row_data[selected_columns].iloc[0]
                            data_text = "\\n".join([f"{col}: {val}" for col, val in row_data_selected.items()])
                            message = f"{user_message}"
                        else:
                            message = user_message
                    else:
                        message = user_message
                    
                    # Limiter la longueur du message
                    if len(message) > 4000:
                        message = message[:3900] + "...\\n\\n[Message tronqué]"
                    
                    # Envoyer le message (texte ou image)
                    if self.selected_image.get() and os.path.exists(self.selected_image.get()):
                        # Envoyer une image
                        success = self.send_image_message(phone_number, message)
                        if success:
                            sent_count += 1
                        else:
                            failed_count += 1
                            failed_numbers.append(f"{phone_number}: Erreur envoi image")
                        continue
                    else:
                        # Envoyer un message texte
                        url = f"https://api.ultramsg.com/{self.instance_id.get()}/messages/chat"
                        payload = {
                            'token': self.token.get(),
                            'to': phone_number,
                            'body': message
                        }
                        
                        response = requests.post(url, data=payload, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('sent'):
                            sent_count += 1
                        else:
                            failed_count += 1
                            failed_numbers.append(f"{phone_number}: {result.get('message', 'Erreur inconnue')}")
                    else:
                        failed_count += 1
                        failed_numbers.append(f"{phone_number}: Erreur API {response.status_code}")
                    
                    # Petite pause entre les envois pour éviter le spam
                    import time
                    time.sleep(1)
                    
                    # Mise à jour du status (optionnel)
                    self.connection_status.configure(text=f"📤 Envoi: {i}/{total_numbers}")
                    self.root.update()
                    
                except Exception as e:
                    failed_count += 1
                    failed_numbers.append(f"{phone_number}: {str(e)}")
            
            # Rapport final
            report = f"📊 Rapport d'envoi:\\n"
            report += f"✅ Envoyés avec succès: {sent_count}\\n"
            report += f"❌ Échecs: {failed_count}\\n"
            
            if failed_numbers:
                report += f"\\nÉchecs détaillés (premiers 5):\\n"
                for failure in failed_numbers[:5]:
                    report += f"• {failure}\\n"
                
                if len(failed_numbers) > 5:
                    report += f"... et {len(failed_numbers) - 5} autres échecs"
            
            self.connection_status.configure(text="✅ Envoi terminé")
            
            if failed_count == 0:
                messagebox.showinfo("🎉 Envoi réussi!", report)
            else:
                messagebox.showwarning("⚠️ Envoi terminé avec erreurs", report)
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'envoi massif: {str(e)}")
    
    def send_image_message(self, phone_number, caption=""):
        """Envoyer une image via WhatsApp avec une légende optionnelle"""
        try:
            image_path = self.selected_image.get()
            
            # Vérifier que le fichier existe
            if not os.path.exists(image_path):
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
            
            # Préparer l'URL et les données
            url = f"https://api.ultramsg.com/{self.instance_id.get()}/messages/image"
            
            payload = {
                'token': self.token.get(),
                'to': phone_number,
                'image': f"data:{mime_type};base64,{image_base64}",
                'caption': caption if caption else ""
            }
            
            # Envoyer l'image
            response = requests.post(url, data=payload, timeout=60)  # Timeout plus long pour les images
            
            if response.status_code == 200:
                result = response.json()
                return result.get('sent', False)
            else:
                return False
                
        except Exception as e:
            print(f"Erreur envoi image: {str(e)}")
            return False
    
    def save_config(self):
        """Sauvegarder la configuration dans un fichier JSON"""
        try:
            config = {
                'instance_id': self.instance_id.get(),
                'token': self.token.get(),
                'phone_column': self.phone_column.get() if hasattr(self, 'phone_column') else '',
                'selected_image': self.selected_image.get() if hasattr(self, 'selected_image') else '',
                'user_message': self.user_message.get("0.0", "end-1c") if hasattr(self, 'user_message') else '',
                'include_excel_data': self.include_excel_data.get() if hasattr(self, 'include_excel_data') else True,
                'api_visible': self.api_visible.get() if hasattr(self, 'api_visible') else False
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"Erreur sauvegarde config: {str(e)}")
    
    def load_config(self):
        """Charger la configuration depuis le fichier JSON"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Restaurer les valeurs
                self.instance_id.set(config.get('instance_id', ''))
                self.token.set(config.get('token', ''))
                
                if hasattr(self, 'phone_column') and config.get('phone_column'):
                    self.phone_column.set(config.get('phone_column', ''))
                
                if hasattr(self, 'selected_image'):
                    self.selected_image.set(config.get('selected_image', ''))
                
                if hasattr(self, 'user_message') and config.get('user_message'):
                    self.user_message.delete("0.0", "end")
                    self.user_message.insert("0.0", config.get('user_message', ''))
                
                if hasattr(self, 'include_excel_data'):
                    self.include_excel_data.set(config.get('include_excel_data', True))
                
                if hasattr(self, 'api_visible'):
                    api_visible = config.get('api_visible', False)
                    self.api_visible.set(api_visible)
                    if api_visible:
                        self.api_section.pack(fill='x', padx=20, pady=(5, 15))
                        self.api_toggle_btn.configure(text="📱 Configuration UltraMsg API  ▼")
                
        except Exception as e:
            print(f"Erreur chargement config: {str(e)}")
    
    def on_config_change(self, *args):
        """Sauvegarder automatiquement quand la configuration change"""
        self.save_config()
    
    def on_closing(self):
        """Sauvegarder la configuration avant de fermer l'application"""
        self.save_config()
        self.root.destroy()

def main():
    root = ctk.CTk()
    app = ExcelReaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()