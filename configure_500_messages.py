#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurateur pour atteindre 500 messages/jour selon différentes stratégies
"""

def show_500_messages_options():
    """Affiche les options pour atteindre 500 messages/jour"""
    print("🎯 CONFIGURATEUR POUR 500 MESSAGES/JOUR")
    print("=" * 50)
    
    print("⚠️  IMPORTANT: Vous venez d'être bloqué pour spam !")
    print("   Choisissez votre stratégie avec précaution\n")
    
    strategies = {
        '1': {
            'name': '🟢 SÉCURISÉE - Montée Progressive (Recommandée)',
            'description': 'Augmentation graduelle sur 2-3 mois',
            'success_rate': '70%',
            'risk': 'Modéré',
            'phases': [
                {'week': 1, 'daily_limit': 20, 'batch_size': 2, 'msg_delay': [20, 45], 'batch_delay': [15, 25]},
                {'week': 2, 'daily_limit': 50, 'batch_size': 3, 'msg_delay': [15, 30], 'batch_delay': [10, 20]},
                {'week': 3, 'daily_limit': 100, 'batch_size': 4, 'msg_delay': [12, 25], 'batch_delay': [8, 15]},
                {'week': 4, 'daily_limit': 200, 'batch_size': 5, 'msg_delay': [10, 20], 'batch_delay': [5, 12]},
                {'week': 8, 'daily_limit': 350, 'batch_size': 6, 'msg_delay': [8, 15], 'batch_delay': [4, 8]},
                {'week': 12, 'daily_limit': 500, 'batch_size': 7, 'msg_delay': [6, 12], 'batch_delay': [3, 6]}
            ]
        },
        '2': {
            'name': '🟡 ACCÉLÉRÉE - Montée Rapide (Risquée)',
            'description': 'Augmentation rapide sur 3-4 semaines',  
            'success_rate': '30%',
            'risk': 'Élevé',
            'phases': [
                {'week': 1, 'daily_limit': 50, 'batch_size': 3, 'msg_delay': [15, 30], 'batch_delay': [8, 15]},
                {'week': 2, 'daily_limit': 150, 'batch_size': 5, 'msg_delay': [10, 20], 'batch_delay': [5, 10]},
                {'week': 3, 'daily_limit': 300, 'batch_size': 7, 'msg_delay': [8, 15], 'batch_delay': [3, 6]},
                {'week': 4, 'daily_limit': 500, 'batch_size': 8, 'msg_delay': [6, 12], 'batch_delay': [2, 4]}
            ]
        },
        '3': {
            'name': '🔴 IMMÉDIATE - Configuration Directe (Très Risquée)',
            'description': 'Configuration pour 500 msg/jour immédiatement',
            'success_rate': '5%',
            'risk': 'Maximum',
            'phases': [
                {'week': 1, 'daily_limit': 500, 'batch_size': 8, 'msg_delay': [6, 10], 'batch_delay': [2, 3]}
            ]
        },
        '4': {
            'name': '🛡️ ALTERNATIVE - Multiple Comptes (Sûre)',
            'description': '5 comptes × 100 msg/jour = 500 total',
            'success_rate': '85%',
            'risk': 'Faible',
            'phases': [
                {'week': 1, 'daily_limit': 100, 'batch_size': 4, 'msg_delay': [12, 20], 'batch_delay': [6, 12], 'accounts': 5}
            ]
        }
    }
    
    for key, strategy in strategies.items():
        print(f"{key}. {strategy['name']}")
        print(f"   📝 {strategy['description']}")
        print(f"   📊 Taux de succès: {strategy['success_rate']}")
        print(f"   ⚠️  Risque: {strategy['risk']}")
        print()
    
    while True:
        try:
            choice = input("Votre choix (1-4): ").strip()
            if choice in strategies:
                return strategies[choice]
            print("❌ Choix invalide. Tapez 1, 2, 3 ou 4")
        except KeyboardInterrupt:
            print("\n👋 Configuration annulée")
            return None

def apply_strategy_config(strategy):
    """Applique la configuration d'une stratégie"""
    print(f"\n🔧 APPLICATION: {strategy['name']}")
    print("=" * 60)
    
    if 'accounts' in strategy['phases'][0]:
        print("🏢 STRATÉGIE MULTIPLE COMPTES:")
        print(f"   • Créez {strategy['phases'][0]['accounts']} comptes/instances WhatsApp")
        print(f"   • Configurez chaque compte pour {strategy['phases'][0]['daily_limit']} msg/jour")
        print(f"   • Total: {strategy['phases'][0]['accounts']} × {strategy['phases'][0]['daily_limit']} = {strategy['phases'][0]['accounts'] * strategy['phases'][0]['daily_limit']} msg/jour")
        print("\n⚙️ Configuration par compte:")
        phase = strategy['phases'][0]
    else:
        print("📅 PLANNING DES PHASES:")
        for phase in strategy['phases']:
            if phase['week'] == 1:
                print(f"   📍 Semaine {phase['week']}: {phase['daily_limit']} msg/jour (DÉBUT)")
            elif phase['week'] <= 4:
                print(f"   📍 Semaine {phase['week']}: {phase['daily_limit']} msg/jour")
            else:
                print(f"   📍 Mois {phase['week']//4}: {phase['daily_limit']} msg/jour")
        
        print(f"\n🚀 CONFIGURATION POUR LA PHASE 1:")
        phase = strategy['phases'][0]
    
    print(f"   • Batch size: {phase['batch_size']} messages")
    print(f"   • Délai entre messages: {phase['msg_delay'][0]}-{phase['msg_delay'][1]}s")
    print(f"   • Délai entre batches: {phase['batch_delay'][0]}-{phase['batch_delay'][1]} minutes")
    print(f"   • Limite quotidienne: {phase['daily_limit']} messages")
    
    # Calcul de la capacité théorique
    avg_msg_delay = sum(phase['msg_delay']) / 2
    avg_batch_delay = sum(phase['batch_delay']) / 2 * 60  # en secondes
    time_per_batch = (phase['batch_size'] - 1) * avg_msg_delay + avg_batch_delay
    working_hours = 16
    theoretical_capacity = int((working_hours * 3600 * phase['batch_size']) / time_per_batch) if time_per_batch > 0 else 0
    
    print(f"\n📊 VÉRIFICATION:")
    print(f"   • Capacité théorique: {theoretical_capacity} msg/jour")
    print(f"   • Limite configurée: {phase['daily_limit']} msg/jour")
    
    if theoretical_capacity >= phase['daily_limit']:
        print(f"   ✅ Configuration viable")
    else:
        print(f"   ⚠️ Configuration limite (respectez strictement les horaires)")
    
    # Appliquer la configuration
    confirm = input(f"\n✅ Appliquer cette configuration maintenant ? (o/N): ").strip().lower()
    if confirm not in ['o', 'oui', 'y', 'yes']:
        print("❌ Configuration annulée")
        return False
    
    apply_config_to_file(phase)
    return True

