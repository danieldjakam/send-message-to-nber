#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier la configuration des délais anti-spam
"""

from api.bulk_sender import BulkSender
from api.whatsapp_client import WhatsAppClient

def test_bulk_sender_config():
    """Teste la configuration du BulkSender"""
    print("🧪 Test de la configuration anti-spam du BulkSender")
    print("=" * 60)
    
    # Créer une instance temporaire pour tester la config
    temp_client = WhatsAppClient("test", "test")
    bulk_sender = BulkSender(temp_client)
    
    print(f"📊 Configuration actuelle:")
    print(f"   • Taille des batches: {bulk_sender.batch_size} messages")
    print(f"   • Délai entre messages: {bulk_sender.message_delay} secondes")
    print(f"   • Délai entre batches: {bulk_sender.batch_delay} secondes ({bulk_sender.batch_delay//60} minutes)")
    print(f"   • Messages par série: {bulk_sender.message_burst_limit}")
    print(f"   • Pause entre séries: {bulk_sender.burst_pause_duration} secondes ({bulk_sender.burst_pause_duration//60} minutes)")
    print(f"   • Threads maximum: {bulk_sender.max_workers}")
    
    print("\n🎯 Comportement attendu:")
    print(f"   1. Envoie {bulk_sender.batch_size} messages avec {bulk_sender.message_delay}s entre chacun")
    print(f"   2. Pause de {bulk_sender.batch_delay//60} minutes")
    print(f"   3. Recommence automatiquement avec le batch suivant")
    
    print("\n⏱️ Calcul des timings:")
    temps_batch = (bulk_sender.batch_size - 1) * bulk_sender.message_delay  # -1 car pas de délai après le dernier
    temps_total_8_msg = temps_batch + bulk_sender.batch_delay
    print(f"   • Temps pour 8 messages: {temps_batch}s ({temps_batch//60}min {temps_batch%60}s)")
    print(f"   • Temps total avec pause: {temps_total_8_msg}s ({temps_total_8_msg//60}min {temps_total_8_msg%60}s)")
    
    # Simuler pour 24 messages (3 batches)
    total_batches = 3
    temps_total = (total_batches * temps_batch) + ((total_batches - 1) * bulk_sender.batch_delay)
    print(f"\n📈 Exemple pour 24 messages (3 batches):")
    print(f"   • Temps total estimé: {temps_total}s ({temps_total//60}min {temps_total%60}s)")
    
    # Vérifications
    print("\n✅ Vérifications:")
    success = True
    
    if bulk_sender.batch_size != 8:
        print(f"   ❌ Taille de batch incorrecte: {bulk_sender.batch_size} au lieu de 8")
        success = False
    else:
        print(f"   ✅ Taille de batch correcte: {bulk_sender.batch_size}")
    
    if bulk_sender.message_delay != 6.0:
        print(f"   ❌ Délai entre messages incorrect: {bulk_sender.message_delay}s au lieu de 6s")
        success = False
    else:
        print(f"   ✅ Délai entre messages correct: {bulk_sender.message_delay}s")
    
    if bulk_sender.batch_delay != 180.0:
        print(f"   ❌ Délai entre batches incorrect: {bulk_sender.batch_delay}s au lieu de 180s")
        success = False
    else:
        print(f"   ✅ Délai entre batches correct: {bulk_sender.batch_delay}s (3 minutes)")
    
    if bulk_sender.max_workers != 1:
        print(f"   ❌ Nombre de threads incorrect: {bulk_sender.max_workers} au lieu de 1")
        success = False
    else:
        print(f"   ✅ Envoi séquentiel configuré: {bulk_sender.max_workers} thread")
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Configuration anti-spam correcte ! L'application respectera:")
        print("   • 6 secondes entre chaque message")
        print("   • 8 messages puis pause de 3 minutes")
        print("   • Reprise automatique")
    else:
        print("❌ Configuration incorrecte - vérifiez les paramètres")
    
    return success

if __name__ == "__main__":
    test_bulk_sender_config()