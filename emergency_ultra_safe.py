#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'urgence pour appliquer les paramètres ultra-sécurisés
À utiliser après un blocage spam
"""

def apply_emergency_config():
    """Applique immédiatement la configuration d'urgence la plus sûre"""
    print("🚨 APPLICATION D'URGENCE - PARAMÈTRES ULTRA-SÉCURISÉS")
    print("=" * 60)
    
    config = {
        'batch_size': 2,           # Seulement 2 messages par batch
        'message_delay_min': 20,   # Minimum 20 secondes entre messages
        'message_delay_max': 45,   # Maximum 45 secondes entre messages  
        'batch_delay_min': 15,     # Minimum 15 minutes entre batches
        'batch_delay_max': 25,     # Maximum 25 minutes entre batches
        'daily_limit': 20          # Maximum 20 messages par jour
    }
    
    print("⚠️  CONFIGURATION D'URGENCE:")
    print(f"   • {config['batch_size']} messages par batch (ultra-petit)")
    print(f"   • {config['message_delay_min']}-{config['message_delay_max']}s entre messages")
    print(f"   • {config['batch_delay_min']}-{config['batch_delay_max']} minutes entre batches")
    print(f"   • Maximum {config['daily_limit']} messages/jour")
    print()
    print("📊 RÉSULTAT ATTENDU:")
    print(f"   • ~3-4 messages par heure maximum")
    print(f"   • Risque de blocage quasi-nul")
    print(f"   • Parfait pour récupérer après un blocage")
    
    confirm = input("\n🚨 Appliquer cette configuration d'urgence ? (O/n): ").strip().lower()
    if confirm not in ['', 'o', 'oui', 'y', 'yes']:
        print("❌ Configuration d'urgence annulée")
        return False
    
    # Appliquer la configuration
    file_path = "api/bulk_sender.py"
    
    replacements = {
        'batch_size: int = 3': f'batch_size: int = {config["batch_size"]}',
        'batch_size: int = 5': f'batch_size: int = {config["batch_size"]}',
        'batch_size: int = 8': f'batch_size: int = {config["batch_size"]}',
        'self.batch_delay = 600.0': f'self.batch_delay = {config["batch_delay_min"] * 60:.1f}',
        'self.batch_delay = 300.0': f'self.batch_delay = {config["batch_delay_min"] * 60:.1f}',
        'self.batch_delay = 90.0': f'self.batch_delay = {config["batch_delay_min"] * 60:.1f}',
        'self.message_delay = 15.0': f'self.message_delay = {config["message_delay_min"]:.1f}',
        'self.message_delay = 10.0': f'self.message_delay = {config["message_delay_min"]:.1f}',
        'self.message_delay = 6.0': f'self.message_delay = {config["message_delay_min"]:.1f}',
        'self.max_daily_limit = 50': f'self.max_daily_limit = {config["daily_limit"]}',
        'self.max_daily_limit = 100': f'self.max_daily_limit = {config["daily_limit"]}',
        'self.max_daily_limit = 200': f'self.max_daily_limit = {config["daily_limit"]}',
        'self.max_daily_limit = None': f'self.max_daily_limit = {config["daily_limit"]}',
        'self.message_burst_limit = 3': f'self.message_burst_limit = {config["batch_size"]}',
        'self.message_burst_limit = 5': f'self.message_burst_limit = {config["batch_size"]}',
        'self.message_burst_limit = 8': f'self.message_burst_limit = {config["batch_size"]}',
        'self.burst_pause_duration = 600': f'self.burst_pause_duration = {config["batch_delay_min"] * 60:.0f}',
        'self.burst_pause_duration = 300': f'self.burst_pause_duration = {config["batch_delay_min"] * 60:.0f}',
        'self.burst_pause_duration = 90': f'self.burst_pause_duration = {config["batch_delay_min"] * 60:.0f}',
        'self.min_message_delay = 10.0': f'self.min_message_delay = {config["message_delay_min"]:.1f}',
        'self.min_message_delay = 6.0': f'self.min_message_delay = {config["message_delay_min"]:.1f}',
        'self.max_message_delay = 25.0': f'self.max_message_delay = {config["message_delay_max"]:.1f}',
        'self.max_message_delay = 20.0': f'self.max_message_delay = {config["message_delay_max"]:.1f}',
        'self.max_message_delay = 12.0': f'self.max_message_delay = {config["message_delay_max"]:.1f}',
        'self.min_batch_delay = 480.0': f'self.min_batch_delay = {config["batch_delay_min"] * 60:.1f}',
        'self.min_batch_delay = 300.0': f'self.min_batch_delay = {config["batch_delay_min"] * 60:.1f}',
        'self.min_batch_delay = 120.0': f'self.min_batch_delay = {config["batch_delay_min"] * 60:.1f}',
        'self.max_batch_delay = 900.0': f'self.max_batch_delay = {config["batch_delay_max"] * 60:.1f}',
        'self.max_batch_delay = 600.0': f'self.max_batch_delay = {config["batch_delay_max"] * 60:.1f}',
        'self.max_batch_delay = 300.0': f'self.max_batch_delay = {config["batch_delay_max"] * 60:.1f}',
    }
    
    try:
        # Lire le fichier
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Appliquer les remplacements
        changes_made = 0
        for old, new in replacements.items():
            if old in content:
                content = content.replace(old, new)
                changes_made += 1
        
        # Écrire le fichier modifié
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Configuration d'urgence appliquée !")
        print(f"📝 {changes_made} paramètres modifiés")
        
        print(f"\n🚀 UTILISATION RECOMMANDÉE:")
        print(f"   1. Attendez 24h avant de reprendre l'envoi")
        print(f"   2. Commencez par 5-10 messages seulement")
        print(f"   3. Surveillez attentivement les réactions")
        print(f"   4. Si OK, augmentez très progressivement")
        
        print(f"\n⚠️  RÈGLES STRICTES:")
        print(f"   • Jamais plus de 20 messages/jour")
        print(f"   • Arrêt immédiat au moindre signe de problème")
        print(f"   • Pauses obligatoires de 15-25 minutes")
        print(f"   • Messages espacés de 20-45 secondes")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'application: {e}")
        return False

if __name__ == "__main__":
    print("🚨 SCRIPT D'URGENCE ANTI-SPAM")
    print("À utiliser après un blocage WhatsApp")
    print()
    
    success = apply_emergency_config()
    
    if success:
        print(f"\n🎉 CONFIGURATION D'URGENCE ACTIVÉE")
        print(f"   Votre application est maintenant ultra-sécurisée")
        print(f"   Relancez avec: python main_with_advanced_progress.py")
    else:
        print(f"\n❌ Échec de la configuration d'urgence")
        print(f"   Vérifiez le fichier api/bulk_sender.py manuellement")
    
    exit(0 if success else 1)