# -*- coding: utf-8 -*-
"""
Composants UI réutilisables
"""
import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from typing import Callable, Optional, List, Dict, Any
import time
from utils.logger import logger
from ui.progress_widgets import SimpleProgressOverlay, AnimatedProgressBar
from ui.progress_widgets import SimpleProgressOverlay, AnimatedProgressBar


class StatusIndicator(ctk.CTkLabel):
    """Indicateur de statut avec couleurs"""
    
    STATUS_COLORS = {
        'success': '#28a745',
        'error': '#dc3545', 
        'warning': '#ffc107',
        'info': '#17a2b8',
        'default': '#6c757d'
    }
    
    STATUS_ICONS = {
        'success': '🟢',
        'error': '🔴',
        'warning': '🟡',
        'info': '🔵',
        'default': '⚪'
    }
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.set_status('default', 'Prêt')
    
    def set_status(self, status_type: str, message: str):
        """Met à jour le statut"""
        icon = self.STATUS_ICONS.get(status_type, self.STATUS_ICONS['default'])
        color = self.STATUS_COLORS.get(status_type, self.STATUS_COLORS['default'])
        
        self.configure(
            text=f"{icon} {message}",
            text_color=color
        )


class ProgressFrame(ctk.CTkFrame):
    """Frame avec barre de progression animée et statistiques"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Label de statut principal
        self.progress_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.progress_label.pack(pady=(15, 5))
        
        # Barre de progression animée
        self.progress_bar = AnimatedProgressBar(
            self,
            height=20,
            corner_radius=10
        )
        self.progress_bar.pack(fill='x', padx=20, pady=5)
        self.progress_bar.set(0)
        
        # Statistiques rapides
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill='x', padx=20, pady=5)
        
        # Grid pour les stats
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Temps écoulé
        self.time_label = ctk.CTkLabel(
            stats_frame,
            text="⏱️ 00:00",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.time_label.grid(row=0, column=0, sticky="w")
        
        # Pourcentage
        self.percent_label = ctk.CTkLabel(
            stats_frame,
            text="0%",
            font=ctk.CTkFont(size=10, weight="bold")
        )
        self.percent_label.grid(row=0, column=1)
        
        # Débit
        self.rate_label = ctk.CTkLabel(
            stats_frame,
            text="🚀 0/sec",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.rate_label.grid(row=0, column=2, sticky="e")
        
        # Variables pour calculs
        self.start_time = None
        self.last_current = 0
        self.last_time = None
        
        self.pack_forget()  # Masquer par défaut
    
    def show(self, title: str = "Traitement en cours..."):
        """Affiche la barre de progression"""
        self.progress_label.configure(text=title)
        self.progress_bar.set(0)
        self.progress_bar.start_animation()
        self.start_time = time.time()
        self.last_time = self.start_time
        self.pack(fill='x', pady=10)
    
    def hide(self):
        """Masque la barre de progression"""
        self.progress_bar.stop_animation()
        self.pack_forget()
    
    def update(self, current: int, total: int, message: str = ""):
        """Met à jour la progression avec statistiques"""
        import time
        
        current_time = time.time()
        
        if total > 0:
            progress = current / total
            self.progress_bar.set(progress)
            
            # Pourcentage
            percentage = progress * 100
            self.percent_label.configure(text=f"{percentage:.1f}%")
            
            # Changer la couleur selon la progression
            if percentage >= 100:
                self.progress_bar.set_color_theme('success')
            elif percentage > 75:
                self.progress_bar.set_color_theme('info')
            elif percentage > 50:
                self.progress_bar.set_color_theme('default')
            
            # Temps écoulé
            if self.start_time:
                elapsed = current_time - self.start_time
                minutes = int(elapsed // 60)
                seconds = int(elapsed % 60)
                self.time_label.configure(text=f"⏱️ {minutes:02d}:{seconds:02d}")
            
            # Débit
            if self.last_time and current > self.last_current:
                time_diff = current_time - self.last_time
                if time_diff > 0:
                    rate = (current - self.last_current) / time_diff
                    self.rate_label.configure(text=f"🚀 {rate:.1f}/sec")
            
            self.last_current = current
            self.last_time = current_time
            
            # Message principal
            if message:
                text = f"{message} - {percentage:.1f}%"
            else:
                text = f"Progression: {current}/{total} ({percentage:.1f}%)"
            
            self.progress_label.configure(text=text)


class CollapsibleSection(ctk.CTkFrame):
    """Section repliable"""
    
    def __init__(self, parent, title: str, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.is_open = tk.BooleanVar(value=False)
        self.title = title
        
        # Header avec bouton toggle
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill='x', padx=10, pady=5)
        
        self.toggle_button = ctk.CTkButton(
            self.header,
            text=f"{title} ▶",
            command=self.toggle,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("gray75", "gray25"),
            hover_color=("gray65", "gray35"),
            anchor="w"
        )
        self.toggle_button.pack(fill='x')
        
        # Conteneur pour le contenu
        self.content_frame = ctk.CTkFrame(self)
        
        # Le contenu est masqué par défaut
    
    def toggle(self):
        """Basculer l'affichage du contenu"""
        if self.is_open.get():
            # Fermer
            self.content_frame.pack_forget()
            self.toggle_button.configure(text=f"{self.title} ▶")
            self.is_open.set(False)
        else:
            # Ouvrir
            self.content_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
            self.toggle_button.configure(text=f"{self.title} ▼")
            self.is_open.set(True)
    
    def get_content_frame(self) -> ctk.CTkFrame:
        """Retourne le frame pour ajouter du contenu"""
        return self.content_frame
    
    def set_open(self, is_open: bool):
        """Définit l'état ouvert/fermé"""
        if is_open != self.is_open.get():
            self.toggle()


