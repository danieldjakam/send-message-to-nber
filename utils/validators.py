# -*- coding: utf-8 -*-
"""
Utilitaires de validation des données
"""
import re
from typing import List, Tuple, Optional
import pandas as pd


class PhoneValidator:
    """Validateur de numéros de téléphone"""
    
    # Patterns pour différents formats de numéros
    PATTERNS = {
        'international': r'^\+[1-9]\d{1,14}$',
        'french_mobile': r'^(?:\+33|0033|33)?[67]\d{8}$',
        'french_landline': r'^(?:\+33|0033|33)?[1-5]\d{8}$',
        'cameroon': r'^(?:\+237|237)?[6-9]\d{8}$',  # Numéros camerounais
        'whatsapp_format': r'^\d{10,15}$'  # Format WhatsApp sans préfixes
    }
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Vérifie si un numéro de téléphone est valide"""
        if not phone or not isinstance(phone, str):
            return False
        
        # Nettoyer le numéro
        cleaned = PhoneValidator.clean_phone(phone)
        if not cleaned:
            return False
        
        # Vérifier avec les différents patterns
        for pattern in PhoneValidator.PATTERNS.values():
            if re.match(pattern, cleaned):
                return True
        
        return False
    
    @staticmethod
    def clean_phone(phone: str) -> str:
        """Nettoie un numéro de téléphone"""
        if not phone or not isinstance(phone, str):
            return ""
        
        # Supprimer tous les caractères non numériques sauf +
        cleaned = re.sub(r'[^\d+]', '', str(phone).strip())
        
        # Gérer les formats français
        if cleaned.startswith('0033'):
            cleaned = '+33' + cleaned[4:]
        elif cleaned.startswith('33') and len(cleaned) > 10:
            cleaned = '+33' + cleaned[2:]
        elif cleaned.startswith('0') and len(cleaned) == 10:
            # Numéro français sans indicatif
            cleaned = '+33' + cleaned[1:]
        
        # Gérer les formats camerounais
        elif cleaned.startswith('0237'):
            cleaned = '+237' + cleaned[4:]
        elif cleaned.startswith('237') and len(cleaned) >= 11:
            # Ajouter le + pour les numéros camerounais
            cleaned = '+237' + cleaned[3:]
        
        return cleaned
    
    @staticmethod
    def format_for_whatsapp(phone: str) -> str:
        """Formate un numéro pour WhatsApp (sans + ni espaces)"""
        cleaned = PhoneValidator.clean_phone(phone)
        if cleaned.startswith('+'):
            return cleaned[1:]
        return cleaned
    
    @staticmethod
    def validate_phone_list(phones: List[str]) -> Tuple[List[str], List[str]]:
        """Valide une liste de numéros"""
        valid_phones = []
        invalid_phones = []
        
        for phone in phones:
            if PhoneValidator.is_valid_phone(phone):
                valid_phones.append(PhoneValidator.format_for_whatsapp(phone))
            else:
                invalid_phones.append(phone)
        
        return valid_phones, invalid_phones


class DataValidator:
    """Validateur de données générales"""
    
    @staticmethod
    def validate_excel_file(file_path: str) -> Tuple[bool, str]:
        """Valide un fichier Excel"""
        try:
            if not file_path:
                return False, "Aucun fichier sélectionné"
            
            # Vérifier l'extension
            if not file_path.lower().endswith(('.xlsx', '.xls')):
                return False, "Le fichier doit être un fichier Excel (.xlsx ou .xls)"
            
            # Essayer de lire le fichier
            df = pd.read_excel(file_path)
            
            if df.empty:
                return False, "Le fichier Excel est vide"
            
            if len(df.columns) == 0:
                return False, "Le fichier Excel ne contient aucune colonne"
            
            return True, f"Fichier valide: {len(df)} lignes, {len(df.columns)} colonnes"
        
        except FileNotFoundError:
            return False, "Fichier non trouvé"
        except PermissionError:
            return False, "Pas d'autorisation pour lire le fichier"
        except Exception as e:
            return False, f"Erreur lors de la lecture du fichier: {str(e)}"
    
    @staticmethod
    def validate_image_file(file_path: str) -> Tuple[bool, str]:
        """Valide un fichier image"""
        if not file_path:
            return True, "Aucune image sélectionnée"
        
        try:
            import os
            
            if not os.path.exists(file_path):
                return False, "Fichier image non trouvé"
            
            # Vérifier l'extension
            valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext not in valid_extensions:
                return False, f"Format d'image non supporté: {file_ext}"
            
            # Vérifier la taille du fichier (max 5MB)
            file_size = os.path.getsize(file_path)
            max_size = 5 * 1024 * 1024  # 5MB
            
            if file_size > max_size:
                return False, f"Fichier trop volumineux: {file_size / 1024 / 1024:.1f}MB (max 5MB)"
            
            return True, f"Image valide: {file_size / 1024:.1f}KB"
        
        except Exception as e:
            return False, f"Erreur lors de la validation de l'image: {str(e)}"
    
    @staticmethod
    def validate_api_credentials(instance_id: str, token: str) -> Tuple[bool, str]:
        """Valide les identifiants API"""
        errors = []
        
        if not instance_id or not instance_id.strip():
            errors.append("Instance ID manquant")
        elif len(instance_id.strip()) < 5:
            errors.append("Instance ID trop court")
        
        if not token or not token.strip():
            errors.append("Token manquant")
        elif len(token.strip()) < 10:
            errors.append("Token trop court")
        
        if errors:
            return False, "; ".join(errors)
        
        return True, "Identifiants API valides"