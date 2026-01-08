# 📄 Fiche d'Identité du Modèle (Model Card)

## 🆔 Détails du Modèle
* **Nom** : Prédicteur départ collaborateur
* **Version** : 1.0
* **Date** : Janvier 2026
* **Type** : Classification Binaire Supervisée
* **Stratégie** : Optimisation par pondération des classes (Class Weight Tuning)

## 🎯 Objectif
Aider les RH à identifier les collaborateurs à risque de départ.
* **Input** : Données démographiques et professionnelles.
* **Output** : Prédiction binaire (0: Reste, 1: Part) + Probabilité.

## 📊 Performances
Le modèle a été optimisé pour maximiser le **Rappel (Recall)** afin de ne pas manquer les collaborateurs sur le départ, tout en maintenant une précision globale équilibrée.

| Métrique | Score | Interprétation |
| :--- | :--- | :--- |
| **Balanced Accuracy** | **0.737** | Précision moyenne pondérée (tient compte du déséquilibre des classes). |
| **Rappel (Recall)** | **0.77** | Le modèle détecte correctement **77%** des départs réels. |

> **Note technique** : Le déséquilibre des classes (peu de départs vs beaucoup de collaborateurs restant) a été géré via un système de "poids" (weights) et de multiplicateurs lors de l'entraînement, privilégiant la classe minoritaire.

## ⚙️ Traitement des Données (Feature Engineering)

### 1. Encodage Hybride
Nous avons utilisé une approche mixte pour conserver un maximum d'information :
* **Encodage Ordinal** : Appliqué aux variables ayant une hiérarchie (ex: *Niveau d'éducation*, *Fréquence de déplacement*).
* **One-Hot Encoding** : Appliqué aux variables nominales sans ordre (ex: *Département*, *Statut Marital*).

### 2. Gestion du déséquilibre
Plutôt que de générer de fausses données (SMOTE), nous avons opté pour une pénalisation algorithmique via un dictionnaire de poids (*class_weights*), forçant le modèle à prêter plus d'attention aux cas de démission.

## 💾 Données d'Entraînement
* **Source** : Jeu de données RH public (type IBM Analytics).
* **Volume** : ~1470 entrées.
* **Structure** : Données historiques anonymisées.

## 🔄 Protocole de Maintenance
Actuellement, le réentraînement n'est pas automatisé. Voici la procédure recommandée en cas de baisse de performance ou d'ajout de données :

1.  **Mise à jour des données** : Ajouter les nouveaux profils dans le dataset source (CSV).
2.  **Réentraînement** : Exécuter le Notebook d'entraînement initial.
3.  **Validation** : Vérifier que le *Balanced Accuracy* reste supérieur à 0.70.
4.  **Export** : Générer le nouveau fichier `.joblib`.
5.  **Déploiement** : Remplacer l'ancien fichier `.joblib` dans le dossier `/app` et redémarrer l'API.

## ⚠️ Limitations
* **Biais temporel** : Le modèle est basé sur des données historiques figées. Il ne prend pas en compte les changements récents de politique RH ou le contexte économique actuel.