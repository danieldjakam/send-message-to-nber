#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cx_Freeze import setup, Executable
import sys
import os

# Options de build
build_options = {
    'packages': [
        'customtkinter', 
        'pandas', 
        'requests', 
        'tkinter', 
        'openpyxl',
        'base64',
        'json',
        'time'
    ],
    'excludes': [
        'matplotlib', 
        'scipy', 
        'numpy.f2py',
        'unittest',
        'test'
    ],
    'include_files': [
        # Inclure les fichiers CustomTkinter
        ('requirements.txt', 'requirements.txt')
    ],
    'optimize': 2,
    'zip_include_packages': ['*'],
    'zip_exclude_packages': []
}

# Options pour l'exécutable
executable_options = {
    'target_name': 'ExcelWhatsApp',
    'copyright': '© 2024 Excel WhatsApp Sender',
    'icon': None  # Vous pouvez ajouter un fichier .ico ici
}

# Configuration des exécutables selon la plateforme
if sys.platform == "win32":
    # Configuration Windows (.exe)
    executables = [
        Executable(
            "main.py",
            base="Win32GUI",  # Interface graphique sans console
            **executable_options
        )
    ]
elif sys.platform == "darwin":
    # Configuration macOS (.app)
    executables = [
        Executable(
            "main.py",
            base=None,
            **executable_options
        )
    ]
else:
    # Configuration Linux
    executables = [
        Executable(
            "main.py",
            base=None,
            **executable_options
        )
    ]

setup(
    name="Excel WhatsApp Sender",
    version="1.0.0",
    description="Application pour envoyer des messages WhatsApp depuis Excel via UltraMsg API",
    author="Votre Nom",
    author_email="votre.email@example.com",
    options={'build_exe': build_options},
    executables=executables
)