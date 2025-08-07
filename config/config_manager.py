# -*- coding: utf-8 -*-
"""
Gestionnaire de configuration sécurisé
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from .security import SecurityManager


class ConfigManager:
    """Gestionnaire de configuration avec chiffrement des données sensibles"""
    
    # Clés qui doivent être chiffrées
    ENCRYPTED_KEYS = {'token', 'instance_id'}
    
    def __init__(self, config_file: Path = None):
        if config_file is None:
            config_file = Path.home() / ".excel_whatsapp" / "config.json"
        
        self.config_file = config_file
        self.config_dir = config_file.parent
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.security_manager = SecurityManager(self.config_dir)
        self._config = {}
        self.load_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration"""
        value = self._config.get(key, default)
        
        # Déchiffrer si c'est une clé sensible
        if key in self.ENCRYPTED_KEYS and value and isinstance(value, str):
            if self.security_manager.is_encrypted(value):
                try:
                    value = self.security_manager.decrypt_data(value)
                except Exception:
                    # Si le déchiffrement échoue, garder la valeur originale
                    pass
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Définit une valeur de configuration"""
        # Chiffrer si c'est une clé sensible
        if key in self.ENCRYPTED_KEYS and value and isinstance(value, str):
            value = self.security_manager.encrypt_data(value)
        
        self._config[key] = value
        self.save_config()
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """Met à jour plusieurs valeurs de configuration"""
        for key, value in config_dict.items():
            if key in self.ENCRYPTED_KEYS and value and isinstance(value, str):
                value = self.security_manager.encrypt_data(value)
            self._config[key] = value
        self.save_config()
    
    def load_config(self) -> None:
        """Charge la configuration depuis le fichier"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                self._config = {}
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
            self._config = {}
    
    def save_config(self) -> None:
        """Sauvegarde la configuration dans le fichier"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")
    
    def get_all(self) -> Dict[str, Any]:
        """Récupère toute la configuration (avec déchiffrement)"""
        result = {}
        for key, value in self._config.items():
            result[key] = self.get(key)
        return result
    
    def clear_sensitive_data(self) -> None:
        """Efface les données sensibles de la configuration"""
        for key in self.ENCRYPTED_KEYS:
            if key in self._config:
                del self._config[key]
        self.save_config()