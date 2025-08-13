#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse du fichier Excel pour identifier les problèmes potentiels avec les numéros
"""

import pandas as pd
from collections import Counter
import re

def analyze_excel_file():
    """Analyse le fichier Excel pour détecter les problèmes"""
    print("🔍 Analyse du fichier Excel")
    print("=" * 50)
    
    file_path = "12 Aout 2025 18 COLONNES.XLSX"
    
    try:
        # Charger le fichier Excel
        df = pd.read_excel(file_path)
        print(f"✅ Fichier chargé: {len(df)} lignes, {len(df.columns)} colonnes")
        
        # Afficher les colonnes disponibles
        print(f"\n📋 Colonnes disponibles:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2d}. {col}")
        
        # Chercher les colonnes qui contiennent des numéros de téléphone
        phone_columns = []
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['contact', 'phone', 'tel', 'numero', 'number', 'mobile']):
                phone_columns.append(col)
        
        print(f"\n📱 Colonnes de numéros détectées: {phone_columns}")
        
        # Analyser la colonne "contacts 1" spécifiquement
        if 'contacts 1' in df.columns:
            analyze_phone_column(df, 'contacts 1')
        elif phone_columns:
            # Prendre la première colonne de téléphone trouvée
            analyze_phone_column(df, phone_columns[0])
        else:
            print("❌ Aucune colonne de numéros de téléphone trouvée")
            # Analyser toutes les colonnes pour voir laquelle pourrait contenir des numéros
            for col in df.columns:
                sample_values = df[col].dropna().head(5).tolist()
                print(f"   {col}: {sample_values}")
    
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")

def analyze_phone_column(df, column_name):
    """Analyse une colonne spécifique de numéros de téléphone"""
    print(f"\n🔍 Analyse de la colonne '{column_name}'")
    print("-" * 40)
    
    # Statistiques de base
    total_rows = len(df)
    phone_data = df[column_name].dropna()
    valid_count = len(phone_data)
    empty_count = total_rows - valid_count
    
    print(f"📊 Statistiques de base:")
    print(f"   • Total lignes: {total_rows}")
    print(f"   • Numéros non vides: {valid_count}")
    print(f"   • Cellules vides: {empty_count}")
    
    if valid_count == 0:
        print("❌ Aucun numéro trouvé dans cette colonne")
        return
    
    # Analyser les formats des numéros
    phone_list = phone_data.astype(str).tolist()
    
    # Patterns communs
    patterns = {
        'avec_plus': 0,      # +XX...
        'avec_00': 0,        # 00XX...
        'normal': 0,         # 6XXXXXXXX
        'avec_espaces': 0,   # XX XX XX
        'avec_tirets': 0,    # XX-XX-XX
        'invalide': 0        # Autres formats
    }
    
    formats_examples = {
        'avec_plus': [],
        'avec_00': [],
        'normal': [],
        'avec_espaces': [],
        'avec_tirets': [],
        'invalide': []
    }
    
    for phone in phone_list[:100]:  # Analyser les 100 premiers
        phone_str = str(phone).strip()
        
        if phone_str.startswith('+'):
            patterns['avec_plus'] += 1
            if len(formats_examples['avec_plus']) < 3:
                formats_examples['avec_plus'].append(phone_str)
        elif phone_str.startswith('00'):
            patterns['avec_00'] += 1
            if len(formats_examples['avec_00']) < 3:
                formats_examples['avec_00'].append(phone_str)
        elif ' ' in phone_str:
            patterns['avec_espaces'] += 1
            if len(formats_examples['avec_espaces']) < 3:
                formats_examples['avec_espaces'].append(phone_str)
        elif '-' in phone_str:
            patterns['avec_tirets'] += 1
            if len(formats_examples['avec_tirets']) < 3:
                formats_examples['avec_tirets'].append(phone_str)
        elif re.match(r'^[0-9]+$', phone_str) and len(phone_str) >= 8:
            patterns['normal'] += 1
            if len(formats_examples['normal']) < 3:
                formats_examples['normal'].append(phone_str)
        else:
            patterns['invalide'] += 1
            if len(formats_examples['invalide']) < 3:
                formats_examples['invalide'].append(phone_str)
    
    print(f"\n📱 Formats de numéros détectés:")
    for format_type, count in patterns.items():
        if count > 0:
            percentage = (count / len(phone_list)) * 100
            examples = formats_examples[format_type]
            print(f"   • {format_type}: {count} ({percentage:.1f}%) - Ex: {examples}")
    
    # Détecter les doublons
    phone_counts = Counter(phone_list)
    duplicates = {phone: count for phone, count in phone_counts.items() if count > 1}
    
    print(f"\n🔄 Analyse des doublons:")
    print(f"   • Numéros uniques: {len(phone_counts)}")
    print(f"   • Numéros en doublon: {len(duplicates)}")
    
    if duplicates:
        print(f"   • Top 5 doublons:")
        for phone, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"     - {phone}: {count} fois")
        
        # Calculer l'impact des doublons
        duplicate_entries = sum(count - 1 for count in duplicates.values())
        print(f"   • Entrées en trop à cause des doublons: {duplicate_entries}")
    
    # Analyser les longueurs
    lengths = [len(str(phone).replace(' ', '').replace('-', '').replace('+', '')) for phone in phone_list]
    length_counts = Counter(lengths)
    
    print(f"\n📏 Longueurs des numéros (chiffres seulement):")
    for length, count in sorted(length_counts.items()):
        percentage = (count / len(phone_list)) * 100
        print(f"   • {length} chiffres: {count} ({percentage:.1f}%)")
    
    # Exemples de numéros
    print(f"\n📋 Exemples de numéros (10 premiers):")
    for i, phone in enumerate(phone_list[:10], 1):
        print(f"   {i:2d}. {phone}")

if __name__ == "__main__":
    analyze_excel_file()