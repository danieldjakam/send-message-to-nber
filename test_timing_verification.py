#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de vérification du timing exact
"""

from api.bulk_sender import BulkSender
from api.whatsapp_client import WhatsAppClient

def test_timing_calculation():
    print("⏰ VÉRIFICATION DU TIMING")
    print("=" * 50)
    
    # Créer une instance
    client = WhatsAppClient("test", "test")
    sender = BulkSender(client)
    
    # Afficher la configuration
    print("🔧 CONFIGURATION ACTUELLE:")
    print(f"   💬 Messages par série: {sender.message_burst_limit}")
    print(f"   ⏱️  Délai entre messages: {sender.message_delay} secondes ({sender.message_delay/60:.1f} min)")
    print(f"   ⏸️  Pause entre séries: {sender.burst_pause_duration} secondes ({sender.burst_pause_duration/60:.1f} min)")
    
    # Calcul détaillé
    print("\n📊 CALCUL DÉTAILLÉ DU TIMING:")
    
    # Pour une série de 5 messages
    messages_per_serie = sender.message_burst_limit
    delay_between_messages = sender.message_delay
    pause_between_series = sender.burst_pause_duration
    
    # Temps pour envoyer les messages (4 intervalles entre 5 messages)
    intervals_count = messages_per_serie - 1
    time_for_messages = intervals_count * delay_between_messages
    
    # Temps total par série
    total_time_per_serie = time_for_messages + pause_between_series
    
    print(f"   📤 Messages dans une série: {messages_per_serie}")
    print(f"   🔢 Intervalles entre messages: {intervals_count}")
    print(f"   ⏱️  Temps pour les messages: {intervals_count} × {delay_between_messages}s = {time_for_messages}s ({time_for_messages/60:.1f} min)")
    print(f"   ⏸️  Pause entre séries: {pause_between_series}s ({pause_between_series/60:.1f} min)")
    print(f"   🕒 TEMPS TOTAL PAR SÉRIE: {total_time_per_serie}s ({total_time_per_serie/60:.1f} min)")
    
    # Performance horaire et quotidienne
    print("\n📈 PERFORMANCE:")
    
    # Messages par heure
    minutes_per_hour = 60
    series_per_hour = minutes_per_hour * 60 / total_time_per_serie
    messages_per_hour = series_per_hour * messages_per_serie
    
    # Messages par jour
    hours_per_day = 24
    messages_per_day = messages_per_hour * hours_per_day
    
    print(f"   🕐 Séries par heure: {series_per_hour:.2f}")
    print(f"   📤 Messages par heure: {messages_per_hour:.0f}")
    print(f"   📅 Messages par jour (24h): {messages_per_day:.0f}")
    
    # Validation du timing souhaité
    print(f"\n✅ VALIDATION:")
    target_time = 7  # minutes souhaitées
    actual_time = total_time_per_serie / 60
    
    if abs(actual_time - target_time) <= 0.5:  # Tolérance de 30 secondes
        print(f"   🎯 PARFAIT: {actual_time:.1f} min ≈ {target_time} min (objectif atteint)")
        validation_status = "✅ SUCCÈS"
    else:
        print(f"   ⚠️  ÉCART: {actual_time:.1f} min vs {target_time} min (écart: {abs(actual_time - target_time):.1f} min)")
        validation_status = "⚠️ AJUSTEMENT NÉCESSAIRE"
    
    print(f"\n{validation_status}")
    print("=" * 50)
    
    return {
        'messages_per_serie': messages_per_serie,
        'time_per_serie_minutes': actual_time,
        'messages_per_hour': int(messages_per_hour),
        'messages_per_day': int(messages_per_day),
        'target_achieved': abs(actual_time - target_time) <= 0.5
    }

if __name__ == "__main__":
    result = test_timing_calculation()