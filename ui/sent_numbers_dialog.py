# -*- coding: utf-8 -*-
"""
Dialog de gestion des numéros envoyés - Historique, Export, Suppression
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import json
from pathlib import Path
from typing import List, Set
import pandas as pd
from datetime import datetime
import threading
import time

from utils.logger import logger


class SentNumbersDialog(ctk.CTkToplevel):
    """Dialog pour gérer les numéros déjà envoyés"""
    
    def __init__(self, parent, bulk_sender):
        super().__init__(parent)
        
        self.bulk_sender = bulk_sender
        self.sent_numbers_count = bulk_sender.get_sent_numbers_count()
        
        # Configuration de la fenêtre
        self.title("📚 Gestion des Numéros Contactés")
        self.geometry("600x700")
        self.resizable(True, True)
        
        # Centrer la fenêtre
        self.transient(parent)
        self.grab_set()
        
        # Variables d'état
        self.all_numbers = []
        
        self.create_widgets()
        self.load_numbers()
        
        # Focus sur la fenêtre
        self.focus()
    
    def create_widgets(self):
        """Crée l'interface du dialog"""
        
        # Header avec statistiques
        header_frame = ctk.CTkFrame(self, corner_radius=10)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📚 Historique des Numéros Contactés",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 5))
        
        # Statistiques
        stats_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        stats_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text=f"📊 Total: {self.sent_numbers_count} numéros contactés",
            font=ctk.CTkFont(size=14)
        )
        self.stats_label.pack()
        
        # Recherche
        search_frame = ctk.CTkFrame(self, corner_radius=10)
        search_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="🔍 Rechercher un numéro:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        search_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        search_input_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_input_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_input_frame,
            placeholder_text="Tapez un numéro pour rechercher...",
            height=35
        )
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        search_btn = ctk.CTkButton(
            search_input_frame,
            text="🔍",
            command=self.search_numbers,
            height=35,
            width=40
        )
        search_btn.pack(side='right')
        
        # Zone d'affichage des numéros
        content_frame = ctk.CTkFrame(self, corner_radius=10)
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        content_label = ctk.CTkLabel(
            content_frame,
            text="📋 Liste des numéros:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        content_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        # Zone de texte scrollable
        self.numbers_textbox = ctk.CTkTextbox(
            content_frame,
            height=300,
            font=ctk.CTkFont(family="Courier", size=11)
        )
        self.numbers_textbox.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Boutons d'action
        actions_frame = ctk.CTkFrame(self, corner_radius=10)
        actions_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        actions_label = ctk.CTkLabel(
            actions_frame,
            text="⚙️ Actions:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        actions_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        # Ligne de boutons
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Bouton Actualiser
        refresh_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 Actualiser",
            command=self.refresh_data,
            height=35,
            width=120,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        refresh_btn.pack(side='left', padx=(0, 5))
        
        # Bouton Export Excel
        export_excel_btn = ctk.CTkButton(
            buttons_frame,
            text="📊 Export Excel",
            command=self.export_to_excel,
            height=35,
            width=120,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#2E8B57", "#228B22")
        )
        export_excel_btn.pack(side='left', padx=(0, 5))
        
        # Bouton Export JSON
        export_json_btn = ctk.CTkButton(
            buttons_frame,
            text="📄 Export JSON",
            command=self.export_to_json,
            height=35,
            width=120,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#4682B4", "#1E90FF")
        )
        export_json_btn.pack(side='left', padx=(0, 5))
        
        # Bouton Supprimer
        delete_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Supprimer",
            command=self.confirm_delete_all,
            height=35,
            width=120,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#DC143C", "#B22222")
        )
        delete_btn.pack(side='right')
        
        # Bouton Fermer
        close_frame = ctk.CTkFrame(self, fg_color="transparent")
        close_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        close_btn = ctk.CTkButton(
            close_frame,
            text="❌ Fermer",
            command=self.destroy,
            height=35,
            width=100,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        close_btn.pack(side='right')
    
    def load_numbers(self):
        """Charge et affiche les numéros"""
        try:
            # Récupérer les numéros du bulk_sender
            sent_numbers = list(self.bulk_sender.sent_numbers)
            
            if not sent_numbers:
                self.numbers_textbox.delete("1.0", "end")
                self.numbers_textbox.insert("1.0", "Aucun numéro contacté pour le moment.\n\n💡 Les numéros apparaîtront ici après le premier envoi.")
                return
            
            # Trier les numéros
            sent_numbers.sort()
            
            # Afficher dans le textbox
            self.numbers_textbox.delete("1.0", "end")
            
            content = f"📋 {len(sent_numbers)} numéros contactés:\\n\\n"
            
            for i, number in enumerate(sent_numbers, 1):
                content += f"{i:4d}. {number}\\n"
            
            self.numbers_textbox.insert("1.0", content)
            
            # Mettre à jour les stats
            self.stats_label.configure(text=f"📊 Total: {len(sent_numbers)} numéros contactés")
            self.sent_numbers_count = len(sent_numbers)
            
        except Exception as e:
            logger.error("load_numbers_error", error=str(e))
            self.numbers_textbox.delete("1.0", "end")
            self.numbers_textbox.insert("1.0", f"❌ Erreur lors du chargement: {str(e)}")
    
    def search_numbers(self):
        """Filtre les numéros selon la recherche"""
        search_text = self.search_entry.get().strip().lower()
        
        if not search_text:
            self.load_numbers()
            return
        
        try:
            sent_numbers = list(self.bulk_sender.sent_numbers)
            
            # Filtrer les numéros
            filtered_numbers = [num for num in sent_numbers if search_text in num.lower()]
            
            # Afficher les résultats filtrés
            self.numbers_textbox.delete("1.0", "end")
            
            if not filtered_numbers:
                self.numbers_textbox.insert("1.0", f"🔍 Aucun résultat pour '{search_text}'")
                return
            
            filtered_numbers.sort()
            content = f"🔍 {len(filtered_numbers)} résultat(s) pour '{search_text}':\\n\\n"
            
            for i, number in enumerate(filtered_numbers, 1):
                content += f"{i:4d}. {number}\\n"
            
            self.numbers_textbox.insert("1.0", content)
            
        except Exception as e:
            logger.error("search_numbers_error", error=str(e))
    
    def refresh_data(self):
        """Actualise les données"""
        # Recharger les numéros depuis le fichier
        self.bulk_sender._load_sent_numbers()
        self.load_numbers()
        messagebox.showinfo("✅ Actualisation", "Les données ont été actualisées avec succès!")
    
    def export_to_excel(self):
        """Exporte les numéros vers Excel"""
        try:
            sent_numbers = list(self.bulk_sender.sent_numbers)
            
            if not sent_numbers:
                messagebox.showwarning("⚠️ Aucune donnée", "Aucun numéro à exporter.")
                return
            
            # Demander le fichier de destination
            file_path = filedialog.asksaveasfilename(
                title="Exporter vers Excel",
                defaultextension=".xlsx",
                filetypes=[
                    ("Fichiers Excel", "*.xlsx"),
                    ("Tous les fichiers", "*.*")
                ],
                initialname=f"numeros_contactes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if not file_path:
                return
            
            # Créer le DataFrame
            df = pd.DataFrame({
                'Numéro': sorted(sent_numbers),
                'Date_Export': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # Ajouter un index commençant à 1
            df.index = range(1, len(df) + 1)
            
            # Exporter
            df.to_excel(file_path, index_label='ID')
            
            messagebox.showinfo(
                "✅ Export réussi", 
                f"Export Excel réussi!\\n\\n📁 Fichier: {Path(file_path).name}\\n📊 {len(sent_numbers)} numéros exportés"
            )
            
            logger.info("excel_export_success", file=file_path, count=len(sent_numbers))
            
        except Exception as e:
            error_msg = f"Erreur lors de l'export Excel: {str(e)}"
            logger.error("excel_export_error", error=str(e))
            messagebox.showerror("❌ Erreur d'export", error_msg)
    
    def export_to_json(self):
        """Exporte les numéros vers JSON"""
        try:
            sent_numbers = list(self.bulk_sender.sent_numbers)
            
            if not sent_numbers:
                messagebox.showwarning("⚠️ Aucune donnée", "Aucun numéro à exporter.")
                return
            
            # Demander le fichier de destination
            file_path = filedialog.asksaveasfilename(
                title="Exporter vers JSON",
                defaultextension=".json",
                filetypes=[
                    ("Fichiers JSON", "*.json"),
                    ("Tous les fichiers", "*.*")
                ],
                initialname=f"numeros_contactes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            if not file_path:
                return
            
            # Créer les données JSON
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'total_count': len(sent_numbers),
                'sent_numbers': sorted(sent_numbers),
                'export_info': {
                    'application': 'Excel vers WhatsApp Pro',
                    'version': '2.2'
                }
            }
            
            # Exporter
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo(
                "✅ Export réussi", 
                f"Export JSON réussi!\\n\\n📁 Fichier: {Path(file_path).name}\\n📊 {len(sent_numbers)} numéros exportés"
            )
            
            logger.info("json_export_success", file=file_path, count=len(sent_numbers))
            
        except Exception as e:
            error_msg = f"Erreur lors de l'export JSON: {str(e)}"
            logger.error("json_export_error", error=str(e))
            messagebox.showerror("❌ Erreur d'export", error_msg)
    
    def confirm_delete_all(self):
        """Demande confirmation avant suppression"""
        if self.sent_numbers_count == 0:
            messagebox.showinfo("ℹ️ Information", "Aucun numéro à supprimer.")
            return
        
        confirm_msg = (
            f"🗑️ Confirmation de suppression\\n\\n"
            f"⚠️ Cette action est IRRÉVERSIBLE!\\n\\n"
            f"📊 Numéros à supprimer: {self.sent_numbers_count}\\n"
            f"📁 Fichier: sent_numbers.json\\n\\n"
            f"Êtes-vous sûr de vouloir supprimer TOUS les numéros contactés?"
        )
        
        if messagebox.askyesno("🗑️ Confirmer la suppression", confirm_msg):
            self.delete_all_numbers()
    
    def delete_all_numbers(self):
        """Supprime tous les numéros"""
        try:
            # Supprimer via le bulk_sender
            self.bulk_sender.clear_sent_numbers()
            
            # Actualiser l'affichage
            self.load_numbers()
            
            messagebox.showinfo(
                "✅ Suppression réussie",
                f"Tous les numéros ont été supprimés avec succès!\\n\\n"
                f"📊 {self.sent_numbers_count} numéros supprimés\\n"
                f"📁 Fichier sent_numbers.json vidé"
            )
            
            logger.info("all_sent_numbers_deleted", count=self.sent_numbers_count)
            self.sent_numbers_count = 0
            
        except Exception as e:
            error_msg = f"Erreur lors de la suppression: {str(e)}"
            logger.error("delete_numbers_error", error=str(e))
            messagebox.showerror("❌ Erreur de suppression", error_msg)