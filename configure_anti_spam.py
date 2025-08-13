#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de configuration des paramètres anti-spam
Permet de choisir le niveau de sécurité souhaité
"""

from api.bulk_sender import BulkSender
from api.whatsapp_client import WhatsAppClient

def configure_anti_spam():
    """Configure les paramètres anti-spam selon le niveau de sécurité"""
    print("⚙️ Configuration des paramètres Anti-Spam")
    print("=" * 50)
    
    print("🛡️ Choisissez votre niveau de sécurité:")
    print("   1. 🔴 MAXIMUM (après blocage) - Le plus sûr")
    print("   2. 🟡 ÉLEVÉ (préventif) - Sécurisé")
    print("   3. 🟢 MODÉRÉ (classique) - Équilibré")
    print("   4. 🔵 PERSONNALISÉ - Vous choisissez")
    
    while True:
        try:
            choice = input("\nVotre choix (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                break
            print("❌ Choix invalide. Tapez 1, 2, 3 ou 4")
        except KeyboardInterrupt:
            print("\n👋 Configuration annulée")
            return False
    
    configs = get_security_configs()
    
    if choice == '4':
        config = create_custom_config()
    else:
        config_names = ['maximum', 'elevated', 'moderate']
        config = configs[config_names[int(choice) - 1]]
    
    # Afficher la configuration choisie
    display_config(config)
    
    # Demander confirmation
    confirm = input("\n✅ Appliquer cette configuration ? (o/N): ").strip().lower()
    if confirm not in ['o', 'oui', 'y', 'yes']:
        print("❌ Configuration annulée")
        return False
    
    # Appliquer la configuration
    apply_config(config)
    print("🎉 Configuration appliquée avec succès !")
    
    return True

def get_security_configs():
    """Retourne les configurations prédéfinies"""
    return {
        'maximum': {
            'name': '🔴 MAXIMUM (après blocage)',
            'batch_size': 3,
            'message_delay_min': 15,
            'message_delay_max': 30,
            'batch_delay_min': 10,  # minutes
            'batch_delay_max': 20,  # minutes
            'daily_limit': 30,
            'description': 'Pour récupérer après un blocage - Ultra sécurisé'
        },
        'elevated': {
            'name': '🟡 ÉLEVÉ (préventif)',
            'batch_size': 5,
            'message_delay_min': 10,
            'message_delay_max': 20,
            'batch_delay_min': 5,   # minutes
            'batch_delay_max': 10,  # minutes
            'daily_limit': 100,
            'description': 'Préventif - Très sécurisé'
        },
        'moderate': {
            'name': '🟢 MODÉRÉ (classique)',
            'batch_size': 8,
            'message_delay_min': 6,
            'message_delay_max': 12,
            'batch_delay_min': 2,   # minutes
            'batch_delay_max': 5,   # minutes
            'daily_limit': 200,
            'description': 'Équilibré - Risque modéré'
        }
    }

def create_custom_config():
    """Crée une configuration personnalisée"""
    print("\n🔵 Configuration personnalisée:")
    
    config = {
        'name': '🔵 PERSONNALISÉ',
        'description': 'Configuration personnalisée'
    }
    
    # Taille des batches
    while True:
        try:
            batch_size = int(input("Nombre de messages par batch (1-10): "))
            if 1 <= batch_size <= 10:
                config['batch_size'] = batch_size
                break
            print("❌ Doit être entre 1 et 10")
        except ValueError:
            print("❌ Veuillez entrer un nombre")
    
    # Délai entre messages
    print(f"\nDélai entre messages (secondes):")
    while True:
        try:
            min_delay = float(input("  Minimum (5-60): "))
            if 5 <= min_delay <= 60:
                config['message_delay_min'] = min_delay
                break
            print("❌ Doit être entre 5 et 60 secondes")
        except ValueError:
            print("❌ Veuillez entrer un nombre")
    
    while True:
        try:
            max_delay = float(input(f"  Maximum ({min_delay}-120): "))
            if min_delay <= max_delay <= 120:
                config['message_delay_max'] = max_delay
                break
            print(f"❌ Doit être entre {min_delay} et 120 secondes")
        except ValueError:
            print("❌ Veuillez entrer un nombre")
    
    # Délai entre batches
    print(f"\nDélai entre batches (minutes):")
    while True:
        try:
            min_batch = float(input("  Minimum (1-30): "))
            if 1 <= min_batch <= 30:
                config['batch_delay_min'] = min_batch
                break
            print("❌ Doit être entre 1 et 30 minutes")
        except ValueError:
            print("❌ Veuillez entrer un nombre")
    
    while True:
        try:
            max_batch = float(input(f"  Maximum ({min_batch}-60): "))
            if min_batch <= max_batch <= 60:
                config['batch_delay_max'] = max_batch
                break
            print(f"❌ Doit être entre {min_batch} et 60 minutes")
        except ValueError:
            print("❌ Veuillez entrer un nombre")
    
    # Limite quotidienne
    while True:
        try:
            daily = int(input("Limite quotidienne de messages (10-1000): "))
            if 10 <= daily <= 1000:
                config['daily_limit'] = daily
                break
            print("❌ Doit être entre 10 et 1000")
        except ValueError:
            print("❌ Veuillez entrer un nombre")
    
    return config

def display_config(config):
    """Affiche une configuration"""
    print(f"\n📋 Configuration: {config['name']}")
    print(f"   📝 {config['description']}")
    print(f"   📦 Messages par batch: {config['batch_size']}")
    print(f"   ⏱️  Délai entre messages: {config['message_delay_min']}-{config['message_delay_max']}s")
    print(f"   🛑 Délai entre batches: {config['batch_delay_min']}-{config['batch_delay_max']} minutes")
    print(f"   📊 Limite quotidienne: {config['daily_limit']} messages")
    
    # Calculs estimatifs
    avg_msg_delay = (config['message_delay_min'] + config['message_delay_max']) / 2
    avg_batch_delay = (config['batch_delay_min'] + config['batch_delay_max']) / 2 * 60  # en secondes
    
    time_per_batch = (config['batch_size'] - 1) * avg_msg_delay + avg_batch_delay
    messages_per_hour = 3600 * config['batch_size'] / time_per_batch if time_per_batch > 0 else 0
    
    print(f"   📈 Estimation: ~{messages_per_hour:.1f} messages/heure")
    
    # Niveau de risque
    if config['batch_size'] <= 3 and avg_msg_delay >= 15 and avg_batch_delay >= 600:
        risk = "🟢 TRÈS FAIBLE"
    elif config['batch_size'] <= 5 and avg_msg_delay >= 10 and avg_batch_delay >= 300:
        risk = "🟡 FAIBLE"
    elif config['batch_size'] <= 8 and avg_msg_delay >= 6 and avg_batch_delay >= 120:
        risk = "🟠 MODÉRÉ"
    else:
        risk = "🔴 ÉLEVÉ"
    
    print(f"   ⚠️  Risque de blocage: {risk}")

def apply_config(config):
    """Applique une configuration au fichier bulk_sender.py"""
    import fileinput
    import sys
    
    file_path = "api/bulk_sender.py"
    
    # Mappings des valeurs à remplacer
    replacements = {
        'batch_size: int = 3': f'batch_size: int = {config["batch_size"]}',
        'self.batch_delay = 600.0': f'self.batch_delay = {config["batch_delay_min"] * 60:.1f}',
        'self.message_delay = 15.0': f'self.message_delay = {config["message_delay_min"]:.1f}',
        'self.max_daily_limit = 50': f'self.max_daily_limit = {config["daily_limit"]}',
        'self.message_burst_limit = 3': f'self.message_burst_limit = {config["batch_size"]}',
        'self.burst_pause_duration = 600': f'self.burst_pause_duration = {config["batch_delay_min"] * 60:.0f}',
        'self.min_message_delay = 10.0': f'self.min_message_delay = {config["message_delay_min"]:.1f}',
        'self.max_message_delay = 25.0': f'self.max_message_delay = {config["message_delay_max"]:.1f}',
        'self.min_batch_delay = 480.0': f'self.min_batch_delay = {config["batch_delay_min"] * 60:.1f}',
        'self.max_batch_delay = 900.0': f'self.max_batch_delay = {config["batch_delay_max"] * 60:.1f}',
    }
    
    # Lire le fichier et appliquer les remplacements
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    # Écrire le fichier modifié
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    print("⚙️ CONFIGURATEUR ANTI-SPAM")
    print("Pour éviter les blocages WhatsApp")
    print()
    
    success = configure_anti_spam()
    
    if success:
        print(f"\n🚀 PROCHAINES ÉTAPES:")
        print(f"   1. Relancez l'application")
        print(f"   2. Testez avec quelques messages")
        print(f"   3. Si pas de blocage, vous pouvez rester sur ces paramètres")
        print(f"   4. En cas de blocage, revenez au niveau MAXIMUM")
        print(f"\n⚠️  IMPORTANT:")
        print(f"   • Respectez toujours la limite quotidienne")
        print(f"   • Évitez les pics d'activité")
        print(f"   • Surveillez les signaux d'alerte")
    else:
        print(f"\n👋 Configuration annulée - paramètres inchangés")
    
    exit(0 if success else 1)