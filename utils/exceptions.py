# -*- coding: utf-8 -*-
"""
Exceptions personnalisées pour l'application
"""


class ExcelWhatsAppException(Exception):
    """Exception de base pour l'application"""
    pass


class ConfigurationError(ExcelWhatsAppException):
    """Erreur de configuration"""
    pass


class ValidationError(ExcelWhatsAppException):
    """Erreur de validation des données"""
    pass


class APIError(ExcelWhatsAppException):
    """Erreur liée à l'API WhatsApp"""
    pass


class FileError(ExcelWhatsAppException):
    """Erreur liée aux fichiers"""
    pass


class SecurityError(ExcelWhatsAppException):
    """Erreur de sécurité"""
    pass