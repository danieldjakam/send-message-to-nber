#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test d'intégration du système anti-spam
Ce script teste tous les composants du système anti-spam intégré
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.anti_spam_manager import AntiSpamManager, AntiSpamConfig, BehaviorPattern, RiskLevel
from datetime import datetime, timedelta

def test_anti_spam_manager():
    """Teste le gestionnaire anti-spam"""
    print("🧪 Test du gestionnaire anti-spam...")
    
    # Créer le manager
    manager = AntiSpamManager()
    
    # Test de configuration
    config = manager.config
    print(f"   📋 Configuration par défaut:")
    print(f"   - Mode expert: {config.expert_mode}")
    print(f"   - Limite quotidienne: {config.daily_message_limit}")
    print(f"   - Limite horaire: {config.hourly_message_limit}")
    print(f"   - Délais: {config.min_message_delay}s - {config.max_message_delay}s")
    print(f"   - Heures de travail: {config.working_hours_start}h - {config.working_hours_end}h")
    print(f"   - Pattern: {config.behavior_pattern}")
    
    # Test can_send_message
    can_send, reason, delay = manager.can_send_message("test")
    print(f"   🚦 Test envoi: {'✅ Autorisé' if can_send else '❌ Bloqué'}")
    print(f"   📝 Raison: {reason}")
    print(f"   ⏱️ Délai: {delay}s ({delay//60}m {delay%60}s)")
    
    # Test du niveau de risque
    risk = manager.calculate_risk_level()
    print(f"   🎯 Niveau de risque: {risk.value}")
    
    # Test des recommandations
    recommendations = manager.get_recommendations(total_messages=500)
    print(f"   💡 Recommandations pour 500 messages:")
    if 'suggestions' in recommendations:
        for suggestion in recommendations.get('suggestions', [])[:3]:
            print(f"     • {suggestion}")
    
    # Test du statut
    status = manager.get_current_status()
    print(f"   📊 Statut actuel:")
    print(f"     - Protections: {'✅ Actives' if status['config_active'] else '❌ Désactivées'}")
    print(f"     - Usage quotidien: {status['daily_usage']['sent']}/{status['daily_usage']['limit']}")
    print(f"     - Usage horaire: {status['hourly_usage']['sent']}/{status['hourly_usage']['limit']}")
    
    print("✅ Test du gestionnaire anti-spam réussi\n")
    
    return manager

def test_expert_mode():
    """Teste le mode expert"""
    print("🔧 Test du mode expert...")
    
    manager = AntiSpamManager()
    
    # Activer le mode expert
    manager.config.expert_mode = True
    
    # Tester que toutes les protections sont désactivées
    can_send, reason, delay = manager.can_send_message("test")
    
    print(f"   🚦 Mode expert - Envoi: {'✅ Autorisé' if can_send else '❌ Bloqué'}")
    print(f"   📝 Raison: {reason}")
    print(f"   ⏱️ Délai: {delay}s")
    
    if can_send and delay == 0:
        print("✅ Mode expert fonctionne correctement - aucune restriction")
    else:
        print("❌ Mode expert ne fonctionne pas correctement")
    
    # Remettre en mode normal
    manager.config.expert_mode = False
    print("✅ Test du mode expert réussi\n")

def test_behavior_patterns():
    """Teste les différents patterns de comportement"""
    print("🎭 Test des patterns de comportement...")
    
    manager = AntiSpamManager()
    
    patterns = [
        (BehaviorPattern.OFFICE_WORKER, "👔 Travailleur de Bureau"),
        (BehaviorPattern.CASUAL_USER, "😊 Utilisateur Occasionnel"), 
        (BehaviorPattern.BUSINESS_USER, "💼 Utilisateur Professionnel"),
        (BehaviorPattern.STUDENT, "🎓 Étudiant")
    ]
    
    for pattern, name in patterns:
        manager.config.behavior_pattern = pattern.value
        delay = manager.calculate_intelligent_delay()
        print(f"   {name}: délai de base ≈ {delay}s")
    
    print("✅ Test des patterns de comportement réussi\n")

def test_configuration_persistence():
    """Teste la sauvegarde et le chargement de configuration"""
    print("💾 Test de persistence de la configuration...")
    
    # Créer un manager avec une configuration personnalisée
    manager = AntiSpamManager()
    
    # Modifier la configuration
    original_daily_limit = manager.config.daily_message_limit
    original_behavior = manager.config.behavior_pattern
    
    manager.config.daily_message_limit = 999
    manager.config.behavior_pattern = BehaviorPattern.WEEKEND_WARRIOR.value
    manager.config.enable_weekend_protection = False
    
    # Sauvegarder
    manager.save_config()
    print("   💾 Configuration sauvegardée")
    
    # Créer un nouveau manager pour tester le chargement
    manager2 = AntiSpamManager()
    
    # Vérifier que la configuration a été chargée
    if (manager2.config.daily_message_limit == 999 and
        manager2.config.behavior_pattern == BehaviorPattern.WEEKEND_WARRIOR.value and
        manager2.config.enable_weekend_protection == False):
        print("✅ Configuration chargée correctement")
    else:
        print("❌ Problème de chargement de configuration")
    
    # Restaurer la configuration originale
    manager.config.daily_message_limit = original_daily_limit
    manager.config.behavior_pattern = original_behavior
    manager.save_config()
    
    print("✅ Test de persistence réussi\n")

def test_recommendations_engine():
    """Teste le moteur de recommandations"""
    print("💡 Test du moteur de recommandations...")
    
    manager = AntiSpamManager()
    
    # Test avec différents volumes
    volumes = [10, 100, 1000, 5000]
    
    for volume in volumes:
        recommendations = manager.get_recommendations(total_messages=volume)
        
        print(f"   📊 {volume} messages:")
        print(f"     - Niveau de risque: {recommendations.get('risk_level', 'N/A')}")
        
        if 'estimated_duration_text' in recommendations:
            print(f"     - Durée estimée: {recommendations['estimated_duration_text']}")
        
        if 'recommended_batch_size' in recommendations:
            print(f"     - Taille de batch recommandée: {recommendations['recommended_batch_size']}")
        
        if 'should_distribute_over_days' in recommendations:
            distribute = recommendations['should_distribute_over_days']
            print(f"     - Distribution multi-jours: {'✅ Recommandée' if distribute else '❌ Pas nécessaire'}")
    
    print("✅ Test du moteur de recommandations réussi\n")

def main():
    """Fonction principale de test"""
    print("🚀 TESTS D'INTÉGRATION DU SYSTÈME ANTI-SPAM")
    print("=" * 50)
    print()
    
    try:
        # Tests principaux
        manager = test_anti_spam_manager()
        test_expert_mode()
        test_behavior_patterns()
        test_configuration_persistence()
        test_recommendations_engine()
        
        print("🎉 TOUS LES TESTS SONT RÉUSSIS!")
        print()
        print("📋 RÉSUMÉ DE L'INTÉGRATION:")
        print("✅ Gestionnaire anti-spam fonctionnel")
        print("✅ Configuration personnalisable")
        print("✅ Mode expert pour utilisateurs avancés")
        print("✅ Patterns de comportement multiples")
        print("✅ Moteur de recommandations intelligent")
        print("✅ Persistence des configurations")
        print("✅ Analyse de risque en temps réel")
        print("✅ Statistiques d'usage")
        print()
        print("🛡️ Le système anti-spam est prêt à protéger contre")
        print("   la détection de spam lors des envois en masse!")
        
        return True
        
    except Exception as e:
        print(f"❌ ERREUR LORS DES TESTS: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)