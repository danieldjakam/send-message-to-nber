#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def install_build_dependencies():
    """Installer les dépendances nécessaires pour la compilation"""
    print("📦 Installation des dépendances de build...")
    
    dependencies = [
        'pyinstaller',
        'cx_Freeze',
        'customtkinter',
        'pandas',
        'openpyxl',
        'requests'
    ]
    
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✅ {dep} installé")
        except subprocess.CalledProcessError:
            print(f"❌ Erreur lors de l'installation de {dep}")
            return False
    
    return True

def build_with_pyinstaller():
    """Compiler avec PyInstaller"""
    print(f"🔨 Compilation avec PyInstaller pour {platform.system()}...")
    
    try:
        # Nettoyer les anciens builds
        for folder in ['build', 'dist', '__pycache__']:
            if os.path.exists(folder):
                shutil.rmtree(folder)
                print(f"🧹 Dossier {folder} nettoyé")
        
        # Commande PyInstaller
        cmd = [
            'pyinstaller',
            '--name=ExcelWhatsAppSender',
            '--onefile',
            '--windowed',
            '--add-data=requirements.txt:.',
            '--hidden-import=customtkinter',
            '--hidden-import=pandas',
            '--hidden-import=openpyxl',
            '--hidden-import=requests',
            '--exclude-module=matplotlib',
            '--exclude-module=scipy',
            'main.py'
        ]
        
        subprocess.check_call(cmd)
        print("✅ Compilation PyInstaller réussie !")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur PyInstaller: {e}")
        return False

def build_with_cx_freeze():
    """Compiler avec cx_Freeze"""
    print(f"🔨 Compilation avec cx_Freeze pour {platform.system()}...")
    
    try:
        subprocess.check_call([sys.executable, 'setup.py', 'build'])
        print("✅ Compilation cx_Freeze réussie !")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur cx_Freeze: {e}")
        return False

def create_dmg_macos():
    """Créer un fichier .dmg sur macOS"""
    if platform.system() != 'Darwin':
        print("⚠️ Création DMG disponible uniquement sur macOS")
        return False
    
    print("📦 Création du fichier .dmg...")
    
    try:
        app_name = "Excel WhatsApp Sender"
        dmg_name = f"{app_name.replace(' ', '_')}.dmg"
        
        # Vérifier si l'application existe
        app_path = f"dist/{app_name}.app"
        if not os.path.exists(app_path):
            print(f"❌ Application non trouvée: {app_path}")
            return False
        
        # Créer le DMG
        cmd = [
            'hdiutil', 'create', '-volname', app_name,
            '-srcfolder', 'dist/',
            '-ov', '-format', 'UDZO',
            f'dist/{dmg_name}'
        ]
        
        subprocess.check_call(cmd)
        print(f"✅ DMG créé: dist/{dmg_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur création DMG: {e}")
        return False

def main():
    """Fonction principale de build"""
    print("🚀 Script de compilation Excel WhatsApp Sender")
    print("=" * 50)
    
    # Installer les dépendances
    if not install_build_dependencies():
        print("❌ Échec de l'installation des dépendances")
        return
    
    # Choisir la méthode de compilation
    print("\\nMéthodes de compilation disponibles:")
    print("1. PyInstaller (recommandé)")
    print("2. cx_Freeze")
    
    choice = input("\\nChoisissez une méthode (1 ou 2): ").strip()
    
    success = False
    if choice == "1":
        success = build_with_pyinstaller()
    elif choice == "2":
        success = build_with_cx_freeze()
    else:
        print("❌ Choix invalide")
        return
    
    if success:
        print("\\n🎉 Compilation terminée avec succès !")
        
        # Créer DMG sur macOS
        if platform.system() == 'Darwin':
            create_dmg = input("\\nCréer un fichier .dmg ? (o/n): ").strip().lower()
            if create_dmg in ['o', 'oui', 'y', 'yes']:
                create_dmg_macos()
        
        print(f"\\n📁 Fichiers générés dans le dossier 'dist/'")
        
        # Lister les fichiers créés
        if os.path.exists('dist'):
            print("\\nFichiers créés:")
            for file in os.listdir('dist'):
                size = os.path.getsize(f'dist/{file}') / (1024*1024)  # MB
                print(f"  📄 {file} ({size:.1f} MB)")
    
    else:
        print("❌ Compilation échouée")

if __name__ == "__main__":
    main()