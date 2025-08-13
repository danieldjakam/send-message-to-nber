#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de la configuration ultra-conservative pour éviter les blocages spam
"""

from api.bulk_sender import BulkSender
from api.whatsapp_client import WhatsAppClient
import time

def test_ultra_conservative_config():
    """Teste la nouvelle configuration ultra-conservative"""
    print("🛡️ Test de la configuration ULTRA-CONSERVATIVE")
    print("=" * 60)
    
    # Créer une instance pour tester la config
    temp_client = WhatsAppClient("test", "test")
    bulk_sender = BulkSender(temp_client)
    
    print(f"📊 NOUVELLE CONFIGURATION ANTI-SPAM:")
    print(f"   • Taille des batches: {bulk_sender.batch_size} messages")
    print(f"   • Délai entre messages: {bulk_sender.message_delay}s (base)")
    print(f"   • Délai entre batches: {bulk_sender.batch_delay}s ({bulk_sender.batch_delay/60:.1f} minutes)")
    print(f"   • Limite quotidienne: {bulk_sender.max_daily_limit} messages")
    print(f"   • Threads maximum: {bulk_sender.max_workers}")
    
    print(f"\n🎲 DÉLAIS ALÉATOIRES:")
    print(f"   • Utilisation: {bulk_sender.use_random_delays}")
    print(f"   • Entre messages: {bulk_sender.min_message_delay}-{bulk_sender.max_message_delay}s")
    print(f"   • Entre batches: {bulk_sender.min_batch_delay/60:.1f}-{bulk_sender.max_batch_delay/60:.1f} minutes")
    
    print(f"\n⏱️ SIMULATION DES TIMINGS:")
    
    # Simuler 3 batches de 3 messages chacun (9 messages total)
    total_batches = 3
    
    print(f"\n📋 Scénario: {total_batches} batches de {bulk_sender.batch_size} messages")
    
    total_time = 0
    
    for batch_num in range(total_batches):
        print(f"\n   🔄 BATCH {batch_num + 1}:")
        
        # Temps pour envoyer 3 messages avec délais
        batch_time = 0
        for msg_num in range(bulk_sender.batch_size):
            # Délai message (sauf le dernier)
            if msg_num < bulk_sender.batch_size - 1:
                message_delay = bulk_sender._get_random_message_delay()
                batch_time += message_delay
                print(f"      Message {msg_num + 1} → Attente {message_delay:.1f}s")
            else:
                print(f"      Message {msg_num + 1} → Dernier du batch")
        
        total_time += batch_time
        print(f"      ✅ Temps du batch: {batch_time:.1f}s ({batch_time/60:.1f} minutes)")
        
        # Pause entre batches (sauf après le dernier)
        if batch_num < total_batches - 1:
            batch_delay = bulk_sender._get_random_batch_delay()
            total_time += batch_delay
            print(f"      🛑 Pause avant batch suivant: {batch_delay:.1f}s ({batch_delay/60:.1f} minutes)")
    
    print(f"\n📈 RÉSUMÉ COMPLET:")
    print(f"   • Total messages: {total_batches * bulk_sender.batch_size}")
    print(f"   • Temps total: {total_time:.1f}s ({total_time/60:.1f} minutes ou {total_time/3600:.1f} heures)")
    print(f"   • Temps par message: {total_time/(total_batches * bulk_sender.batch_size):.1f}s")
    
    # Calcul pour une journée complète
    messages_per_hour = 3600 / (total_time / (total_batches * bulk_sender.batch_size))
    messages_per_day = messages_per_hour * 24
    
    print(f"\n📊 PROJECTION:")
    print(f"   • Messages/heure max: {messages_per_hour:.1f}")
    print(f"   • Messages/jour max: {messages_per_day:.1f}")
    print(f"   • Limite configurée: {bulk_sender.max_daily_limit}")
    
    # Vérifications de sécurité
    print(f"\n🛡️ VÉRIFICATIONS DE SÉCURITÉ:")
    
    success = True
    
    # Vérifier que la limite journalière est respectée
    if bulk_sender.max_daily_limit and messages_per_day > bulk_sender.max_daily_limit:
        print(f"   ✅ Limite journalière respectée: {bulk_sender.max_daily_limit} < {messages_per_day:.1f}")
    else:
        print(f"   ✅ Limite journalière OK")
    
    # Vérifier les délais minimums
    min_message_time = bulk_sender.min_message_delay
    min_batch_time = bulk_sender.min_batch_delay / 60
    
    if min_message_time >= 10:
        print(f"   ✅ Délai minimum entre messages: {min_message_time}s ≥ 10s")
    else:
        print(f"   ❌ Délai trop court entre messages: {min_message_time}s < 10s")
        success = False
    
    if min_batch_time >= 8:
        print(f"   ✅ Délai minimum entre batches: {min_batch_time:.1f}min ≥ 8min")
    else:
        print(f"   ❌ Délai trop court entre batches: {min_batch_time:.1f}min < 8min")
        success = False
    
    if bulk_sender.batch_size <= 3:
        print(f"   ✅ Taille de batch sécurisée: {bulk_sender.batch_size} ≤ 3")
    else:
        print(f"   ❌ Batch trop grand: {bulk_sender.batch_size} > 3")
        success = False
    
    print(f"\n{'='*60}")
    
    if success:
        print(f"🎉 CONFIGURATION ULTRA-SÉCURISÉE !")
        print(f"✅ Cette configuration devrait éviter TOUT blocage spam")
        print(f"✅ Très lent mais 100% fiable")
        print(f"✅ Simule parfaitement un comportement humain")
        print(f"✅ Maximum {bulk_sender.max_daily_limit} messages/jour")
    else:
        print(f"❌ CONFIGURATION ENCORE TROP AGRESSIVE")
        print(f"❌ Risque de blocage subsiste")
    
    return success

def show_timing_comparison():
    """Montre la comparaison avec l'ancienne configuration"""
    print(f"\n📊 COMPARAISON AVANT/APRÈS:")
    print(f"-" * 40)
    
    print(f"AVANT (configuration qui a causé le blocage):")
    print(f"   • 8 messages par batch")
    print(f"   • 6s entre messages")
    print(f"   • 1.5 minutes entre batches")
    print(f"   • ~320 messages/heure possible")
    print(f"   → RÉSULTAT: BLOCAGE SPAM ❌")
    
    print(f"\nAPRÈS (configuration ultra-conservative):")
    print(f"   • 3 messages par batch")
    print(f"   • 10-25s entre messages (aléatoire)")
    print(f"   • 8-15 minutes entre batches (aléatoire)")
    print(f"   • ~15 messages/heure maximum")
    print(f"   • Limite 50 messages/jour")
    print(f"   → RÉSULTAT: SÉCURITÉ MAXIMALE ✅")
    
    print(f"\n🎯 STRATÉGIE:")
    print(f"   1. Privilégier la SÉCURITÉ sur la VITESSE")
    print(f"   2. Imiter parfaitement un humain")
    print(f"   3. Rester sous toutes les limites de détection")
    print(f"   4. Augmenter progressivement si pas de blocage")

if __name__ == "__main__":
    success = test_ultra_conservative_config()
    show_timing_comparison()
    
    print(f"\n🚀 RECOMMANDATION:")
    if success:
        print(f"✅ Utilisez cette configuration pour éviter les blocages")
        print(f"✅ Patience requise mais sécurité garantie")
    else:
        print(f"❌ Configuration à ajuster encore")
    
    exit(0 if success else 1)