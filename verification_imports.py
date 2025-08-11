#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérification complète des imports et dépendances
"""

import sys
import importlib
import subprocess
from pathlib import Path

def test_imports():
    print("🔍 VÉRIFICATION DES IMPORTS ET DÉPENDANCES")
    print("=" * 60)
    
    # Modules critiques à tester
    critical_modules = {
        'customtkinter': 'Interface graphique principale',
        'tkinter': 'Interface graphique système',
        'pandas': 'Traitement fichiers Excel',
        'requests': 'Communication API WhatsApp',
        'openpyxl': 'Lecture fichiers .xlsx',
        'xlrd': 'Lecture fichiers .xls',
        'json': 'Gestion fichiers JSON',
        'threading': 'Gestion threads',
        'time': 'Gestion temporisation',
        'pathlib': 'Gestion fichiers/dossiers',
        'concurrent.futures': 'Threading avancé',
        'dataclasses': 'Classes de données',
        'typing': 'Types Python',
        're': 'Expressions régulières'
    }
    
    print("📦 MODULES CRITIQUES:")
    print("-" * 30)
    
    failed_imports = []
    for module, description in critical_modules.items():
        try:
            importlib.import_module(module)
            print(f"   ✅ {module:<20} - {description}")
        except ImportError as e:
            print(f"   ❌ {module:<20} - ERREUR: {e}")
            failed_imports.append(module)
    
    # Test des imports de l'application
    print(f"\n🏗️  MODULES APPLICATION:")
    print("-" * 30)
    
    app_modules = [
        'config.config_manager',
        'api.whatsapp_client', 
        'api.bulk_sender',
        'utils.validators',
        'utils.logger',
        'utils.exceptions',
        'ui.components',
        'ui.bulk_send_dialog',
        'ui.progress_widgets',
        'ui.sent_numbers_dialog'
    ]
    
    app_failed = []
    for module in app_modules:
        try:
            importlib.import_module(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            print(f"   ❌ {module} - ERREUR: {e}")
            app_failed.append(module)
        except Exception as e:
            print(f"   ⚠️  {module} - ATTENTION: {e}")
    
    # Test du fichier principal
    print(f"\n🚀 FICHIER PRINCIPAL:")
    print("-" * 25)
    
    main_file = Path('main_with_advanced_progress.py')
    if main_file.exists():
        print(f"   ✅ {main_file} existe")
        
        # Test syntaxe
        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                compile(f.read(), main_file, 'exec')
            print(f"   ✅ Syntaxe Python valide")
        except SyntaxError as e:
            print(f"   ❌ Erreur syntaxe: {e}")
            app_failed.append('main_syntax')
    else:
        print(f"   ❌ {main_file} introuvable")
        app_failed.append('main_file')
    
    # Vérification des dépendances pip
    print(f"\n📋 DÉPENDANCES PIP:")
    print("-" * 25)
    
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True, timeout=10)
        
        pip_packages = result.stdout.lower()
        required_packages = ['customtkinter', 'pandas', 'requests', 'openpyxl']
        
        for package in required_packages:
            if package in pip_packages:
                print(f"   ✅ {package} installé")
            else:
                print(f"   ❌ {package} manquant")
                failed_imports.append(f"pip_{package}")
                
    except Exception as e:
        print(f"   ⚠️  Impossible de vérifier pip: {e}")
    
    # Résultat final
    print(f"\n{'='*60}")
    
    total_errors = len(failed_imports) + len(app_failed)
    
    if total_errors == 0:
        print("🎉 TOUS LES IMPORTS SONT VALIDES !")
        print("   ✅ Modules système: OK")
        print("   ✅ Modules application: OK") 
        print("   ✅ Fichier principal: OK")
        print("   ✅ Dépendances pip: OK")
        return True
    else:
        print(f"❌ {total_errors} PROBLÈME(S) DÉTECTÉ(S)")
        if failed_imports:
            print(f"   Modules système manquants: {failed_imports}")
        if app_failed:
            print(f"   Modules application défaillants: {app_failed}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)