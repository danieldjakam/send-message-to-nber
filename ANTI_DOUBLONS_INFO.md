# 🚫 Système Anti-Doublons

## 📋 Fonctionnalités

Le système anti-doublons évite automatiquement de renvoyer le **même message** au **même numéro de téléphone**.

### ✅ Ce qui est détecté comme doublon :
- **Même numéro** + **Même message texte**
- **Même numéro** + **Même message** + **Même image**
- Les numéros sont normalisés (seuls les chiffres comptent)

### 📊 Suivi automatique :
- ✅ **Enregistrement** : Chaque envoi réussi est sauvegardé
- 🔄 **Vérification** : Avant chaque envoi, vérification des doublons
- 📝 **Statistiques** : Nombre de contacts et messages envoyés
- 💾 **Persistance** : Les données survivent aux redémarrages

## 🎯 Utilisation

### 1. Envoi automatique
- Le système filtre automatiquement les doublons
- Affiche le nombre de doublons ignorés
- Continue avec les nouveaux numéros uniquement

### 2. Gestion manuelle
- **Bouton "📝 Historique"** dans l'interface
- **Voir les statistiques** : Nombre de contacts et messages
- **Exporter la liste** : Sauvegarde JSON des numéros contactés
- **Effacer l'historique** : Reset complet (avec confirmation)

## 📁 Stockage des données

```
~/.insam_message/
└── sent_numbers.json    # Historique des envois
```

### Structure du fichier JSON :
```json
{
  "sent_numbers": {
    "1234567890": {
      "message_hashes": ["abc123", "def456"],
      "last_sent": "2025-08-07T16:30:00",
      "total_sent": 2
    }
  },
  "last_updated": "2025-08-07T16:30:00"
}
```

## 🔄 Cas d'usage

### ✅ Scénarios où les messages SONT envoyés :
1. **Nouveau numéro** jamais contacté
2. **Même numéro** avec un **message différent**
3. **Même numéro** avec une **image différente**
4. Après avoir **effacé l'historique**

### 🚫 Scénarios où les messages ne sont PAS envoyés :
1. **Même numéro** + **Même message** déjà envoyé
2. **Même numéro** + **Même image** + **Même texte**

## ⚙️ Configuration

### Messages personnalisés avec données Excel :
- Le hash inclut le **message final** avec les données
- Chaque ligne Excel génère un message unique
- Permet d'envoyer à la même personne si les données changent

### Gestion des images :
- Les images sont identifiées par leur **taille de fichier**
- Remplacer une image par une autre = nouveau message possible

## 🛠️ Maintenance

### Export des données :
```json
{
  "exported_on": "2025-08-07T16:30:00",
  "total_numbers": 150,
  "total_messages": 230,
  "numbers": [
    {
      "phone": "1234567890",
      "total_sent": 2,
      "last_sent": "2025-08-07T16:30:00",
      "messages_count": 2
    }
  ]
}
```

### Reset de l'historique :
- ⚠️ **Action irréversible**
- Confirmation obligatoire
- Permet de renvoyer aux mêmes numéros

## 💡 Conseils

1. **Avant un envoi massif** : Vérifiez les statistiques
2. **Tests multiples** : Utilisez différents messages de test
3. **Backup régulier** : Exportez périodiquement la liste
4. **Messages évolutifs** : Variez le contenu pour éviter la répétition