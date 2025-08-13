#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration optimisée pour 50 messages/jour avec nouveau numéro WhatsApp
Paramètres calculés pour maximiser l'efficacité tout en restant sécurisé
"""

def show_optimized_config():
    """Affiche la configuration optimisée pour 50 messages/jour"""
    
    print("🚀 CONFIGURATION OPTIMISÉE - 50 MESSAGES/JOUR")
    print("=" * 60)
    print("Configuration calculée pour nouveau numéro WhatsApp")
    print()
    
    print("📊 PARAMÈTRES PRINCIPAUX:")
    print("   • Limite quotidienne: 50 messages")
    print("   • Batch size: 5 messages par série")
    print("   • Nombre de batches: 10 batches/jour")
    print("   • Threads maximum: 2 threads")
    print()
    
    print("⏰ TIMING OPTIMISÉ:")
    print("   • Délai entre messages: 6-12 secondes")
    print("   • Délai entre batches: 4-6 minutes")
    print("   • Pause après chaque batch: 5 minutes")
    print("   • Temps total estimé: 1h30 pour 50 messages")
    print()
    
    print("🎯 CALCULS DE PERFORMANCE:")
    print("   • Messages par batch: 5")
    print("   • Temps par batch: ~1 min (5 msg × 12s)")
    print("   • Pause entre batches: 5 min")
    print("   • Temps par cycle: 6 min")
    print("   • 10 cycles = 60 min + pauses = ~90 min total")
    print()
    
    print("🛡️ SÉCURITÉ:")
    print("   • Délais aléatoires activés")
    print("   • Retry automatique (3 tentatives)")
    print("   • Gestion mémoire tous les 50 messages")
    print("   • Rate limiting intelligent")
    print()
    
    print("💡 AVANTAGES DE CETTE CONFIGURATION:")
    print("   ✅ Plus rapide que l'ultra-conservateur")
    print("   ✅ Sécurisé pour nouveau numéro")
    print("   ✅ Permet 50 messages en moins de 2h")
    print("   ✅ Comportement humain simulé")
    print("   ✅ Récupération d'erreurs robuste")
    print()
    
    print("🚦 RECOMMANDATIONS D'USAGE:")
    print("   1. Testez avec 5-10 messages d'abord")
    print("   2. Surveillez les taux de délivrance")
    print("   3. Utilisez entre 9h-17h en semaine")
    print("   4. Évitez les week-ends pour débuter")
    print("   5. Gardez des messages variés")

def calculate_daily_capacity():
    """Calcule la capacité théorique avec ces paramètres"""
    
    print("\n📈 CALCUL DE CAPACITÉ THÉORIQUE:")
    print("=" * 45)
    
    # Paramètres
    batch_size = 5
    msg_delay_avg = 9  # moyenne de 6-12s
    batch_delay_avg = 300  # 5 minutes
    
    # Calculs
    time_per_batch = (batch_size * msg_delay_avg) + batch_delay_avg  # en secondes
    time_per_batch_min = time_per_batch / 60  # en minutes
    
    batches_for_50 = 50 // batch_size
    total_time_min = batches_for_50 * time_per_batch_min
    total_time_hours = total_time_min / 60
    
    print(f"   • Temps par batch: {time_per_batch_min:.1f} min")
    print(f"   • Batches nécessaires: {batches_for_50}")
    print(f"   • Temps total: {total_time_min:.1f} min ({total_time_hours:.1f}h)")
    print()
    
    # Capacité horaire
    msgs_per_hour = 60 / time_per_batch_min * batch_size
    daily_capacity_8h = msgs_per_hour * 8
    
    print(f"   • Messages/heure: {msgs_per_hour:.1f}")
    print(f"   • Capacité sur 8h: {daily_capacity_8h:.0f} messages")
    print(f"   • Marge de sécurité: {((daily_capacity_8h - 50) / 50 * 100):.0f}%")

if __name__ == "__main__":
    show_optimized_config()
    calculate_daily_capacity()
    
    print("\n" + "=" * 60)
    print("✅ CONFIGURATION PRÊTE - VOUS POUVEZ LANCER L'ENVOI")
    print("=" * 60)
    print()
    print("🚀 Pour utiliser:")
    print("   python main_with_advanced_progress.py")
    print()
    print("⚠️  N'oubliez pas de:")
    print("   • Configurer votre nouveau numéro WhatsApp")
    print("   • Tester avec quelques messages d'abord")
    print("   • Surveiller les performances")