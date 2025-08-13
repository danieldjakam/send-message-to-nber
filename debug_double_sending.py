#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour identifier pourquoi les messages sont envoyés en double
"""

import json
from pathlib import Path
from api.bulk_sender import BulkSender
from api.whatsapp_client import WhatsAppClient

def debug_double_sending():
    """Diagnostique le problème d'envoi en double"""
    print("🔍 Diagnostic des envois en double")
    print("=" * 50)
    
    # Créer un client temporaire
    temp_client = WhatsAppClient("test", "test")
    bulk_sender = BulkSender(temp_client)
    
    # Vérifier le fichier des numéros envoyés
    sent_numbers_file = bulk_sender.sent_numbers_file
    print(f"📁 Fichier des numéros envoyés: {sent_numbers_file}")
    
    if sent_numbers_file.exists():
        try:
            with open(sent_numbers_file, 'r', encoding='utf-8') as f:
                sent_data = json.load(f)
            
            print(f"📊 Numéros déjà contactés: {len(sent_data)} numéros")
            
            # Afficher les 10 derniers numéros
            if sent_data:
                print(f"\n📋 Derniers numéros contactés:")
                for i, phone in enumerate(list(sent_data)[-10:]):
                    print(f"   {i+1:2d}. {phone}")
        except Exception as e:
            print(f"❌ Erreur lecture fichier: {e}")
    else:
        print("📄 Aucun fichier de numéros envoyés trouvé")
    
    # Vérifier les sessions sauvegardées
    sessions_dir = bulk_sender.sessions_dir
    print(f"\n📁 Dossier des sessions: {sessions_dir}")
    
    if sessions_dir.exists():
        session_files = list(sessions_dir.glob("*.json"))
        print(f"📊 Sessions sauvegardées: {len(session_files)}")
        
        for session_file in session_files[-5:]:  # 5 dernières sessions
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                print(f"\n📋 Session: {session_file.name}")
                print(f"   • ID: {session_data.get('session_id', 'N/A')}")
                print(f"   • Total messages: {session_data.get('total_messages', 'N/A')}")
                print(f"   • Terminé: {session_data.get('completed', 'N/A')}")
                print(f"   • Réussis: {session_data.get('successful', 'N/A')}")
                print(f"   • Échoués: {session_data.get('failed', 'N/A')}")
                print(f"   • Annulé: {session_data.get('cancelled', False)}")
                print(f"   • Fini: {session_data.get('finished', False)}")
                print(f"   • Batch actuel: {session_data.get('current_batch', 'N/A')}")
                
            except Exception as e:
                print(f"❌ Erreur lecture session {session_file.name}: {e}")
    else:
        print("📄 Aucun dossier de sessions trouvé")
    
    # Diagnostics supplémentaires
    print(f"\n🔧 Configuration actuelle:")
    print(f"   • Taille batch: {bulk_sender.batch_size}")
    print(f"   • Délai entre messages: {bulk_sender.message_delay}s")
    print(f"   • Délai entre batches: {bulk_sender.batch_delay}s")
    print(f"   • Limite quotidienne: {bulk_sender.max_daily_limit}")
    
    print(f"\n🚨 PROBLÈMES POTENTIELS:")
    print(f"   1. Sessions non marquées comme terminées -> reprise infinie")
    print(f"   2. Numéros pas correctement normalisés -> pas de déduplication")
    print(f"   3. Fichier sent_numbers.json corrompu ou effacé")
    print(f"   4. Plusieurs instances de l'app qui tournent en parallèle")
    
    print(f"\n💡 SOLUTIONS:")
    print(f"   1. Vérifiez qu'une seule instance de l'app tourne")
    print(f"   2. Supprimez les sessions non terminées si nécessaire")
    print(f"   3. Vérifiez la cohérence du fichier sent_numbers.json")

def clean_old_sessions():
    """Nettoie les anciennes sessions non terminées"""
    print(f"\n🧹 Nettoyage des sessions non terminées")
    print("-" * 40)
    
    temp_client = WhatsAppClient("test", "test")
    bulk_sender = BulkSender(temp_client)
    sessions_dir = bulk_sender.sessions_dir
    
    if not sessions_dir.exists():
        print("📄 Aucun dossier de sessions trouvé")
        return
    
    session_files = list(sessions_dir.glob("*.json"))
    cleaned_count = 0
    
    for session_file in session_files:
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            finished = session_data.get('finished', False)
            cancelled = session_data.get('cancelled', False)
            
            # Supprimer les sessions non terminées ET non annulées (potentiellement problématiques)
            if not finished and not cancelled:
                print(f"🗑️ Suppression session non terminée: {session_file.name}")
                session_file.unlink()
                cleaned_count += 1
            else:
                print(f"✅ Session OK: {session_file.name} (finished={finished}, cancelled={cancelled})")
                
        except Exception as e:
            print(f"❌ Erreur traitement {session_file.name}: {e}")
    
    print(f"\n✅ Nettoyage terminé: {cleaned_count} sessions supprimées")

if __name__ == "__main__":
    debug_double_sending()
    
    print(f"\n" + "=" * 50)
    user_input = input("Voulez-vous nettoyer les sessions non terminées ? (o/N): ")
    if user_input.lower() in ['o', 'oui', 'y', 'yes']:
        clean_old_sessions()
    else:
        print("Nettoyage ignoré")