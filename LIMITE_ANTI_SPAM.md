# 🚨 Système de Protection Anti-Spam

## 🎯 Objectif

Protéger votre compte WhatsApp contre les blocages en limitant automatiquement le nombre de messages envoyés par session.

## 📊 Limites Appliquées

### 🔴 Limite Stricte
- **Maximum : 2500 messages par session**
- Limite appliquée automatiquement
- Protection contre les blocages WhatsApp

### ⚠️ Avertissements
- **1000+ messages** : Avertissement de gros volume
- **2500+ messages** : Limite stricte avec options

## 🛡️ Protections Automatiques

### 1. Vérification avant envoi
- Comptage automatique des messages à envoyer
- Affichage d'alertes pour les gros volumes
- Demande de confirmation utilisateur

### 2. Troncature de sécurité
- Si > 2500 messages → Limitation aux 2500 premiers
- Messages excédentaires ignorés
- Notification claire à l'utilisateur

### 3. Options intelligentes
- **Option 1** : Envoi partiel (2500 premiers messages)
- **Option 2** : Division en sessions multiples

## 🔄 Gestion des Gros Volumes

### Pour envoyer plus de 2500 messages :

1. **Première session**
   - Lance l'envoi → Envoie les 2500 premiers
   - Messages marqués comme envoyés dans l'historique

2. **Sessions suivantes**
   - Relance l'application et l'envoi
   - Le système anti-doublons ignore les déjà envoyés
   - Envoie les 2500 suivants, etc.

3. **Exemple pour 7500 messages**
   - Session 1 : Messages 1-2500 ✅
   - Session 2 : Messages 2501-5000 ✅
   - Session 3 : Messages 5001-7500 ✅

## 📋 Messages d'Interface

### 🚨 Limite Anti-Spam Dépassée
```
⚠️ ATTENTION - LIMITE ANTI-SPAM

Vous tentez d'envoyer 5000 messages
Limite de sécurité: 2500 messages par session

Options disponibles:

🔸 OPTION 1 - Envoi partiel (Recommandé)
   Envoyer seulement les premiers 2500 messages

🔸 OPTION 2 - Division en sessions
   Diviser en 2 sessions de 2500 max
   (Nécessite plusieurs lancements)

Choisir Option 1 (Oui) ou Option 2 (Non) ?
```

### 📊 Gros Volume Détecté (1000-2499)
```
📊 GROS VOLUME DÉTECTÉ

Vous allez envoyer 1500 messages

Recommandations:
• L'envoi peut prendre du temps
• Surveillez les logs pour les erreurs
• Évitez de fermer l'application

Continuer avec cet envoi ?
```

## 🔧 Configuration Technique

### Dans `api/bulk_sender.py` :
```python
# Limite anti-spam
self.MAX_MESSAGES_PER_SESSION = 2500
```

### Vérifications appliquées :
1. **Filtrage doublons** → Données filtrées
2. **Vérification limite** → Si > 2500 → Troncature
3. **Confirmation utilisateur** → Dialogue d'options
4. **Envoi sécurisé** → Maximum 2500 messages

## 🎯 Avantages

### ✅ Protection du compte
- Évite les blocages WhatsApp Business
- Respecte les limites de l'API
- Prévient les suspensions de compte

### ✅ Expérience utilisateur
- Alertes claires et informatives
- Options flexibles selon le besoin
- Guidance pour les gros volumes

### ✅ Compatibilité avec anti-doublons
- Fonctionne parfaitement avec le système de doublons
- Permet les envois en plusieurs sessions
- Historique persistant entre les sessions

## 📈 Recommandations d'Utilisation

### 🟢 Envois Optimaux (0-1000 messages)
- Aucune restriction
- Envoi direct possible
- Performance optimale

### 🟡 Gros Volumes (1000-2500 messages)
- Avertissement affiché
- Envoi possible en une session
- Surveillance recommandée

### 🔴 Très Gros Volumes (2500+ messages)
- **Recommandé** : Envoi partiel (premiers 2500)
- **Alternatif** : Division en sessions multiples
- Utilisation du système anti-doublons

## 🚀 Conseils Pratiques

1. **Planifiez vos envois** : Divisez les gros fichiers Excel
2. **Testez d'abord** : Commencez par de petits volumes
3. **Surveillez l'API** : Vérifiez les limites de votre compte UltraMsg
4. **Patience** : Les gros volumes prennent du temps
5. **Sauvegardez** : Exportez régulièrement l'historique des envois