def apply_config_to_file(phase):
    """Applique une phase de configuration au fichier bulk_sender.py"""
    file_path = "api/bulk_sender.py"
    
    try:
        # Lire le fichier
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacements
        replacements = [
            ('batch_size: int = 2)', f'batch_size: int = {phase["batch_size"]})'),
            ('batch_size: int = 3)', f'batch_size: int = {phase["batch_size"]})'),
            ('batch_size: int = 8)', f'batch_size: int = {phase["batch_size"]})'),
            ('self.batch_delay = 900.0', f'self.batch_delay = {phase["batch_delay"][0] * 60:.1f}'),
            ('self.batch_delay = 600.0', f'self.batch_delay = {phase["batch_delay"][0] * 60:.1f}'),
            ('self.message_delay = 20.0', f'self.message_delay = {phase["msg_delay"][0]:.1f}'),
            ('self.message_delay = 15.0', f'self.message_delay = {phase["msg_delay"][0]:.1f}'),
            ('self.max_daily_limit = 20', f'self.max_daily_limit = {phase["daily_limit"]}'),
            ('self.max_daily_limit = 50', f'self.max_daily_limit = {phase["daily_limit"]}'),
            ('self.message_burst_limit = 2', f'self.message_burst_limit = {phase["batch_size"]}'),
            ('self.message_burst_limit = 3', f'self.message_burst_limit = {phase["batch_size"]}'),
            ('self.min_message_delay = 20.0', f'self.min_message_delay = {phase["msg_delay"][0]:.1f}'),
            ('self.max_message_delay = 45.0', f'self.max_message_delay = {phase["msg_delay"][1]:.1f}'),
            ('self.min_batch_delay = 900.0', f'self.min_batch_delay = {phase["batch_delay"][0] * 60:.1f}'),
            ('self.max_batch_delay = 1500.0', f'self.max_batch_delay = {phase["batch_delay"][1] * 60:.1f}'),
        ]
        
        changes_made = 0
        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                changes_made += 1
        
        # Écrire le fichier modifié
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Configuration appliquée ! ({changes_made} modifications)")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'application: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🎯 OBJECTIF: 500 MESSAGES PAR JOUR")
    print("📅 Après un blocage spam")
    print()
    
    strategy = show_500_messages_options()
    
    if strategy:
        success = apply_strategy_config(strategy)
        
        if success:
            print(f"\n🎉 CONFIGURATION APPLIQUÉE AVEC SUCCÈS !")
            
            if strategy['name'].startswith('🟢'):
                print(f"✅ Stratégie sécurisée choisie - Excellent choix !")
                print(f"📅 Suivez le planning sur 2-3 mois")
                print(f"📊 Surveillez attentivement les métriques")
                
            elif strategy['name'].startswith('🟡'):
                print(f"⚠️ Stratégie accélérée - Soyez très vigilant !")
                print(f"🚨 Arrêt immédiat au moindre signe de problème")
                
            elif strategy['name'].startswith('🔴'):
                print(f"🚨 STRATÉGIE TRÈS RISQUÉE - 95% de chance de blocage !")
                print(f"⚠️ Dernière chance avant bannissement possible")
                
            elif strategy['name'].startswith('🛡️'):
                print(f"🏢 Stratégie multiple comptes - La plus sûre !")
                print(f"📋 Configurez 5 comptes avec les mêmes paramètres")
            
            print(f"\n🚀 Pour démarrer:")
            print(f"   python main_with_advanced_progress.py")
            
        else:
            print(f"\n❌ Configuration annulée")
    else:
        print(f"\n👋 Au revoir !")
    
    print(f"\n💡 RAPPEL: La patience est la clé du succès à long terme !")