class ValidatedEntry(ctk.CTkFrame):
    """Entry avec validation visuelle"""
    
    def __init__(self, parent, placeholder_text: str = "", validator: Optional[Callable] = None, **kwargs):
        super().__init__(parent, fg_color="transparent")
        
        self.validator = validator
        self.is_valid = True
        
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder_text,
            **kwargs
        )
        self.entry.pack(side='left', fill='x', expand=True)
        
        self.status_icon = ctk.CTkLabel(
            self,
            text="",
            width=30,
            font=ctk.CTkFont(size=16)
        )
        self.status_icon.pack(side='right', padx=(5, 0))
        
        # Bind validation sur changement
        self.entry.bind('<KeyRelease>', self._validate)
        self.entry.bind('<FocusOut>', self._validate)
    
    def _validate(self, event=None):
        """Valide la saisie"""
        if self.validator:
            value = self.entry.get()
            try:
                is_valid, message = self.validator(value)
                if is_valid:
                    self.status_icon.configure(text="✅", text_color="green")
                    self.is_valid = True
                else:
                    self.status_icon.configure(text="❌", text_color="red")
                    self.is_valid = False
            except Exception:
                self.status_icon.configure(text="❓", text_color="orange")
                self.is_valid = False
        else:
            self.status_icon.configure(text="")
            self.is_valid = True
    
    def get(self) -> str:
        """Récupère la valeur"""
        return self.entry.get()
    
    def set(self, value: str):
        """Définit la valeur"""
        self.entry.delete(0, 'end')
        self.entry.insert(0, value)
        self._validate()


class DataTable(ctk.CTkFrame):
    """Tableau de données avec style moderne"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, corner_radius=10, **kwargs)
        
        # Configuration du style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._setup_dark_theme()
        
        # Container pour le treeview et scrollbars
        self.tree_container = ctk.CTkFrame(self, fg_color="transparent")
        self.tree_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview
        self.tree = ttk.Treeview(self.tree_container, show='headings')
        
        # Scrollbars
        self.v_scrollbar = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.tree.yview)
        self.h_scrollbar = ttk.Scrollbar(self.tree_container, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # Placement
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.v_scrollbar.grid(row=0, column=1, sticky='ns')
        self.h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        self.tree_container.grid_rowconfigure(0, weight=1)
        self.tree_container.grid_columnconfigure(0, weight=1)
        
        # Info label
        self.info_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.info_label.pack(pady=(5, 10))
    
    def _setup_dark_theme(self):
        """Configure le thème sombre pour le tableau"""
        self.style.configure("Treeview",
                            background="#2b2b2b",
                            foreground="white",
                            rowheight=25,
                            fieldbackground="#2b2b2b")
        
        self.style.configure("Treeview.Heading",
                            background="#1f538d",
                            foreground="white",
                            relief="flat")
        
        self.style.map("Treeview",
                      background=[('selected', '#144870')])
    
    def load_data(self, data, columns: List[str], max_rows: int = 1000):
        """Charge les données dans le tableau"""
        # Nettoyer le tableau existant
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Configurer les colonnes
        self.tree['columns'] = columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, minwidth=100)
        
        # Ajouter les données (limitées)
        data_to_show = data.head(max_rows) if hasattr(data, 'head') else data[:max_rows]
        
        for _, row in data_to_show.iterrows() if hasattr(data_to_show, 'iterrows') else enumerate(data_to_show):
            values = [str(row[col]) for col in columns] if hasattr(row, '__getitem__') else list(row)
            self.tree.insert('', 'end', values=values)
        
        # Mettre à jour l'info
        total_rows = len(data) if hasattr(data, '__len__') else 0
        shown_rows = len(data_to_show) if hasattr(data_to_show, '__len__') else 0
        
        info_text = f"📊 Affichage de {shown_rows} lignes"
        if total_rows > max_rows:
            info_text += f" sur {total_rows} (limité pour la performance)"
        
        self.info_label.configure(text=info_text)


class MessageComposer(ctk.CTkFrame):
    """Composeur de message avec preview"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Label
        self.label = ctk.CTkLabel(
            self,
            text="✉️ Composer votre message:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.label.pack(anchor='w', padx=10, pady=(10, 5))
        
        # Zone de texte
        self.textbox = ctk.CTkTextbox(
            self,
            height=100,
            font=ctk.CTkFont(size=11),
            wrap="word"
        )
        self.textbox.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Définir un message par défaut
        self.textbox.insert("0.0", "Bonjour,\\n\\nJe vous envoie les informations demandées.\\n\\nCordialement.")
        
        # Stats du message
        self.stats_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.stats_label.pack(anchor='e', padx=10, pady=(0, 10))
        
        # Bind pour mettre à jour les stats
        self.textbox.bind('<KeyRelease>', self._update_stats)
        self._update_stats()
    
    def _update_stats(self, event=None):
        """Met à jour les statistiques du message"""
        message = self.get_message()
        char_count = len(message)
        word_count = len(message.split()) if message.strip() else 0
        
        self.stats_label.configure(text=f"{char_count} caractères, {word_count} mots")
    
    def get_message(self) -> str:
        """Récupère le message"""
        return self.textbox.get("0.0", "end-1c")
    
    def set_message(self, message: str):
        """Définit le message"""
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", message)
        self._update_stats()
    
    def clear(self):
        """Efface le message"""
        self.textbox.delete("0.0", "end")
        self._update_stats()