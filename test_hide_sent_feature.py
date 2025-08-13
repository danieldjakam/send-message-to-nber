#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de la fonctionnalité pour masquer les numéros déjà contactés
"""

import pandas as pd
from api.bulk_sender import BulkSender
from api.whatsapp_client import WhatsAppClient

def test_hide_sent_feature():
    """Teste la fonctionnalité de masquage des numéros envoyés"""
    print("🧪 Test de la fonctionnalité 'Masquer les déjà contactés'")
    print("=" * 60)
    
    # Créer des données de test
    test_data = {
        'CONTACTS 1': [
            '650000001', '650000002', '650000003', '650000004', '650000005',
            '650000006', '650000007', '650000008', '650000009', '650000010'
        ],
        'Message': [
            'Message 1', 'Message 2', 'Message 3', 'Message 4', 'Message 5',
            'Message 6', 'Message 7', 'Message 8', 'Message 9', 'Message 10'
        ]
    }
    
    df = pd.DataFrame(test_data)
    print(f"📊 Données de test créées: {len(df)} lignes")
    
    # Créer le BulkSender
    temp_client = WhatsAppClient("test", "test")
    bulk_sender = BulkSender(temp_client)
    
    # Simuler que quelques numéros ont été envoyés
    simulated_sent = ['650000002', '650000004', '650000007']
    for phone in simulated_sent:
        normalized = bulk_sender._normalize_phone(phone)
        bulk_sender.sent_numbers.add(normalized)
    
    print(f"📱 Numéros simulés comme envoyés: {simulated_sent}")
    
    # Tester le filtrage
    columns = ['CONTACTS 1', 'Message']
    
    # Simuler la fonction de filtrage de l'interface
    def filter_sent_numbers_from_display(df, columns, bulk_sender):
        """Réplique de la fonction dans main_with_advanced_progress.py"""
        if not bulk_sender.sent_numbers:
            return df[columns]
        
        # Trouver la colonne de téléphone
        phone_column = None
        for col in columns:
            if 'contact' in col.lower() or 'phone' in col.lower():
                phone_column = col
                break
        
        if phone_column is None:
            return df[columns]
        
        # Filtrer les lignes où le numéro n'est PAS dans la liste des envoyés
        filtered_mask = df[phone_column].apply(
            lambda phone: bulk_sender._normalize_phone(str(phone)) not in bulk_sender.sent_numbers
        )
        
        filtered_df = df[filtered_mask]
        return filtered_df[columns]
    
    # Test SANS filtrage
    print(f"\n📋 SANS filtrage (tous les numéros):")
    all_data = df[columns]
    print(f"   • Lignes affichées: {len(all_data)}")
    for i, row in all_data.iterrows():
        status = "❌ Déjà envoyé" if row['CONTACTS 1'] in simulated_sent else "✅ Pas encore envoyé"
        print(f"   {i+1:2d}. {row['CONTACTS 1']} - {status}")
    
    # Test AVEC filtrage
    print(f"\n🚫 AVEC filtrage (masquer les déjà contactés):")
    filtered_data = filter_sent_numbers_from_display(df, columns, bulk_sender)
    print(f"   • Lignes affichées: {len(filtered_data)}")
    print(f"   • Lignes masquées: {len(all_data) - len(filtered_data)}")
    
    for i, (idx, row) in enumerate(filtered_data.iterrows(), 1):
        print(f"   {i:2d}. {row['CONTACTS 1']} - ✅ Pas encore envoyé")
    
    # Vérification
    print(f"\n✅ Vérifications:")
    
    expected_remaining = [phone for phone in test_data['CONTACTS 1'] if phone not in simulated_sent]
    actual_remaining = filtered_data['CONTACTS 1'].tolist()
    
    if set(expected_remaining) == set(actual_remaining):
        print(f"   ✅ Filtrage correct: {len(expected_remaining)} numéros restants")
    else:
        print(f"   ❌ Erreur de filtrage!")
        print(f"      Attendu: {expected_remaining}")
        print(f"      Obtenu: {actual_remaining}")
        return False
    
    if len(simulated_sent) == (len(all_data) - len(filtered_data)):
        print(f"   ✅ Nombre de masqués correct: {len(simulated_sent)}")
    else:
        print(f"   ❌ Erreur de comptage!")
        return False
    
    # Test de mise à jour en temps réel
    print(f"\n🔄 Test de mise à jour en temps réel:")
    print(f"   Simulation: envoi du message à 650000001...")
    
    # Ajouter un nouveau numéro envoyé
    new_sent = '650000001'
    normalized = bulk_sender._normalize_phone(new_sent)
    bulk_sender.sent_numbers.add(normalized)
    
    # Nouveau filtrage
    updated_filtered = filter_sent_numbers_from_display(df, columns, bulk_sender)
    print(f"   • Lignes affichées maintenant: {len(updated_filtered)}")
    print(f"   • Lignes masquées maintenant: {len(all_data) - len(updated_filtered)}")
    
    if len(updated_filtered) == len(filtered_data) - 1:
        print(f"   ✅ Mise à jour correcte: 1 ligne supplémentaire masquée")
    else:
        print(f"   ❌ Erreur de mise à jour!")
        return False
    
    print(f"\n🎉 CONCLUSION:")
    print(f"   ✅ La fonctionnalité fonctionne parfaitement!")
    print(f"   ✅ Les numéros déjà contactés sont bien masqués")
    print(f"   ✅ La mise à jour en temps réel fonctionne")
    print(f"   ✅ Votre liste sera automatiquement nettoyée!")
    
    return True

if __name__ == "__main__":
    success = test_hide_sent_feature()
    exit(0 if success else 1)