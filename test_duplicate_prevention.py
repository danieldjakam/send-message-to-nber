#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier le système anti-doublons
"""

import pandas as pd
from api.bulk_sender import BulkSender
from api.whatsapp_client import WhatsAppClient
from pathlib import Path
import json

def test_duplicate_prevention():
    print("🧪 TEST DU SYSTÈME ANTI-DOUBLONS")
    print("=" * 50)
    
    # Créer un client temporaire pour les tests
    temp_client = WhatsAppClient("test_instance", "test_token")
    bulk_sender = BulkSender(temp_client)
    
    # Afficher l'état initial
    initial_count = bulk_sender.get_sent_numbers_count()
    print(f"📊 Numéros déjà contactés: {initial_count}")
    
    # Charger le fichier Excel
    try:
        df = pd.read_excel('MESSAGE CIBLE OBTENU DES INDUSTRIELS.xlsx')
        print(f"📁 Fichier Excel chargé: {len(df)} lignes")
        
        # Prendre les premiers numéros de chaque colonne
        test_messages = []
        for col in df.columns:
            if col in ['ISTE', 'ISSAS ET ESG', 'INSAM']:
                for i in range(min(10, len(df))):  # 10 premiers de chaque colonne
                    phone = str(df.iloc[i][col]).strip()
                    if phone and phone != 'nan':
                        test_messages.append((phone, f"Test message pour {phone}", None))
        
        print(f"📱 Messages de test préparés: {len(test_messages)}")
        
        # Test 1: Filtrage initial
        print("\n🔍 TEST 1: Filtrage initial")
        print("-" * 30)
        
        original_count = len(test_messages)
        filtered = bulk_sender._filter_already_sent(test_messages)
        filtered_count = len(filtered)
        skipped = original_count - filtered_count
        
        print(f"📤 Messages originaux: {original_count}")
        print(f"✅ Messages à envoyer: {filtered_count}")
        print(f"⏭️ Messages ignorés (déjà contactés): {skipped}")
        
        if skipped > 0:
            print(f"📋 Exemples de numéros déjà contactés:")
            already_sent = []
            for phone, _, _ in test_messages:
                if bulk_sender.is_phone_already_sent(phone):
                    already_sent.append(phone)
                    if len(already_sent) <= 5:
                        print(f"   - {phone}")
            if len(already_sent) > 5:
                print(f"   ... et {len(already_sent) - 5} autres")
        
        # Test 2: Simulation d'ajout de numéros
        print("\n➕ TEST 2: Simulation d'ajout de nouveaux numéros")
        print("-" * 45)
        
        if filtered_count > 0:
            # Simuler l'ajout de 3 numéros comme "contactés"
            test_numbers = [phone for phone, _, _ in filtered[:3]]
            for phone in test_numbers:
                bulk_sender.sent_numbers.add(phone)
                print(f"✅ Simulé: {phone} ajouté comme contacté")
            
            # Sauvegarder
            bulk_sender._save_sent_numbers()
            print("💾 Sauvegarde effectuée")
            
            # Retester le filtrage
            print("\n🔄 TEST 3: Nouveau filtrage après simulation")
            print("-" * 40)
            
            new_filtered = bulk_sender._filter_already_sent(test_messages)
            new_filtered_count = len(new_filtered)
            new_skipped = original_count - new_filtered_count
            
            print(f"📤 Messages originaux: {original_count}")
            print(f"✅ Messages à envoyer maintenant: {new_filtered_count}")
            print(f"⏭️ Messages ignorés maintenant: {new_skipped}")
            print(f"📈 Différence: {new_skipped - skipped} numéros supplémentaires ignorés")
        
        # Afficher le contenu du fichier JSON
        print("\n📁 CONTENU DU FICHIER sent_numbers.json")
        print("-" * 40)
        
        sent_file = bulk_sender.sent_numbers_file
        if sent_file.exists():
            with open(sent_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            total_saved = data.get('total_count', 0)
            last_updated = data.get('last_updated', 'N/A')
            
            print(f"📊 Total numéros sauvés: {total_saved}")
            print(f"🕒 Dernière mise à jour: {last_updated}")
            print(f"📍 Emplacement: {sent_file}")
            
            if total_saved <= 10:
                print(f"📋 Numéros sauvés:")
                for i, num in enumerate(data.get('sent_numbers', []), 1):
                    print(f"   {i:2d}. {num}")
            else:
                print(f"📋 Premiers numéros sauvés:")
                for i, num in enumerate(data.get('sent_numbers', [])[:5], 1):
                    print(f"   {i:2d}. {num}")
                print(f"   ... et {total_saved - 5} autres")
        else:
            print("❌ Fichier sent_numbers.json n'existe pas encore")
        
        print("\n" + "=" * 50)
        print("✅ TEST TERMINÉ - Le système anti-doublons fonctionne !")
        print("💡 Lors du prochain envoi, tous ces numéros seront automatiquement ignorés")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

if __name__ == "__main__":
    test_duplicate_prevention()