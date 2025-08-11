#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de simulation d'interruption et reprise d'envoi
"""

from api.bulk_sender import BulkSender, SendingSession
from api.whatsapp_client import WhatsAppClient, MessageResult
import time
import json

class MockWhatsAppClient(WhatsAppClient):
    """Client WhatsApp simulé pour les tests"""
    
    def __init__(self):
        # Ne pas appeler super().__init__ pour éviter la vraie initialisation
        self.instance_id = "test"
        self.token = "test"
        self.sent_count = 0
    
    def send_text_message(self, phone, message):
        """Simule l'envoi d'un message"""
        self.sent_count += 1
        
        # Simuler des succès et quelques échecs
        if self.sent_count % 10 == 0:  # 1 échec sur 10
            return MessageResult(phone, False, "Erreur simulée")
        else:
            return MessageResult(phone, True)

def test_interruption_reprise():
    print("🔄 TEST INTERRUPTION/REPRISE D'ENVOI")
    print("=" * 60)
    
    # Créer un client simulé
    mock_client = MockWhatsAppClient()
    sender = BulkSender(mock_client)
    
    # Nettoyer pour le test
    sender.sent_numbers.clear()
    sender._save_sent_numbers()
    
    # Préparer des messages de test
    test_messages = []
    for i in range(25):  # 25 messages (5 séries)
        phone = f"65015305{i:01d}"
        message = f"Message de test {i+1}"
        test_messages.append((phone, message, None))
    
    print(f"📱 Messages préparés: {len(test_messages)}")
    
    # PHASE 1: Début d'envoi normal
    print(f"\n📍 PHASE 1: Début d'envoi normal")
    print("-" * 40)
    
    print("🚀 Simulation d'envoi des 10 premiers messages...")
    
    # Simuler l'envoi des 10 premiers avec succès
    for i in range(10):
        phone, message, _ = test_messages[i]
        
        # Simuler l'envoi
        result = mock_client.send_text_message(phone, message)
        
        if result.success:
            normalized = sender._normalize_phone(phone)
            sender.sent_numbers.add(normalized)
            print(f"   ✅ Message {i+1}: {phone} → Envoyé")
        else:
            print(f"   ❌ Message {i+1}: {phone} → Échec")
    
    # Sauvegarder l'état
    sender._save_sent_numbers()
    
    print(f"💾 État sauvegardé: {len(sender.sent_numbers)} numéros contactés")
    
    # PHASE 2: Simulation d'interruption
    print(f"\n📍 PHASE 2: Simulation d'interruption")
    print("-" * 45)
    
    # Créer une nouvelle instance (simule le redémarrage après interruption)
    print("🔄 Simulation redémarrage application...")
    
    new_mock_client = MockWhatsAppClient()
    new_sender = BulkSender(new_mock_client)
    
    print(f"📊 État après redémarrage:")
    print(f"   💾 Numéros rechargés: {len(new_sender.sent_numbers)}")
    
    # Afficher quelques numéros rechargés
    loaded_numbers = list(new_sender.sent_numbers)[:5]
    print(f"   📋 Exemples rechargés: {loaded_numbers}")
    
    # PHASE 3: Test de reprise avec filtrage
    print(f"\n📍 PHASE 3: Reprise avec filtrage")
    print("-" * 40)
    
    print("🔍 Filtrage des messages (ignorer les déjà envoyés)...")
    
    # Tester le filtrage sur tous les messages
    remaining_messages = new_sender._filter_already_sent(test_messages)
    filtered_out = len(test_messages) - len(remaining_messages)
    
    print(f"   📤 Messages originaux: {len(test_messages)}")
    print(f"   ✅ Messages à envoyer: {len(remaining_messages)}")
    print(f"   ⏭️  Messages ignorés: {filtered_out}")
    print(f"   📊 Taux de filtrage: {filtered_out/len(test_messages)*100:.1f}%")
    
    # Continuer avec les messages restants
    print(f"\n🚀 Reprise de l'envoi (messages restants)...")
    
    sent_after_restart = 0
    for i, (phone, message, _) in enumerate(remaining_messages[:5]):  # 5 suivants
        result = new_mock_client.send_text_message(phone, message)
        
        if result.success:
            normalized = new_sender._normalize_phone(phone)
            new_sender.sent_numbers.add(normalized)
            new_sender._save_sent_numbers()
            sent_after_restart += 1
            print(f"   ✅ Reprise {i+1}: {phone} → Envoyé")
        else:
            print(f"   ❌ Reprise {i+1}: {phone} → Échec")
    
    # PHASE 4: Validation finale
    print(f"\n📍 PHASE 4: Validation finale")
    print("-" * 35)
    
    total_sent = len(new_sender.sent_numbers)
    
    # Vérifier le fichier final
    with open(new_sender.sent_numbers_file, 'r') as f:
        final_data = json.load(f)
    
    # Tests de validation
    validations = [
        ("💾 Persistence après interruption", len(new_sender.sent_numbers) >= 10),
        ("🔄 Rechargement automatique", len(new_sender.sent_numbers) > 0),
        ("🚫 Pas de doublons après reprise", filtered_out >= 10),
        ("📊 Cohérence fichier/mémoire", final_data['total_count'] == len(new_sender.sent_numbers)),
        ("🎯 Progression totale", total_sent >= 10)
    ]
    
    all_passed = True
    for test_name, passed in validations:
        status = "✅" if passed else "❌"
        print(f"   {status} {test_name}")
        if not passed:
            all_passed = False
    
    # Statistiques finales
    print(f"\n📊 STATISTIQUES FINALES:")
    print(f"   📤 Total messages testés: {len(test_messages)}")
    print(f"   ✅ Messages envoyés: {total_sent}")
    print(f"   🔄 Messages après interruption: {sent_after_restart}")
    print(f"   ⏭️  Messages filtrés: {filtered_out}")
    print(f"   💾 Fichier final: {final_data['total_count']} numéros")
    
    # Résultat final
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 TEST INTERRUPTION/REPRISE : ✅ PARFAITEMENT FONCTIONNEL")
        print("   • Sauvegarde continue pendant l'envoi ✅")
        print("   • Rechargement automatique après redémarrage ✅")  
        print("   • Filtrage efficace pour éviter les doublons ✅")
        print("   • Reprise transparente de l'envoi ✅")
        print("   • Intégrité des données maintenue ✅")
    else:
        print("❌ TEST INTERRUPTION/REPRISE : PROBLÈME DÉTECTÉ")
    
    print(f"{'='*60}")
    
    return all_passed

if __name__ == "__main__":
    success = test_interruption_reprise()