#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import re
import os

def analyze_excel_file():
    """Analyser le fichier Excel et corriger les numéros de téléphone"""
    
    file_path = "12 Aout 2025 18 COLONNES - SANS DOUBLONS.xlsx"
    
    if not os.path.exists(file_path):
        print(f"Erreur: Le fichier {file_path} n'existe pas")
        return
    
    try:
        # Lire le fichier Excel
        df = pd.read_excel(file_path)
        
        print(f"Structure du fichier Excel:")
        print(f"Nombre de lignes: {len(df)}")
        print(f"Nombre de colonnes: {len(df.columns)}")
        print(f"Colonnes: {list(df.columns)}")
        print("\n" + "="*50 + "\n")
        
        # Afficher les premières lignes pour comprendre la structure
        print("Premières lignes du fichier:")
        print(df.head())
        print("\n" + "="*50 + "\n")
        
        # Identifier les colonnes contenant des numéros de téléphone
        phone_columns = []
        for col in df.columns:
            # Vérifier si la colonne contient des numéros (commence par +, contient des chiffres)
            sample_values = df[col].dropna().head(10).astype(str)
            if any(re.search(r'[\+\d]', str(val)) and len(str(val)) > 8 for val in sample_values):
                phone_columns.append(col)
        
        print(f"Colonnes identifiées comme contenant des numéros: {phone_columns}")
        print("\n" + "="*50 + "\n")
        
        if not phone_columns:
            print("Aucune colonne de numéros détectée")
            return
        
        # Analyser le format de la première colonne de numéros
        first_col = phone_columns[0]
        print(f"Analyse du format de la première colonne '{first_col}':")
        
        first_col_sample = df[first_col].dropna().head(20)
        print("Échantillon des numéros de la première colonne:")
        for i, num in enumerate(first_col_sample):
            print(f"  {i+1}: {num}")
        
        # Détecter le format standard de la première colonne
        format_pattern = detect_phone_format(first_col_sample)
        print(f"\nFormat détecté: {format_pattern}")
        
        # Créer une copie du DataFrame pour les corrections
        df_corrected = df.copy()
        corrections_made = {}
        
        # Corriger chaque colonne de numéros selon le format de la première
        for col in phone_columns:
            if col != first_col:  # Ne pas corriger la première colonne (référence)
                print(f"\nCorrection de la colonne '{col}':")
                original_values = df[col].dropna()
                corrected_values = []
                corrections_count = 0
                
                for idx, phone in df[col].items():
                    if pd.isna(phone):
                        corrected_values.append(phone)
                        continue
                    
                    original_phone = str(phone)
                    corrected_phone = standardize_phone_number(original_phone, format_pattern)
                    
                    if original_phone != corrected_phone:
                        corrections_count += 1
                        print(f"  Ligne {idx+2}: '{original_phone}' → '{corrected_phone}'")
                    
                    df_corrected.at[idx, col] = corrected_phone
                
                corrections_made[col] = corrections_count
                print(f"  Total corrections pour '{col}': {corrections_count}")
        
        # Résumé des corrections
        print(f"\n" + "="*50)
        print("RÉSUMÉ DES CORRECTIONS:")
        total_corrections = sum(corrections_made.values())
        for col, count in corrections_made.items():
            print(f"  {col}: {count} corrections")
        print(f"  TOTAL: {total_corrections} corrections")
        
        if total_corrections > 0:
            # Sauvegarder le fichier corrigé
            output_file = "12 Aout 2025 18 COLONNES - NUMEROS CORRIGES.xlsx"
            df_corrected.to_excel(output_file, index=False)
            print(f"\nFichier corrigé sauvegardé: {output_file}")
        else:
            print("\nAucune correction nécessaire - tous les numéros sont déjà au bon format")
        
    except Exception as e:
        print(f"Erreur lors de l'analyse: {str(e)}")

def detect_phone_format(phone_sample):
    """Détecter le format des numéros de la première colonne"""
    formats = {}
    
    for phone in phone_sample:
        phone_str = str(phone).strip()
        
        # Analyser le format
        if phone_str.startswith('+'):
            if '+33' in phone_str:
                formats['+33_format'] = formats.get('+33_format', 0) + 1
            elif '+212' in phone_str:
                formats['+212_format'] = formats.get('+212_format', 0) + 1
            else:
                formats['other_plus'] = formats.get('other_plus', 0) + 1
        elif phone_str.startswith('0'):
            formats['zero_format'] = formats.get('zero_format', 0) + 1
        else:
            formats['no_prefix'] = formats.get('no_prefix', 0) + 1
    
    # Retourner le format le plus fréquent
    if formats:
        most_common = max(formats, key=formats.get)
        return most_common
    return 'unknown'

def standardize_phone_number(phone, target_format):
    """Standardiser un numéro selon le format cible"""
    if pd.isna(phone):
        return phone
    
    phone_str = str(phone).strip()
    
    # Nettoyer le numéro (enlever espaces, tirets, points)
    cleaned = re.sub(r'[\s\-\.]', '', phone_str)
    
    # Extraire les chiffres principaux
    digits = re.sub(r'[^\d]', '', cleaned)
    
    if target_format == '+33_format':
        # Format français +33
        if cleaned.startswith('+33'):
            return cleaned
        elif cleaned.startswith('0033'):
            return '+' + cleaned[2:]
        elif cleaned.startswith('33') and len(digits) >= 11:
            return '+' + cleaned
        elif cleaned.startswith('0') and len(digits) >= 10:
            return '+33' + cleaned[1:]
        elif len(digits) >= 9:
            return '+33' + digits
        
    elif target_format == '+212_format':
        # Format marocain +212
        if cleaned.startswith('+212'):
            return cleaned
        elif cleaned.startswith('00212'):
            return '+' + cleaned[2:]
        elif cleaned.startswith('212') and len(digits) >= 12:
            return '+' + cleaned
        elif cleaned.startswith('0') and len(digits) >= 10:
            return '+212' + cleaned[1:]
        elif len(digits) >= 9:
            return '+212' + digits
            
    elif target_format == 'zero_format':
        # Format avec 0 initial
        if not cleaned.startswith('0') and len(digits) >= 9:
            return '0' + digits
        elif cleaned.startswith('+33'):
            return '0' + cleaned[3:]
        elif cleaned.startswith('+212'):
            return '0' + cleaned[4:]
    
    # Si aucune règle ne s'applique, retourner tel quel
    return phone_str

if __name__ == "__main__":
    analyze_excel_file()