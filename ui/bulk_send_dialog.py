# -*- coding: utf-8 -*-
"""
Interface utilisateur optimisée pour l'envoi en masse de gros volumes
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import time
from typing import Optional, Callable, List, Dict
from api.bulk_sender import BulkSender, SendingSession
from utils.logger import logger


class BulkSendDialog(ctk.CTkToplevel):
    """Dialog optimisé pour l'envoi en masse de gros volumes"""
    
    def __init__(self, parent, bulk_sender: BulkSender, messages_data: List[tuple]):
        super().__init__(parent)
        
        self.bulk_sender = bulk_sender
        self.messages_data = messages_data
        self.sending_thread: Optional[threading.Thread] = None
        self.current_session: Optional[SendingSession] = None
        
        self.setup_dialog()
        self.create_widgets()
        
        # Variables d'état
        self.is_sending = False
        self.last_update_time = 0
        self.update_interval = 0.5  # Mettre à jour l'UI toutes les 0.5 secondes
        
        # Centrer la fenêtre
        self.center_window()
    
    def setup_dialog(self):
        """Configure la fenêtre de dialog"""
        self.title("📊 Envoi en Masse - Optimisé pour Gros Volumes")
        self.geometry("600x500")
        self.minsize(500, 400)
        
        # Rendre modal
        self.transient(self.master)
        self.grab_set()
        
        # Gestionnaire de fermeture
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Crée l'interface utilisateur"""
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Titre et informations
        title_label = ctk.CTkLabel(
            main_frame,
            text="🚀 Envoi en Masse Optimisé",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Informations sur l'envoi
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill='x', pady=(0, 20), padx=20)
        
        self.info_label = ctk.CTkLabel(
            info_frame,
            text=f"📊 Total: {len(self.messages_data)} messages\\n"
                 f"🎯 Mode: Batch processing optimisé\\n"
                 f"⚡ Threading: Gestion intelligente des ressources",
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        self.info_label.pack(pady=15, padx=15)
        
        # Configuration d'envoi
        config_frame = ctk.CTkFrame(main_frame)
        config_frame.pack(fill='x', pady=(0, 20), padx=20)
        
        config_title = ctk.CTkLabel(
            config_frame,
            text="⚙️ Configuration",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        config_title.pack(pady=(15, 10))
        
        # Taille des batches
        batch_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        batch_frame.pack(fill='x', padx=15, pady=5)
        
        ctk.CTkLabel(batch_frame, text="📦 Taille des batches:", width=150).pack(side='left')
        self.batch_size_var = tk.StringVar(value=str(self.bulk_sender.batch_size))
        batch_entry = ctk.CTkEntry(batch_frame, textvariable=self.batch_size_var, width=100)
        batch_entry.pack(side='left', padx=10)
        
        # Threads simultanés
        thread_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        thread_frame.pack(fill='x', padx=15, pady=5)
        
        ctk.CTkLabel(thread_frame, text="🧵 Threads max:", width=150).pack(side='left')
        self.thread_count_var = tk.StringVar(value=str(self.bulk_sender.max_workers))
        thread_entry = ctk.CTkEntry(thread_frame, textvariable=self.thread_count_var, width=100)
        thread_entry.pack(side='left', padx=10)
        
        # Délai entre batches
        delay_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        delay_frame.pack(fill='x', padx=15, pady=(5, 15))
        
        ctk.CTkLabel(delay_frame, text="⏱️ Délai batches (sec):", width=150).pack(side='left')
        self.batch_delay_var = tk.StringVar(value=str(self.bulk_sender.batch_delay))
        delay_entry = ctk.CTkEntry(delay_frame, textvariable=self.batch_delay_var, width=100)
        delay_entry.pack(side='left', padx=10)
        
        # Section progression
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill='both', expand=True, pady=(0, 20), padx=20)
        
        progress_title = ctk.CTkLabel(
            progress_frame,
            text="📈 Progression",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        progress_title.pack(pady=(15, 10))
        
        # Barre de progression principale
        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=20)
        self.progress_bar.pack(fill='x', padx=15, pady=5)
        self.progress_bar.set(0)
        
        # Labels de statut
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="En attente de démarrage...",
            font=ctk.CTkFont(size=11)
        )
        self.progress_label.pack(pady=5)
        
        self.stats_label = ctk.CTkLabel(
            progress_frame,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.stats_label.pack(pady=(0, 15))
        
        # Boutons de contrôle
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill='x', pady=(0, 20))
        
        self.start_btn = ctk.CTkButton(
            button_frame,
            text="🚀 Démarrer l'envoi",
            command=self.start_sending,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#1f538d", "#14375e")
        )
        self.start_btn.pack(side='left', padx=10, expand=True, fill='x')
        
        self.pause_btn = ctk.CTkButton(
            button_frame,
            text="⏸️ Pause",
            command=self.toggle_pause,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            state="disabled",
            fg_color=("#f39c12", "#d68910")
        )
        self.pause_btn.pack(side='left', padx=10, expand=True, fill='x')
        
        self.stop_btn = ctk.CTkButton(
            button_frame,
            text="🛑 Arrêter",
            command=self.stop_sending,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            state="disabled",
            fg_color=("#e74c3c", "#c0392b")
        )
        self.stop_btn.pack(side='left', padx=10, expand=True, fill='x')
        
        # Bouton fermer
        close_btn = ctk.CTkButton(
            main_frame,
            text="❌ Fermer",
            command=self.on_closing,
            height=35,
            width=100,
            font=ctk.CTkFont(size=11)
        )
        close_btn.pack(pady=(0, 10))
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def start_sending(self):
        """Démarre l'envoi en masse"""
        if self.is_sending:
            return
        
        try:
            # Appliquer la configuration
            self.apply_configuration()
            
            # Réinitialiser l'état
            self.is_sending = True
            self.current_session = None
            
            # Mettre à jour l'interface
            self.start_btn.configure(state="disabled")
            self.pause_btn.configure(state="normal")
            self.stop_btn.configure(state="normal")
            
            # Démarrer l'envoi dans un thread séparé
            self.sending_thread = threading.Thread(
                target=self._send_messages_thread,
                daemon=True
            )
            self.sending_thread.start()
            
            logger.info("bulk_send_dialog_started", total_messages=len(self.messages_data))
            
        except Exception as e:
            self.handle_error(f"Erreur lors du démarrage: {str(e)}")
    
    def apply_configuration(self):
        """Applique la configuration saisie"""
        try:
            self.bulk_sender.batch_size = int(self.batch_size_var.get())
            self.bulk_sender.max_workers = int(self.thread_count_var.get())
            self.bulk_sender.batch_delay = float(self.batch_delay_var.get())
            
            # Validation des valeurs
            if self.bulk_sender.batch_size < 1 or self.bulk_sender.batch_size > 200:
                raise ValueError("La taille des batches doit être entre 1 et 200")
            
            if self.bulk_sender.max_workers < 1 or self.bulk_sender.max_workers > 10:
                raise ValueError("Le nombre de threads doit être entre 1 et 10")
            
            if self.bulk_sender.batch_delay < 0 or self.bulk_sender.batch_delay > 30:
                raise ValueError("Le délai doit être entre 0 et 30 secondes")
                
        except ValueError as e:
            raise ValueError(f"Configuration invalide: {str(e)}")
    
    def _send_messages_thread(self):
        """Thread d'envoi des messages"""
        try:
            session = self.bulk_sender.send_bulk_optimized(
                self.messages_data,
                progress_callback=self.update_progress,
                status_callback=self.update_status
            )
            
            self.current_session = session
            
            # Finaliser dans le thread principal
            self.after(0, self.sending_completed)
            
        except Exception as e:
            logger.error("bulk_send_thread_error", error=str(e))
            self.after(0, lambda: self.handle_error(f"Erreur d'envoi: {str(e)}"))
    
    def update_progress(self, completed: int, total: int, status: str):
        """Met à jour la progression (appelé depuis le thread d'envoi)"""
        current_time = time.time()
        
        # Limiter la fréquence des mises à jour de l'UI
        if current_time - self.last_update_time < self.update_interval:
            return
        
        self.last_update_time = current_time
        
        # Programmer la mise à jour dans le thread principal
        self.after(0, lambda: self._update_progress_ui(completed, total, status))
    
    def _update_progress_ui(self, completed: int, total: int, status: str):
        """Met à jour l'interface de progression"""
        try:
            # Barre de progression
            progress = completed / total if total > 0 else 0
            self.progress_bar.set(progress)
            
            # Label principal
            percentage = progress * 100
            self.progress_label.configure(text=f"{status} - {percentage:.1f}%")
            
            # Statistiques détaillées
            if self.current_session:
                stats = self.bulk_sender.get_session_stats(self.current_session)
                if stats:
                    rate = stats.get('messages_per_second', 0)
                    eta = stats.get('estimated_time_remaining', 0)
                    
                    eta_str = self._format_time(eta) if eta > 0 else "Calcul..."
                    
                    stats_text = (
                        f"✅ Réussis: {stats.get('successful', 0)} | "
                        f"❌ Échecs: {stats.get('failed', 0)} | "
                        f"🚀 {rate:.1f} msg/sec | "
                        f"⏱️ Restant: {eta_str}"
                    )
                    self.stats_label.configure(text=stats_text)
            
        except Exception as e:
            logger.error("progress_update_error", error=str(e))
    
    def update_status(self, message: str):
        """Met à jour le statut (appelé depuis le thread d'envoi)"""
        self.after(0, lambda: self.progress_label.configure(text=message))
    
    def toggle_pause(self):
        """Bascule entre pause et reprise"""
        if not self.is_sending:
            return
        
        if self.bulk_sender.is_paused:
            self.bulk_sender.resume_sending()
            self.pause_btn.configure(text="⏸️ Pause")
            logger.info("bulk_send_resumed_from_dialog")
        else:
            self.bulk_sender.pause_sending()
            self.pause_btn.configure(text="▶️ Reprendre")
            logger.info("bulk_send_paused_from_dialog")
    
    def stop_sending(self):
        """Arrête l'envoi en cours"""
        if not self.is_sending:
            return
        
        # Demander confirmation
        confirm = messagebox.askyesno(
            "Confirmer l'arrêt",
            "Êtes-vous sûr de vouloir arrêter l'envoi en cours ?\\n\\n"
            "Les messages non encore envoyés seront annulés."
        )
        
        if confirm:
            self.bulk_sender.cancel_sending()
            logger.info("bulk_send_cancelled_from_dialog")
    
    def sending_completed(self):
        """Appelé quand l'envoi est terminé"""
        try:
            self.is_sending = False
            
            # Mettre à jour l'interface
            self.start_btn.configure(state="normal", text="🔄 Nouvel envoi")
            self.pause_btn.configure(state="disabled")
            self.stop_btn.configure(state="disabled")
            
            if self.current_session:
                stats = self.bulk_sender.get_session_stats(self.current_session)
                
                if self.current_session.cancelled:
                    self.progress_label.configure(text="🛑 Envoi annulé")
                    messagebox.showwarning(
                        "Envoi annulé",
                        f"L'envoi a été annulé.\\n\\n"
                        f"📊 Traités: {stats.get('completed', 0)}/{stats.get('total', 0)}\\n"
                        f"✅ Réussis: {stats.get('successful', 0)}\\n"
                        f"❌ Échecs: {stats.get('failed', 0)}"
                    )
                else:
                    self.progress_label.configure(text="✅ Envoi terminé avec succès!")
                    
                    success_rate = stats.get('success_rate', 0)
                    if success_rate == 100:
                        messagebox.showinfo(
                            "🎉 Envoi réussi!",
                            f"Tous les messages ont été envoyés avec succès!\\n\\n"
                            f"📊 Total: {stats.get('total', 0)} messages\\n"
                            f"⏱️ Durée: {self._format_time(stats.get('elapsed_time', 0))}\\n"
                            f"🚀 Débit: {stats.get('messages_per_second', 0):.1f} msg/sec"
                        )
                    else:
                        messagebox.showwarning(
                            "⚠️ Envoi terminé avec erreurs",
                            f"L'envoi est terminé mais avec quelques erreurs.\\n\\n"
                            f"📊 Total: {stats.get('total', 0)} messages\\n"
                            f"✅ Réussis: {stats.get('successful', 0)} ({success_rate:.1f}%)\\n"
                            f"❌ Échecs: {stats.get('failed', 0)}\\n"
                            f"⏱️ Durée: {self._format_time(stats.get('elapsed_time', 0))}"
                        )
        
        except Exception as e:
            self.handle_error(f"Erreur lors de la finalisation: {str(e)}")
    
    def handle_error(self, error_message: str):
        """Gère les erreurs"""
        self.is_sending = False
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled")
        self.stop_btn.configure(state="disabled")
        
        self.progress_label.configure(text="❌ Erreur d'envoi")
        messagebox.showerror("Erreur", error_message)
    
    def _format_time(self, seconds: float) -> str:
        """Formate une durée en secondes"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds // 60:.0f}m {seconds % 60:.0f}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours:.0f}h {minutes:.0f}m"
    
    def on_closing(self):
        """Gestionnaire de fermeture"""
        if self.is_sending:
            confirm = messagebox.askyesno(
                "Confirmer la fermeture",
                "Un envoi est en cours. Voulez-vous vraiment fermer ?\\n\\n"
                "L'envoi sera annulé."
            )
            if confirm:
                self.bulk_sender.cancel_sending()
            else:
                return
        
        self.grab_release()
        self.destroy()