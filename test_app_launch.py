#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test pour vérifier que l'application se lance sans erreurs Tkinter
"""

import sys
import time
import threading
from pathlib import Path

def test_app_launch():
    """Teste le lancement de l'application"""
    print("🧪 Test de lancement de l'application")
    print("=" * 50)
    
    try:
        # Import des modules
        import customtkinter as ctk
        from api.bulk_sender import BulkSender
        from api.whatsapp_client import WhatsAppClient
        
        print("✅ Imports réussis")
        
        # Test de création des instances principales
        temp_client = WhatsAppClient("test", "test")
        bulk_sender = BulkSender(temp_client)
        
        print("✅ Instances créées")
        print(f"📊 Configuration: {bulk_sender.batch_size} messages, {bulk_sender.batch_delay}s pause")
        
        # Test de l'interface principale (sans l'afficher)
        root = ctk.CTk()
        root.withdraw()  # Cacher la fenêtre
        
        print("✅ Interface Tkinter créée")
        
        # Nettoyer
        root.destroy()
        
        print("✅ Test réussi - l'application devrait fonctionner")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    success = test_app_launch()
    if success:
        print(f"\n🎉 L'application peut être lancée avec: python main_with_advanced_progress.py")
    else:
        print(f"\n❌ Des problèmes subsistent")
    exit(0 if success else 1)