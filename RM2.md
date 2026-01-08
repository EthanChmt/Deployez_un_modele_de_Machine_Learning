<a id="readme-top"></a>

<div align="center">
  <img src="https://media.licdn.com/dms/image/v2/C5612AQGbh-2GzkdqAQ/article-cover_image-shrink_600_2000/article-cover_image-shrink_600_2000/0/1590327785584?e=2147483647&v=beta&t=J_94telHC675IkwkENNV8mSvEwHtozclDrw2Lq2lIAI" alt="Logo" width="150" height="150">
  <h3 align="center">API de Prédiction d'Attrition</h3>

  <p align="center">
    Une API intelligente pour anticiper les départs des employés (Machine Learning) destinée à être lancée en local.
    <br />
    <br />
    <a href="http://127.0.0.1:8000/docs"><strong>Explorer la documentation API »</strong></a>
    <br />
    <br />
    &middot;
    <a href="#contact">Contact</a>
  </p>
</div>

<details>
  <summary>Table des Matières</summary>
  <ol>
    <li>
      <a href="#a-propos">À propos du projet</a>
      <ul>
        <li><a href="#technologies">Technologies</a></li>
      </ul>
    </li>
    <li><a href="#fonctionnalites">Fonctionnalités</a></li>
    <li><a href="#architecture-technique">Architecture Technique</a></li>
    <li>
      <a href="#demarrage">Démarrage Rapide</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#configuration">Configuration</a></li>
        <li><a href="#lancement">Lancement</a></li>
      </ul>
    </li>
    <li><a href="#docker">Utilisation via Docker</a></li>
    <li><a href="#tests">Tests</a></li>
    <li><a href="#documentation-api">Documentation API</a></li>
    <li><a href="#auteurs">Auteurs</a></li>
  </ol>
</details>

## <a id="a-propos"></a>🚀 À propos du projet

Ce projet est une solution complète de **Machine Learning Operations (MLOps)**. 
Il permet aux responsables RH d'uploader les données d'un employé et d'obtenir instantanément :
1. Une prédiction binaire (Va-t-il démissionner ?).
2. Un score de probabilité (ex: "Risque de départ à 85%").

L'objectif est de fournir un outil d'aide à la décision fiable, auditable et facile à déployer.

<p align="right">(<a href="#readme-top">retour en haut</a>)</p>

### <a id="technologies"></a>🛠️ Technologies utilisées

Voici la stack technique du projet :

* ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
* ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
* ![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
* ![Scikit-Learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
* ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
* ![PostgreSQL](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

<p align="right">(<a href="#readme-top">retour en haut</a>)</p>


# 📋 Fonctionnalités

- **Prédiction en temps réel** : classification binaire (*Reste / Part*) avec score de probabilité  
- **Audit logging** : enregistrement des prédictions et des métadonnées en base de données PostgreSQL  
- **Documentation interactive** : Swagger UI intégré et généré automatiquement  
- **Conteneurisation** : support Docker pour un déploiement proche de la production  

---

## 🛠️ Architecture Technique

- **Langage** : Python 3.10+  
- **Framework Web** : FastAPI  
- **Moteur ML** : Scikit-learn, Joblib, Pandas  
- **Base de données** : PostgreSQL (ORM via SQLAlchemy)  
- **Tests** : Pytest  

---

## 🚀 Installation et Démarrage Local

### Prérequis

- Python 3.10 ou supérieur  
- Git  
- PostgreSQL (local ou distant)  

---

### Installation

    git clone https://github.com/votre-username/Deployez_un_modele_de_Machine_Learning.git
    cd Deployez_un_modele_de_Machine_Learning

    python -m venv venv

    # Windows
    .\venv\Scripts\activate

    # Linux / MacOS
    source venv/bin/activate

    pip install -r requirements.txt

---

### Configuration

Créer un fichier `.env` à la racine du projet :

    DB_PASSWORD=votre_mot_de_passe
    # DB_HOST=localhost
    # DB_USER=postgres
    # DB_NAME=attrition_db
    # DB_PORT=5432

---

### Lancement

    uvicorn app.main:app --reload

API disponible sur :  
http://127.0.0.1:8000

---

## 🐳 Utilisation via Docker

    docker build -t attrition-api .
    docker run -p 8000:8000 --env-file .env attrition-api

---

## ✅ Tests

    pytest

---

## 📖 Documentation API

- Swagger UI : http://127.0.0.1:8000/docs

---

## 👤 Auteurs

Github : **EthanChmt**  
Contact mail : **ethan.chaumeret@gmail.com**  
Projet réalisé dans le cadre de la formation : **OpenClassrooms**.
