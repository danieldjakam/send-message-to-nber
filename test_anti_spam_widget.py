#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour le widget anti-spam entièrement personnalisable
"""

import customtkinter as ctk
import tkinter as tk
from utils.anti_spam_manager import AntiSpamManager, create_balanced_config
from ui.anti_spam_config_widget import UserCustomizableAntiSpamWidget

def test_customizable_widget():
    """Teste le widget entièrement personnalisable"""
    print("🧪 Test du widget anti-spam personnalisable...")
    
    # Créer la fenêtre de test
    root = ctk.CTk()
    root.title("Test - Widget Anti-Spam Personnalisable")
    root.geometry("800x600")
    
    # Créer le gestionnaire anti-spam
    anti_spam_manager = AntiSpamManager(create_balanced_config())
    
    def on_config_change(new_config):
        """Callback test"""
        print(f"✅ Configuration mise à jour:")
        print(f"   - Messages/jour: {new_config.max_messages_per_day}")
        print(f"   - Messages/heure: {new_config.max_messages_per_hour}")
        print(f"   - Délai min: {new_config.min_delay_between_messages}s")
        print(f"   - Délai max: {new_config.max_delay_between_messages}s")
        print(f"   - Pattern: {new_config.behavior_pattern.value}")
    
    # Créer le widget personnalisable
    try:
        widget = UserCustomizableAntiSpamWidget(
            root,
            anti_spam_manager,
            on_config_change=on_config_change
        )
        widget.pack(fill="both", expand=True, padx=20, pady=20)
        
        print("✅ Widget créé avec succès!")
        
        # Informations pour l'utilisateur
        print("\n📝 Instructions de test:")
        print("1. Testez le Mode Expert (devrait désactiver toutes les protections)")
        print("2. Configurez des limites personnalisées")
        print("3. Testez l'import/export de configurations")
        print("4. Vérifiez les préréglages")
        print("5. Fermez la fenêtre pour terminer le test")
        
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du widget: {e}")
        return False

if __name__ == "__main__":
    # Configuration CustomTkinter
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    success = test_customizable_widget()
    
    if success:
        print("\n✅ Test terminé avec succès!")
        print("Le widget anti-spam entièrement personnalisable fonctionne correctement.")
    else:
        print("\n❌ Test échoué!")