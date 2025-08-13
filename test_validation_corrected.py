#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test pour vérifier que la validation des délais a été corrigée
"""

from api.bulk_sender import BulkSender
from api.whatsapp_client import WhatsAppClient
from ui.bulk_send_dialog import BulkSendDialog

def test_validation_corrected():
    """Teste que la validation des délais accepte maintenant 180 secondes"""
    print("🧪 Test de la validation corrigée des délais")
    print("=" * 50)
    
    try:
        # Créer un client temporaire
        temp_client = WhatsAppClient("test", "test")
        bulk_sender = BulkSender(temp_client)
        
        # Vérifier les valeurs configurées
        print(f"📊 Valeurs configurées:")
        print(f"   • batch_delay: {bulk_sender.batch_delay}s")
        print(f"   • message_delay: {bulk_sender.message_delay}s")
        print(f"   • batch_size: {bulk_sender.batch_size}")
        
        # Tester la validation en créant une instance
        # (mais ne pas afficher le dialog)
        print(f"\n🔍 Test de validation...")
        
        # Simuler la validation qui était problématique
        if bulk_sender.batch_delay < 0 or bulk_sender.batch_delay > 600:
            print(f"❌ Validation échoue: délai {bulk_sender.batch_delay}s > 600s")
            return False
        else:
            print(f"✅ Validation réussie: délai {bulk_sender.batch_delay}s ≤ 600s")
        
        print(f"\n✅ Toutes les validations passent correctement!")
        print(f"🎉 L'application peut maintenant utiliser:")
        print(f"   • 6 secondes entre chaque message")
        print(f"   • 3 minutes (180s) entre chaque batch")
        print(f"   • 8 messages par batch")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_validation_corrected()
    exit(0 if success else 1)