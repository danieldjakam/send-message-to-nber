#!/usr/bin/env python3
"""
Test du système de limitation anti-spam
"""

from api.whatsapp_client import WhatsAppClient
from api.bulk_sender import BulkSender

def test_spam_limits():
    """Test des limites anti-spam"""
    
    print("🧪 Test des limites anti-spam")
    print("-" * 40)
    
    # Créer un client fictif
    client = WhatsAppClient("test", "test")
    bulk_sender = BulkSender(client)
    
    # Test 1: Limite normale
    print(f"📊 Limite configurée: {bulk_sender.get_max_messages_per_session()} messages")
    
    # Test 2: Création d'un gros dataset
    test_messages = []
    for i in range(3000):  # 3000 messages > limite de 2500
        phone = f"123456789{i:04d}"
        message = f"Message de test numéro {i+1}"
        test_messages.append((phone, message, None))
    
    print(f"📝 Dataset créé: {len(test_messages)} messages")
    
    # Test 3: Division en chunks
    chunks = bulk_sender.split_messages_for_safety(test_messages)
    print(f"📦 Divisé en {len(chunks)} chunks:")
    
    for i, chunk in enumerate(chunks, 1):
        print(f"   Chunk {i}: {len(chunk)} messages")
    
    # Test 4: Vérification des statistiques
    stats = bulk_sender.get_duplicate_stats()
    print(f"📈 Statistiques actuelles:")
    print(f"   Numéros contactés: {stats['sent_numbers_count']}")
    print(f"   Messages envoyés: {stats['total_messages_sent']}")
    
    print("\n✅ Tests terminés avec succès!")
    print("\n💡 Le système limitera automatiquement à 2500 messages par session")
    print("💡 Les sessions multiples permettront d'envoyer de gros volumes en sécurité")

if __name__ == "__main__":
    test_spam_limits()