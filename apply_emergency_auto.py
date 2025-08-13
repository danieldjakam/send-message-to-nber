#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration d'urgence automatique après blocage spam
Application immédiate des paramètres les plus sécurisés
"""

import json
import os
from pathlib import Path

def apply_emergency_config_auto():
    """Appliquer automatiquement la configuration d'urgence"""
    
    print("🚨 APPLICATION AUTOMATIQUE - CONFIGURATION D'URGENCE")
    print("=" * 60)
    
    # Configuration ultra-sécurisée pour récupération post-blocage
    emergency_config = {
        "batch_size": 2,                    # Ultra-petit batch
        "message_delay_min": 20,            # 20s minimum entre messages
        "message_delay_max": 45,            # 45s maximum entre messages
        "batch_delay_min": 15,              # 15 minutes minimum entre batches
        "batch_delay_max": 25,              # 25 minutes maximum entre batches
        "max_workers": 1,                   # Un seul thread
        "daily_limit": 20,                  # 20 messages/jour maximum
        "enable_session_persistence": True,
        "enable_duplicate_check": True,
        "conservative_mode": True,
        "anti_spam_level": "MAXIMUM",
        
        # Sécurité supplémentaire
        "enable_progressive_delay": True,   # Délais qui augmentent
        "weekend_pause": True,              # Pause le weekend
        "night_pause": True,                # Pause la nuit
        "error_backoff": True,              # Arrêt en cas d'erreur
        
        # Monitoring renforcé
        "log_level": "DEBUG",
        "detailed_stats": True,
        "alert_on_errors": True
    }
    
    # Créer le répertoire de configuration s'il n'existe pas
    config_dir = Path.home() / '.excel_whatsapp'
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / 'emergency_config.json'
    
    try:
        # Sauvegarder la configuration d'urgence
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(emergency_config, f, indent=4, ensure_ascii=False)
        
        print("✅ Configuration d'urgence appliquée avec succès!")
        print(f"📁 Sauvegardée dans: {config_file}")
        print("\n🛡️  PARAMÈTRES APPLIQUÉS:")
        print(f"   • Batch size: {emergency_config['batch_size']} messages")
        print(f"   • Délai messages: {emergency_config['message_delay_min']}-{emergency_config['message_delay_max']}s")
        print(f"   • Délai batches: {emergency_config['batch_delay_min']}-{emergency_config['batch_delay_max']} minutes")
        print(f"   • Limite quotidienne: {emergency_config['daily_limit']} messages")
        print(f"   • Threads: {emergency_config['max_workers']}")
        
        print("\n📊 IMPACT:")
        print("   • ~3-4 messages par heure maximum")
        print("   • Risque de blocage quasi-nul")
        print("   • Parfait pour récupération post-blocage")
        
        print("\n⚠️  INSTRUCTIONS POST-CONFIGURATION:")
        print("   1. 🛑 ATTENDEZ 24-48H avant tout envoi")
        print("   2. 🧪 Testez avec seulement 2-3 messages")
        print("   3. 📈 Augmentez très progressivement")
        print("   4. 👀 Surveillez attentivement les résultats")
        
        # Créer aussi un fichier de statut
        status_file = config_dir / 'emergency_status.json'
        status = {
            "emergency_applied": True,
            "applied_at": str(pd.Timestamp.now()),
            "reason": "Spam block recovery",
            "next_test_allowed": str(pd.Timestamp.now() + pd.Timedelta(hours=24)),
            "recovery_phase": "emergency_config"
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=4, ensure_ascii=False)
        
        print(f"\n📈 STATUT: Configuration d'urgence active")
        print(f"⏰ Prochain test autorisé: dans 24h minimum")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'application: {str(e)}")
        return False

def update_main_configs():
    """Mettre à jour les configurations des applications principales"""
    
    print("\n🔧 MISE À JOUR DES CONFIGURATIONS PRINCIPALES...")
    
    # Paramètres à injecter dans les scripts principaux
    ultra_safe_settings = """
# CONFIGURATION D'URGENCE POST-BLOCAGE
EMERGENCY_MODE = True
BATCH_SIZE = 2
MESSAGE_DELAY_MIN = 20
MESSAGE_DELAY_MAX = 45
BATCH_DELAY_MIN = 900  # 15 minutes
BATCH_DELAY_MAX = 1500  # 25 minutes
MAX_DAILY_MESSAGES = 20
MAX_WORKERS = 1
"""
    
    # Créer un fichier de paramètres d'urgence
    emergency_settings_file = "emergency_settings.py"
    
    try:
        with open(emergency_settings_file, 'w', encoding='utf-8') as f:
            f.write(ultra_safe_settings)
        
        print(f"✅ Paramètres d'urgence créés: {emergency_settings_file}")
        
        # Instructions pour l'utilisateur
        print("\n📋 POUR UTILISER CES PARAMÈTRES:")
        print("   1. Avant d'envoyer, importez: from emergency_settings import *")
        print("   2. Ou utilisez: python main_optimized.py avec ces paramètres")
        print("   3. Ou modifiez manuellement les variables dans vos scripts")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    import pandas as pd
    
    print("🚨 RÉCUPÉRATION POST-BLOCAGE SPAM")
    print("=" * 50)
    print("Application automatique des paramètres ultra-sécurisés")
    print()
    
    success1 = apply_emergency_config_auto()
    success2 = update_main_configs()
    
    if success1 and success2:
        print("\n" + "=" * 60)
        print("✅ CONFIGURATION D'URGENCE APPLIQUÉE AVEC SUCCÈS!")
        print("=" * 60)
        print()
        print("🔥 ÉTAPES SUIVANTES OBLIGATOIRES:")
        print("   1. 🛑 Arrêtez IMMÉDIATEMENT tout envoi")
        print("   2. ⏰ Attendez 24-48h minimum")
        print("   3. 🧪 Testez avec 2-3 messages seulement")
        print("   4. 📈 Montez en charge très progressivement")
        print("   5. 👀 Surveillez constamment les résultats")
        print()
        print("⚠️  RESPECTER CES ÉTAPES EST CRITIQUE POUR LA RÉCUPÉRATION!")
        
    else:
        print("\n❌ Erreur lors de l'application de la configuration")
        print("Vérifiez les permissions et réessayez")