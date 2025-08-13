#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application immédiate des paramètres ultra-sécurisés (sans confirmation)
"""

def apply_ultra_safe_config():
    """Applique immédiatement la configuration ultra-sécurisée"""
    print("🚨 APPLICATION IMMÉDIATE - PARAMÈTRES ULTRA-SÉCURISÉS")
    print("=" * 60)
    
    config = {
        'batch_size': 2,
        'message_delay_min': 20.0,
        'message_delay_max': 45.0,
        'batch_delay_min': 900.0,  # 15 minutes en secondes
        'batch_delay_max': 1500.0, # 25 minutes en secondes
        'daily_limit': 20
    }
    
    file_path = "api/bulk_sender.py"
    
    try:
        # Lire le fichier
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacements spécifiques et sûrs
        replacements = [
            ('batch_size: int = 3)', f'batch_size: int = {config["batch_size"]})'),
            ('batch_size: int = 8)', f'batch_size: int = {config["batch_size"]})'),
            ('batch_size: int = 5)', f'batch_size: int = {config["batch_size"]})'),
            ('self.batch_delay = 600.0', f'self.batch_delay = {config["batch_delay_min"]}'),
            ('self.batch_delay = 300.0', f'self.batch_delay = {config["batch_delay_min"]}'),
            ('self.batch_delay = 90.0', f'self.batch_delay = {config["batch_delay_min"]}'),
            ('self.message_delay = 15.0', f'self.message_delay = {config["message_delay_min"]}'),
            ('self.message_delay = 10.0', f'self.message_delay = {config["message_delay_min"]}'),  
            ('self.message_delay = 6.0', f'self.message_delay = {config["message_delay_min"]}'),
            ('self.max_daily_limit = 50', f'self.max_daily_limit = {config["daily_limit"]}'),
            ('self.max_daily_limit = 100', f'self.max_daily_limit = {config["daily_limit"]}'),
            ('self.max_daily_limit = None', f'self.max_daily_limit = {config["daily_limit"]}'),
            ('self.message_burst_limit = 8', f'self.message_burst_limit = {config["batch_size"]}'),
            ('self.message_burst_limit = 5', f'self.message_burst_limit = {config["batch_size"]}'),
            ('self.message_burst_limit = 3', f'self.message_burst_limit = {config["batch_size"]}'),
            ('self.min_message_delay = 10.0', f'self.min_message_delay = {config["message_delay_min"]}'),
            ('self.min_message_delay = 15.0', f'self.min_message_delay = {config["message_delay_min"]}'),
            ('self.max_message_delay = 25.0', f'self.max_message_delay = {config["message_delay_max"]}'),
            ('self.max_message_delay = 30.0', f'self.max_message_delay = {config["message_delay_max"]}'),
            ('self.min_batch_delay = 480.0', f'self.min_batch_delay = {config["batch_delay_min"]}'),
            ('self.min_batch_delay = 600.0', f'self.min_batch_delay = {config["batch_delay_min"]}'),
            ('self.max_batch_delay = 900.0', f'self.max_batch_delay = {config["batch_delay_max"]}'),
            ('self.max_batch_delay = 1200.0', f'self.max_batch_delay = {config["batch_delay_max"]}'),
        ]
        
        changes_made = 0
        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                changes_made += 1
                print(f"✅ {old} → {new}")
        
        # Écrire le fichier modifié
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n🎉 CONFIGURATION ULTRA-SÉCURISÉE APPLIQUÉE !")
        print(f"📝 {changes_made} paramètres modifiés")
        
        # Afficher la configuration finale
        print(f"\n📊 NOUVELLE CONFIGURATION:")
        print(f"   • {config['batch_size']} messages par batch")
        print(f"   • {config['message_delay_min']:.0f}-{config['message_delay_max']:.0f}s entre messages")
        print(f"   • {config['batch_delay_min']/60:.0f}-{config['batch_delay_max']/60:.0f} minutes entre batches")
        print(f"   • Maximum {config['daily_limit']} messages/jour")
        
        print(f"\n⏱️ ESTIMATION:")
        avg_msg_delay = (config['message_delay_min'] + config['message_delay_max']) / 2
        avg_batch_delay = (config['batch_delay_min'] + config['batch_delay_max']) / 2
        time_per_batch = (config['batch_size'] - 1) * avg_msg_delay + avg_batch_delay
        messages_per_hour = 3600 * config['batch_size'] / time_per_batch
        
        print(f"   • ~{messages_per_hour:.1f} messages/heure maximum")
        print(f"   • Risque de blocage: 🟢 QUASI-NUL")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'application: {e}")
        return False

if __name__ == "__main__":
    success = apply_ultra_safe_config()
    
    if success:
        print(f"\n🚀 PRÊT POUR LA RÉCUPÉRATION:")
        print(f"   1. Attendez 24h avant de reprendre l'envoi")
        print(f"   2. Commencez par 2-3 messages de test seulement")
        print(f"   3. Surveillez attentivement les résultats")
        print(f"   4. Si OK, augmentez très progressivement")
        
        print(f"\n⚠️ RÈGLES STRICTES:")
        print(f"   • Jamais plus de 20 messages/jour")
        print(f"   • Pauses de 15-25 minutes obligatoires")
        print(f"   • Arrêt immédiat au moindre problème")
        
        print(f"\n🔄 Pour relancer l'application:")
        print(f"   python main_with_advanced_progress.py")
    else:
        print(f"\n❌ Échec de la configuration")
    
    exit(0 if success else 1)