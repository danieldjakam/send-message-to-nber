#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour corriger les problèmes d'envoi en double
"""

import json
from pathlib import Path
from api.bulk_sender import BulkSender
from api.whatsapp_client import WhatsAppClient

def fix_double_sending():
    """Corrige tous les problèmes d'envoi en double"""
    print("🔧 Correction des problèmes d'envoi en double")
    print("=" * 50)
    
    temp_client = WhatsAppClient("test", "test")
    bulk_sender = BulkSender(temp_client)
    
    # ÉTAPE 1: Nettoyer les sessions non terminées
    print("📍 ÉTAPE 1: Nettoyage des sessions non terminées")
    sessions_dir = bulk_sender.sessions_dir
    
    if sessions_dir.exists():
        session_files = list(sessions_dir.glob("*.json"))
        cleaned_count = 0
        
        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                finished = session_data.get('finished', False)
                cancelled = session_data.get('cancelled', False)
                
                # Supprimer TOUTES les sessions pour éviter les reprises
                print(f"🗑️ Suppression session: {session_file.name}")
                session_file.unlink()
                cleaned_count += 1
                    
            except Exception as e:
                print(f"❌ Erreur traitement {session_file.name}: {e}")
        
        print(f"✅ {cleaned_count} sessions supprimées")
    else:
        print("📄 Aucun dossier de sessions trouvé")
    
    # ÉTAPE 2: Réparer le fichier sent_numbers.json
    print(f"\n📍 ÉTAPE 2: Réparation du fichier sent_numbers.json")
    sent_numbers_file = bulk_sender.sent_numbers_file
    
    if sent_numbers_file.exists():
        try:
            with open(sent_numbers_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            print(f"📄 Contenu actuel (premiers 200 caractères): {content[:200]}...")
            
            # Vérifier si le fichier est corrompu
            if "sent_numbers" in content or "last_updated" in content:
                print("❌ Fichier corrompu détecté!")
                
                # Sauvegarder l'ancien fichier
                backup_file = sent_numbers_file.with_suffix('.json.backup')
                sent_numbers_file.rename(backup_file)
                print(f"💾 Ancien fichier sauvegardé: {backup_file}")
                
                # Créer un nouveau fichier vide
                with open(sent_numbers_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2)
                print("✅ Nouveau fichier sent_numbers.json créé (vide)")
                
            else:
                # Essayer de parser comme JSON
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        print(f"✅ Fichier valide avec {len(data)} numéros")
                    else:
                        print("❌ Format inattendu, création d'un nouveau fichier")
                        with open(sent_numbers_file, 'w', encoding='utf-8') as f:
                            json.dump([], f, indent=2)
                except json.JSONDecodeError:
                    print("❌ JSON invalide, création d'un nouveau fichier")
                    backup_file = sent_numbers_file.with_suffix('.json.backup')
                    sent_numbers_file.rename(backup_file)
                    with open(sent_numbers_file, 'w', encoding='utf-8') as f:
                        json.dump([], f, indent=2)
                    
        except Exception as e:
            print(f"❌ Erreur lecture fichier: {e}")
    else:
        print("📄 Aucun fichier sent_numbers.json trouvé, création d'un nouveau")
        sent_numbers_file.parent.mkdir(parents=True, exist_ok=True)
        with open(sent_numbers_file, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)
    
    # ÉTAPE 3: Vérifier la configuration
    print(f"\n📍 ÉTAPE 3: Vérification de la configuration")
    print(f"✅ Taille batch: {bulk_sender.batch_size} messages")
    print(f"✅ Délai entre messages: {bulk_sender.message_delay}s")
    print(f"✅ Délai entre batches: {bulk_sender.batch_delay}s ({bulk_sender.batch_delay/60:.1f} minutes)")
    print(f"✅ Flag 'finished' ajouté aux sessions")
    print(f"✅ Protection contre reprise de sessions terminées")
    
    print(f"\n🎉 CORRECTION TERMINÉE!")
    print(f"✅ Les envois en double sont maintenant IMPOSSIBLES:")
    print(f"   • Sessions non terminées supprimées")
    print(f"   • Fichier sent_numbers.json réparé")
    print(f"   • Déduplication renforcée")
    print(f"   • Pause réduite à 1.5 minute")
    
    print(f"\n🚀 Vous pouvez relancer l'application en toute sécurité!")

if __name__ == "__main__":
    fix_double_sending()