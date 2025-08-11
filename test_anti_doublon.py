#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test rapide du système anti-doublons
"""

from api.bulk_sender import BulkSender
from api.whatsapp_client import WhatsAppClient
import json

def test_anti_doublon():
    print("🧪 TEST ANTI-DOUBLONS")
    print("=" * 40)
    
    # Créer une instance de test
    client = WhatsAppClient("test", "test")
    sender = BulkSender(client)
    
    print(f"📊 Numéros déjà contactés: {len(sender.sent_numbers)}")
    
    # Test d'ajout manuel
    test_numbers = ["650153059", "650986024", "651085909"]
    
    print("\n➕ Ajout de numéros de test...")
    for num in test_numbers:
        normalized = sender._normalize_phone(num)
        sender.sent_numbers.add(normalized)
        print(f"   {num} → {normalized}")
    
    # Sauvegarder
    sender._save_sent_numbers()
    print(f"💾 Sauvegardé: {len(sender.sent_numbers)} numéros")
    
    # Vérifier le fichier
    with open(sender.sent_numbers_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n📁 Contenu du fichier:")
    print(f"   Total: {data['total_count']}")
    print(f"   Numéros: {data['sent_numbers']}")
    
    # Test de filtrage
    test_messages = [
        ("650153059", "Test 1", None),  # Déjà contacté
        ("651234567", "Test 2", None),  # Nouveau
        ("650986024", "Test 3", None),  # Déjà contacté
    ]
    
    print(f"\n🔍 Test de filtrage:")
    print(f"   Messages originaux: {len(test_messages)}")
    filtered = sender._filter_already_sent(test_messages)
    print(f"   Messages après filtrage: {len(filtered)}")
    
    for phone, _, _ in filtered:
        print(f"   ✅ À envoyer: {phone}")
    
    print(f"\n{'='*40}")
    print("✅ Test terminé")

if __name__ == "__main__":
    test_anti_doublon()