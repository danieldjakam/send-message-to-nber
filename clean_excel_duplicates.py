#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour nettoyer les doublons dans le fichier Excel
"""

import pandas as pd
from datetime import datetime

def clean_excel_duplicates():
    """Nettoie les doublons du fichier Excel"""
    print("🧹 Nettoyage des doublons dans le fichier Excel")
    print("=" * 50)
    
    input_file = "12 Aout 2025 18 COLONNES.XLSX"
    output_file = f"12 Aout 2025 18 COLONNES - SANS DOUBLONS.xlsx"
    
    try:
        # Charger le fichier
        print(f"📂 Chargement de {input_file}...")
        df = pd.read_excel(input_file)
        
        initial_count = len(df)
        print(f"📊 Lignes initiales: {initial_count}")
        
        # Analyser les doublons dans CONTACTS 1
        if 'CONTACTS 1' in df.columns:
            contacts1_before = df['CONTACTS 1'].value_counts()
            duplicates_before = contacts1_before[contacts1_before > 1]
            
            print(f"\n🔍 Doublons détectés dans CONTACTS 1:")
            print(f"   • Numéros uniques: {len(contacts1_before)}")
            print(f"   • Numéros dupliqués: {len(duplicates_before)}")
            
            if len(duplicates_before) > 0:
                print(f"   • Détail des doublons:")
                for phone, count in duplicates_before.head(10).items():
                    print(f"     - {phone}: {count} fois")
            
            # Supprimer les doublons basés sur CONTACTS 1
            print(f"\n🧹 Suppression des doublons...")
            df_clean = df.drop_duplicates(subset=['CONTACTS 1'], keep='first')
            
            final_count = len(df_clean)
            removed_count = initial_count - final_count
            
            print(f"✅ Nettoyage terminé:")
            print(f"   • Lignes initiales: {initial_count}")
            print(f"   • Lignes finales: {final_count}")
            print(f"   • Doublons supprimés: {removed_count}")
            
            # Sauvegarder le fichier nettoyé
            print(f"\n💾 Sauvegarde vers {output_file}...")
            df_clean.to_excel(output_file, index=False)
            
            print(f"🎉 FICHIER NETTOYÉ CRÉÉ !")
            print(f"📂 Nouveau fichier: {output_file}")
            print(f"📊 {final_count} numéros uniques")
            print(f"✅ Plus aucun doublon!")
            
            # Vérification finale
            print(f"\n✅ Vérification finale:")
            df_verify = pd.read_excel(output_file)
            contacts1_after = df_verify['CONTACTS 1'].value_counts()
            duplicates_after = contacts1_after[contacts1_after > 1]
            
            if len(duplicates_after) == 0:
                print(f"   ✅ Aucun doublon restant - parfait!")
            else:
                print(f"   ❌ {len(duplicates_after)} doublons restants")
            
        else:
            print("❌ Colonne CONTACTS 1 non trouvée")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def compare_files():
    """Compare les deux fichiers pour montrer la différence"""
    print(f"\n📊 Comparaison des fichiers:")
    print("-" * 30)
    
    try:
        # Fichier original
        df_original = pd.read_excel("12 Aout 2025 18 COLONNES.XLSX")
        contacts1_orig = df_original['CONTACTS 1'].tolist()
        
        # Fichier nettoyé
        df_clean = pd.read_excel("12 Aout 2025 18 COLONNES - SANS DOUBLONS.xlsx")
        contacts1_clean = df_clean['CONTACTS 1'].tolist()
        
        print(f"Fichier original:")
        print(f"   • {len(contacts1_orig)} lignes")
        print(f"   • {len(set(contacts1_orig))} numéros uniques")
        print(f"   • {len(contacts1_orig) - len(set(contacts1_orig))} doublons")
        
        print(f"\nFichier nettoyé:")
        print(f"   • {len(contacts1_clean)} lignes")
        print(f"   • {len(set(contacts1_clean))} numéros uniques")
        print(f"   • {len(contacts1_clean) - len(set(contacts1_clean))} doublons")
        
        # Numéros supprimés
        removed_numbers = set(contacts1_orig) - set(contacts1_clean)
        if removed_numbers:
            print(f"\n❌ Attention: {len(removed_numbers)} numéros uniques perdus:")
            for num in list(removed_numbers)[:5]:
                print(f"   - {num}")
        else:
            print(f"\n✅ Aucun numéro unique perdu - parfait!")
            
    except Exception as e:
        print(f"❌ Erreur lors de la comparaison: {e}")

if __name__ == "__main__":
    clean_excel_duplicates()
    try:
        compare_files()
    except:
        pass