import joblib
import pandas as pd
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

# Imports pour la persistance des données (SQLAlchemy)
from sqlalchemy import create_engine, Column, Integer, JSON, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

# ==========================================
# CONFIGURATION DE LA BASE DE DONNÉES
# ==========================================
# Paramètres de connexion PostgreSQL
DB_USER = "postgres"
DB_PASSWORD = "301002"  # Configuration locale
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "attrition_db"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Initialisation du moteur SQLAlchemy et de la session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# MODÈLES DE DONNÉES (ORM & SCHÉMAS)
# ==========================================

class PredictionLog(Base):
    """
    Modèle SQLAlchemy représentant la table d'historique des prédictions.
    Stocke les données d'entrée brutes (JSON) et le résultat de l'inférence.
    """
    __tablename__ = "prediction_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    input_data = Column(JSON)  # Stockage flexible des inputs
    prediction = Column(Integer)

class EmployeeInput(BaseModel):
    """
    Schéma Pydantic pour la validation stricte des données entrantes.
    Définit le contrat d'interface pour l'API.
    """
    id_employee: int
    age: int
    revenu_mensuel: int
    nombre_experiences_precedentes: int
    annee_experience_totale: int
    annees_dans_le_poste_actuel: int
    satisfaction_employee_environnement: int
    note_evaluation_precedente: int
    satisfaction_employee_nature_travail: int
    satisfaction_employee_equipe: int
    satisfaction_employee_equilibre_pro_perso: int
    note_evaluation_actuelle: int
    augmentation_salaire_pourcentage: int
    nombre_participation_pee: int
    nb_formations_suivies: int
    niveau_education: int
    annes_sous_responsable_actuel: int
    annees_dans_l_entreprise: int
    annees_depuis_la_derniere_promotion: int
    distance_domicile_travail: int
    genre: str
    statut_marital: str
    departement: str
    poste: str
    heure_supplementaires: str
    domaine_etude: str
    frequence_deplacement: str

# ==========================================
# LOGIQUE MÉTIER & CHARGEMENT DU MODÈLE
# ==========================================

# Variables globales pour l'état du modèle
model = None
load_error = None

