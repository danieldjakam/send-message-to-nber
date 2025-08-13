#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vérificateur de statut de récupération post-blocage
Aide à décider si vous pouvez reprendre l'envoi
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

def check_recovery_status():
    """Vérifier le statut de récupération et donner des recommandations"""
    
    print("🔍 VÉRIFICATION DU STATUT DE RÉCUPÉRATION")
    print("=" * 50)
    
    config_dir = Path.home() / '.excel_whatsapp'
    status_file = config_dir / 'emergency_status.json'
    
    if not status_file.exists():
        print("⚠️  Aucun statut d'urgence trouvé")
        print("Si vous venez d'être bloqué, lancez: python apply_emergency_auto.py")
        return False
    
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)
        
        applied_at = datetime.fromisoformat(status['applied_at'].replace('Z', '+00:00'))
        next_test = datetime.fromisoformat(status['next_test_allowed'].replace('Z', '+00:00'))
        now = datetime.now()
        
        hours_since_block = (now - applied_at).total_seconds() / 3600
        hours_until_test = (next_test - now).total_seconds() / 3600
        
        print(f"📅 Configuration appliquée: {applied_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"⏰ Temps écoulé depuis: {hours_since_block:.1f} heures")
        
        if hours_until_test > 0:
            print(f"⏳ Attente recommandée encore: {hours_until_test:.1f} heures")
            print("🛑 STATUT: ATTENDRE - PAS PRÊT POUR TEST")
            
            print(f"\n📋 RECOMMANDATIONS ACTUELLES:")
            print("   • Continuez à attendre")
            print("   • N'envoyez AUCUN message")
            print("   • Préparez vos messages de test")
            print("   • Vérifiez votre configuration")
            
            return False
            
        else:
            print("✅ STATUT: PRÊT POUR TEST MINIMAL")
            print(f"⏰ Fenêtre de test ouverte depuis: {abs(hours_until_test):.1f} heures")
            
            # Recommandations selon le temps écoulé
            if hours_since_block < 48:
                print(f"\n🧪 PHASE DE TEST MINIMAL (< 48h)")
                print("   • Maximum 2-3 messages de test")
                print("   • Vers des numéros connus seulement")
                print("   • Espacement 30-60 secondes")
                print("   • Messages différents et naturels")
                print("   • Surveillance constante des résultats")
                
            elif hours_since_block < 168:  # 1 semaine
                print(f"\n📈 PHASE DE MONTÉE PROGRESSIVE (< 1 semaine)")
                print("   • Maximum 5-10 messages/jour")
                print("   • Espacement minimum 20 minutes")
                print("   • Batch de 2 messages maximum")
                print("   • Surveillance des métriques")
                
            else:
                print(f"\n🔄 PHASE DE STABILISATION (> 1 semaine)")
                print("   • Maximum 20-30 messages/jour")
                print("   • Configuration ultra-conservatrice permanente")
                print("   • Monitoring continu obligatoire")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {str(e)}")
        return False

def show_current_config():
    """Afficher la configuration actuelle"""
    
    config_dir = Path.home() / '.excel_whatsapp'
    config_file = config_dir / 'emergency_config.json'
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"\n🛡️  CONFIGURATION ACTUELLE:")
            print(f"   • Batch size: {config.get('batch_size', 'N/A')}")
            print(f"   • Délai messages: {config.get('message_delay_min', 'N/A')}-{config.get('message_delay_max', 'N/A')}s")
            print(f"   • Délai batches: {config.get('batch_delay_min', 'N/A')}-{config.get('batch_delay_max', 'N/A')} min")
            print(f"   • Limite quotidienne: {config.get('daily_limit', 'N/A')}")
            print(f"   • Mode conservateur: {config.get('conservative_mode', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Erreur configuration: {str(e)}")

def get_test_recommendations():
    """Donner des recommandations spécifiques pour les tests"""
    
    print(f"\n📝 GUIDE DE TEST SÉCURISÉ:")
    print("=" * 30)
    
    print("🎯 Messages de test recommandés:")
    print('   1. "Bonjour, c\'est un test de notre système"')
    print('   2. "Salut, juste un petit message pour vérifier"') 
    print('   3. "Hello, test de fonctionnement - merci!"')
    
    print(f"\n🔢 Numéros de test:")
    print("   • Utilisez VOS propres numéros")
    print("   • Ou des contacts qui vous connaissent")
    print("   • JAMAIS de numéros inconnus pour les tests")
    
    print(f"\n⏰ Timing recommandé:")
    print("   • Entre 9h-17h en semaine")
    print("   • Jamais le weekend pour les tests")
    print("   • Espacement 30-60s minimum")
    
    print(f"\n🚨 Signaux d'arrêt immédiat:")
    print("   • Message non délivré")
    print("   • Erreur dans les logs")
    print("   • Pas d'accusé de lecture après 10min")
    print("   • Destinataire signale spam")

def main():
    """Fonction principale"""
    
    ready_for_test = check_recovery_status()
    show_current_config()
    
    if ready_for_test:
        get_test_recommendations()
        
        print(f"\n" + "=" * 60)
        print("✅ PRÊT POUR TEST - PROCÉDEZ AVEC PRUDENCE")
        print("=" * 60)
        print("⚠️  Respectez scrupuleusement les recommandations ci-dessus!")
        
    else:
        print(f"\n" + "=" * 60)
        print("🛑 PAS PRÊT - CONTINUEZ L'ATTENTE")
        print("=" * 60)
        print("🕐 Relancez ce script dans quelques heures")

if __name__ == "__main__":
    main()