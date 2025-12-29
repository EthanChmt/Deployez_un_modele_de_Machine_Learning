import joblib
import pandas as pd
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

model = None
load_error = None

# Données métiers
AVG_SALARY_BY_JOB = {
    'Assistant de Direction': 3239.97, 'Cadre Commercial': 6924.28, 'Consultant': 3237.17, 
    'Directeur Technique': 16033.55, 'Manager': 7528.76, 'Représentant Commercial': 2626.0, 
    'Ressources Humaines': 4235.75, 'Senior Manager': 17181.68, 'Tech Lead': 7295.14
}

# --- NOUVELLE METHODE DE CHARGEMENT (LIFESPAN) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, load_error
    print("🔄 Démarrage du cycle de vie (Lifespan)...")
    try:
        # On cherche le fichier au bon endroit
        if os.path.exists("app/mon_modele.joblib"):
            path = "app/mon_modele.joblib"
        elif os.path.exists("mon_modele.joblib"):
            path = "mon_modele.joblib"
        else:
            raise FileNotFoundError(f"Fichier introuvable. Dossier: {os.getcwd()}, LS: {os.listdir('.')}")

        model = joblib.load(path)
        print(f"✅ Modèle chargé avec succès depuis {path} !")
    except Exception as e:
        print(f"❌ Erreur critique au chargement : {e}")
        load_error = str(e)
        model = None
    
    yield  # L'application tourne ici
    
    print("🛑 Arrêt de l'application.")
    # On pourrait nettoyer la mémoire ici si besoin

# On injecte le lifespan dans l'app
app = FastAPI(title="Employee Attrition Prediction API", version="1.0.0", lifespan=lifespan)

# Modèle de données
class EmployeeInput(BaseModel):
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

def preprocess_input(data: dict) -> pd.DataFrame:
    df = pd.DataFrame([data])
    
    df['genre_M'] = (df['genre'] == 'M').astype(int)
    df['heure_supplementaires_Oui'] = (df['heure_supplementaires'] == 'Oui').astype(int)
    freq_map = {'Non-Travel': 0, 'Travel_Rarely': 1, 'Travel_Frequently': 2, 'Aucun': 0, 'Occasionnel': 1, 'Frequent': 2}
    df['frequence_deplacement'] = df['frequence_deplacement'].map(freq_map).fillna(1).astype(int)

    df['ratio_loyaute'] = df.apply(lambda x: x['annees_dans_l_entreprise'] / x['age'] if x['age'] > 0 else 0, axis=1)
    df['ratio_stagnation'] = df['annees_depuis_la_derniere_promotion'] / (df['annees_dans_l_entreprise'] + 1)
    mean_salary = AVG_SALARY_BY_JOB.get(data['poste'], 5000)
    df['ratio_salaire_comparatif'] = df['revenu_mensuel'] / mean_salary
    df['taux_volatilite'] = df['nombre_experiences_precedentes'] / (df['annee_experience_totale'] + 1)
    df['delta_evaluation'] = df['note_evaluation_actuelle'] - df['note_evaluation_precedente']
    df['frustration_trajet'] = df['distance_domicile_travail'] / (df['satisfaction_employee_equilibre_pro_perso'] + 1)

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

    # One-hot encoding manuel
    if f"statut_marital_{data['statut_marital']}" in expected_columns:
        final_df[f"statut_marital_{data['statut_marital']}"] = 1
    if f"departement_{data['departement']}" in expected_columns:
        final_df[f"departement_{data['departement']}"] = 1
    if f"poste_{data['poste']}" in expected_columns:
        final_df[f"poste_{data['poste']}"] = 1
    if f"domaine_etude_{data['domaine_etude']}" in expected_columns:
        final_df[f"domaine_etude_{data['domaine_etude']}"] = 1

    return final_df

@app.get("/")
def health_check():
    return {"status": "online"}

@app.post("/predict")
def predict(input_data: EmployeeInput):
    if not model:
        # On inclut l'erreur dans la réponse pour comprendre pourquoi ça plante
        detail_msg = f"Modele non chargé. Cause: {load_error if load_error else 'Erreur inconnue (Lifespan non déclenché)'}"
        raise HTTPException(status_code=503, detail=detail_msg)
        
    try:
        features = preprocess_input(input_data.dict())
        prediction = model.predict(features)[0]
        return {"prediction": int(prediction)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))