# Données statistiques pour l'ingénierie des fonctionnalités
AVG_SALARY_BY_JOB = {
    'Assistant de Direction': 3239.97, 'Cadre Commercial': 6924.28, 'Consultant': 3237.17, 
    'Directeur Technique': 16033.55, 'Manager': 7528.76, 'Représentant Commercial': 2626.0, 
    'Ressources Humaines': 4235.75, 'Senior Manager': 17181.68, 'Tech Lead': 7295.14
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire de cycle de vie de l'application.
    Charge le modèle de Machine Learning en mémoire au démarrage du serveur.
    """
    global model, load_error
    print("INFO: Initialisation du cycle de vie de l'application...")
    try:
        # Recherche du fichier modèle (compatible structure locale et conteneurisée)
        if os.path.exists("app/mon_modele.joblib"):
            path = "app/mon_modele.joblib"
        elif os.path.exists("mon_modele.joblib"):
            path = "mon_modele.joblib"
        else:
            raise FileNotFoundError(f"Fichier modèle introuvable. Répertoire courant: {os.getcwd()}")

        model = joblib.load(path)
        print(f"SUCCESS: Modèle chargé depuis {path}")
    except Exception as e:
        print(f"CRITICAL: Échec du chargement du modèle : {e}")
        load_error = str(e)
        model = None
    
    yield
    print("INFO: Arrêt de l'application.")

app = FastAPI(title="Employee Attrition Prediction API", version="1.0.0", lifespan=lifespan)

def preprocess_input(data: dict) -> pd.DataFrame:
    """
    Transforme les données brutes (dictionnaire) en DataFrame prêt pour l'inférence.
    Applique les mêmes transformations (Feature Engineering) que lors de l'entraînement.
    """
    df = pd.DataFrame([data])
    
    # Encodage binaire
    df['genre_M'] = (df['genre'] == 'M').astype(int)
    df['heure_supplementaires_Oui'] = (df['heure_supplementaires'] == 'Oui').astype(int)
    
    # Mapping ordinal
    freq_map = {'Non-Travel': 0, 'Travel_Rarely': 1, 'Travel_Frequently': 2, 'Aucun': 0, 'Occasionnel': 1, 'Frequent': 2}
    df['frequence_deplacement'] = df['frequence_deplacement'].map(freq_map).fillna(1).astype(int)

    # Feature Engineering (Ratios et Deltas)
    df['ratio_loyaute'] = df.apply(lambda x: x['annees_dans_l_entreprise'] / x['age'] if x['age'] > 0 else 0, axis=1)
    df['ratio_stagnation'] = df['annees_depuis_la_derniere_promotion'] / (df['annees_dans_l_entreprise'] + 1)
    mean_salary = AVG_SALARY_BY_JOB.get(data['poste'], 5000)
    df['ratio_salaire_comparatif'] = df['revenu_mensuel'] / mean_salary
    df['taux_volatilite'] = df['nombre_experiences_precedentes'] / (df['annee_experience_totale'] + 1)
    df['delta_evaluation'] = df['note_evaluation_actuelle'] - df['note_evaluation_precedente']
    df['frustration_trajet'] = df['distance_domicile_travail'] / (df['satisfaction_employee_equilibre_pro_perso'] + 1)

    # Alignement des colonnes avec celles attendues par le modèle
    expected_columns = [
        'age', 'revenu_mensuel', 'nombre_experiences_precedentes', 
        'annee_experience_totale', 'annees_dans_le_poste_actuel', 
        'satisfaction_employee_environnement', 'note_evaluation_precedente', 
        'satisfaction_employee_nature_travail', 'satisfaction_employee_equipe', 
        'satisfaction_employee_equilibre_pro_perso', 'note_evaluation_actuelle', 
        'augmentation_salaire_pourcentage', 'nombre_participation_pee', 
        'nb_formations_suivies', 'niveau_education', 'frequence_deplacement', 
        'annes_sous_responsable_actuel', 'ratio_loyaute', 'ratio_stagnation', 
        'ratio_salaire_comparatif', 'taux_volatilite', 'delta_evaluation', 
        'frustration_trajet', 'genre_M', 
        'statut_marital_Divorcé(e)', 'statut_marital_Marié(e)', 
        'departement_Consulting', 
        'poste_Cadre Commercial', 'poste_Consultant', 'poste_Directeur Technique', 
        'poste_Manager', 'poste_Représentant Commercial', 'poste_Ressources Humaines', 
        'poste_Senior Manager', 'poste_Tech Lead', 
        'heure_supplementaires_Oui', 
        'domaine_etude_Entrepreunariat', 'domaine_etude_Infra & Cloud', 
        'domaine_etude_Marketing', 'domaine_etude_Ressources Humaines', 
        'domaine_etude_Transformation Digitale'
    ]
    
    final_df = pd.DataFrame(0, index=[0], columns=expected_columns)
    for col in expected_columns:
        if col in df.columns:
            final_df[col] = df[col]

    # One-Hot Encoding dynamique
    if f"statut_marital_{data['statut_marital']}" in expected_columns:
        final_df[f"statut_marital_{data['statut_marital']}"] = 1
    if f"departement_{data['departement']}" in expected_columns:
        final_df[f"departement_{data['departement']}"] = 1
    if f"poste_{data['poste']}" in expected_columns:
        final_df[f"poste_{data['poste']}"] = 1
    if f"domaine_etude_{data['domaine_etude']}" in expected_columns:
        final_df[f"domaine_etude_{data['domaine_etude']}"] = 1

    return final_df

# ==========================================
# ENDPOINTS API
# ==========================================

@app.get("/")
def health_check():
    """Vérification de l'état de l'API."""
    return {"status": "online", "service": "Attrition Prediction API"}

@app.post("/predict")
def predict(input_data: EmployeeInput):
    """
    Endpoint principal de prédiction.
    1. Prétraite les données reçues.
    2. Exécute le modèle ML.
    3. Enregistre la requête et le résultat en base de données (Audit Log).
    4. Retourne la prédiction.
    """
    if not model:
        detail_msg = f"Service indisponible : Modèle non chargé. Erreur : {load_error}"
        raise HTTPException(status_code=503, detail=detail_msg)
        
    try:
        # 1. Inférence
        features = preprocess_input(input_data.dict())
        prediction_val = int(model.predict(features)[0])
        
        # 2. Persistance des logs en base de données
        db = SessionLocal()
        try:
            log_entry = PredictionLog(
                input_data=input_data.dict(), # Sérialisation JSON des inputs
                prediction=prediction_val
            )
            db.add(log_entry)
            db.commit()
            # Note : En production, utiliser un logger standard (logging.info)
            print("INFO: Prédiction enregistrée en base de données.")
        except Exception as db_error:
            # La prédiction ne doit pas échouer si le logging échoue (Fail-safe)
            print(f"WARNING: Échec de l'écriture en base de données : {db_error}")
        finally:
            db.close()

        return {"prediction": prediction_val}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))