# Makefile pour Excel WhatsApp Sender

# Variables
PYTHON = python3.11
APP_NAME = ExcelWhatsAppSender
MAIN_FILE = main.py

# Couleurs pour les messages
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: help install clean build-pyinstaller build-cx-freeze build-all test run

help: ## Affiche l'aide
	@echo "$(YELLOW)Excel WhatsApp Sender - Commandes de build$(NC)"
	@echo "================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Installe les dépendances
	@echo "$(YELLOW)📦 Installation des dépendances...$(NC)"
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install pyinstaller cx_freeze
	@echo "$(GREEN)✅ Dépendances installées$(NC)"

clean: ## Nettoie les fichiers de build
	@echo "$(YELLOW)🧹 Nettoyage des fichiers de build...$(NC)"
	rm -rf build/ dist/ __pycache__/ *.pyc *.pyo *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Nettoyage terminé$(NC)"

test: ## Lance l'application en mode développement
	@echo "$(YELLOW)🧪 Test de l'application...$(NC)"
	$(PYTHON) $(MAIN_FILE)

run: test ## Alias pour test

build-pyinstaller: clean ## Compile avec PyInstaller
	@echo "$(YELLOW)🔨 Compilation avec PyInstaller...$(NC)"
	pyinstaller --name=$(APP_NAME) \
		--onefile \
		--windowed \
		--add-data="requirements.txt:." \
		--hidden-import=customtkinter \
		--hidden-import=pandas \
		--hidden-import=openpyxl \
		--hidden-import=requests \
		--exclude-module=matplotlib \
		--exclude-module=scipy \
		$(MAIN_FILE)
	@echo "$(GREEN)✅ Compilation PyInstaller terminée$(NC)"
	@ls -la dist/

build-cx-freeze: clean ## Compile avec cx_Freeze
	@echo "$(YELLOW)🔨 Compilation avec cx_Freeze...$(NC)"
	$(PYTHON) setup.py build
	@echo "$(GREEN)✅ Compilation cx_Freeze terminée$(NC)"
	@ls -la build/

build-spec: clean ## Compile avec le fichier .spec
	@echo "$(YELLOW)🔨 Compilation avec fichier .spec...$(NC)"
	pyinstaller build.spec
	@echo "$(GREEN)✅ Compilation .spec terminée$(NC)"
	@ls -la dist/

build-dmg: build-pyinstaller ## Crée un DMG sur macOS (après PyInstaller)
ifeq ($(shell uname), Darwin)
	@echo "$(YELLOW)📦 Création du fichier .dmg...$(NC)"
	hdiutil create -volname "Excel WhatsApp Sender" \
		-srcfolder dist/ \
		-ov -format UDZO \
		"dist/Excel_WhatsApp_Sender.dmg"
	@echo "$(GREEN)✅ DMG créé: dist/Excel_WhatsApp_Sender.dmg$(NC)"
else
	@echo "$(RED)❌ Création DMG disponible uniquement sur macOS$(NC)"
endif

build-all: ## Compile avec toutes les méthodes
	@echo "$(YELLOW)🚀 Compilation avec toutes les méthodes...$(NC)"
	$(MAKE) build-pyinstaller
	$(MAKE) build-cx-freeze
ifeq ($(shell uname), Darwin)
	$(MAKE) build-dmg
endif
	@echo "$(GREEN)🎉 Toutes les compilations terminées !$(NC)"

auto-build: ## Script de build automatique interactif
	@echo "$(YELLOW)🤖 Lancement du script de build automatique...$(NC)"
	$(PYTHON) build.py

package: build-pyinstaller ## Package l'application (alias pour build-pyinstaller)
	@echo "$(GREEN)📦 Application packagée dans dist/$(NC)"

size: ## Affiche la taille des fichiers générés
	@echo "$(YELLOW)📏 Taille des fichiers générés:$(NC)"
	@if [ -d "dist" ]; then \
		du -sh dist/* 2>/dev/null | sort -hr || echo "Aucun fichier dans dist/"; \
	else \
		echo "Dossier dist/ inexistant. Lancez d'abord une compilation."; \
	fi

info: ## Affiche les informations système
	@echo "$(YELLOW)ℹ️  Informations système:$(NC)"
	@echo "OS: $(shell uname -s)"
	@echo "Architecture: $(shell uname -m)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Répertoire: $(shell pwd)"
	@echo "Fichiers Python: $(shell find . -name "*.py" | wc -l | tr -d ' ')"

# Règle par défaut
all: help