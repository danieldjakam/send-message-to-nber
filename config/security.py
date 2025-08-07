# -*- coding: utf-8 -*-
"""
Module de sécurité pour le chiffrement des données sensibles
"""
import base64
import json
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets
import os


class SecurityManager:
    """Gestionnaire de sécurité pour le chiffrement des données sensibles"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.key_file = self.config_dir / ".key"
        self.salt_file = self.config_dir / ".salt"
        self._fernet = None
    
    def _generate_key(self, password: str = None) -> Fernet:
        """Génère ou récupère la clé de chiffrement"""
        if password is None:
            # Utiliser un mot de passe basé sur l'identifiant unique de la machine
            password = self._get_machine_id()
        
        # Générer ou récupérer le salt
        if self.salt_file.exists():
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
        else:
            salt = secrets.token_bytes(32)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
            # Masquer le fichier sur Windows
            if os.name == 'nt':
                os.system(f'attrib +h "{self.salt_file}"')
        
        # Dériver la clé à partir du mot de passe
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)
    
    def _get_machine_id(self) -> str:
        """Obtient un identifiant unique de la machine"""
        try:
            import uuid
            return str(uuid.getnode())
        except:
            return "default_key_fallback"
    
    def encrypt_data(self, data: str) -> str:
        """Chiffre une chaîne de caractères"""
        if self._fernet is None:
            self._fernet = self._generate_key()
        
        encrypted_data = self._fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Déchiffre une chaîne de caractères"""
        if self._fernet is None:
            self._fernet = self._generate_key()
        
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self._fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception:
            # Si le déchiffrement échoue, retourner la donnée telle quelle
            # (pour la rétrocompatibilité)
            return encrypted_data
    
    def is_encrypted(self, data: str) -> bool:
        """Vérifie si une donnée est chiffrée"""
        try:
            # Essayer de décoder en base64
            decoded = base64.urlsafe_b64decode(data.encode())
            # Si c'est décodable et a une longueur cohérente, c'est probablement chiffré
            return len(decoded) > 32
        except:
            return False