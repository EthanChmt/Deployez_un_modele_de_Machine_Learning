import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Employee Attrition Prediction API", version="1.0.0")

model = None

# Les moyennes exactes pour le calcul du ratio salaire
AVG_SALARY_BY_JOB = {
    'Assistant de Direction': 3239.97, 
    'Cadre Commercial': 6924.28, 
    'Consultant': 3237.17, 
    'Directeur Technique': 16033.55, 
    'Manager': 7528.76, 
    'Représentant Commercial': 2626.0, 
    'Ressources Humaines': 4235.75, 
    'Senior Manager': 17181.68, 
    'Tech Lead': 7295.14
}

@app.on_event("startup")
def load_model():
    global model
    try:
        model = joblib.load("app/mon_modele.joblib")
    except Exception as e:
        print(f"Erreur chargement modèle: {e}")

# Le format des données que TU envoies (Texte et chiffres bruts)
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
    
    # 1. Encodage du texte en chiffres
    df['genre_M'] = (df['genre'] == 'M').astype(int)
    df['heure_supplementaires_Oui'] = (df['heure_supplementaires'] == 'Oui').astype(int)
    
    freq_map = {'Non-Travel': 0, 'Travel_Rarely': 1, 'Travel_Frequently': 2, 
                'Aucun': 0, 'Occasionnel': 1, 'Frequent': 2}
    # On force à 1 par défaut si inconnu pour éviter le crash
    df['frequence_deplacement'] = df['frequence_deplacement'].map(freq_map).fillna(1).astype(int)

    # 2. Calcul des Ratios (Feature Engineering)
    df['ratio_loyaute'] = df.apply(lambda x: x['annees_dans_l_entreprise'] / x['age'] if x['age'] > 0 else 0, axis=1)
    df['ratio_stagnation'] = df['annees_depuis_la_derniere_promotion'] / (df['annees_dans_l_entreprise'] + 1)
    
    mean_salary = AVG_SALARY_BY_JOB.get(data['poste'], 5000)
    df['ratio_salaire_comparatif'] = df['revenu_mensuel'] / mean_salary
    
    df['taux_volatilite'] = df['nombre_experiences_precedentes'] / (df['annee_experience_totale'] + 1)
    df['delta_evaluation'] = df['note_evaluation_actuelle'] - df['note_evaluation_precedente']
    df['frustration_trajet'] = df['distance_domicile_travail'] / (df['satisfaction_employee_equilibre_pro_perso'] + 1)

    # 3. Préparation des colonnes finales (Ordre strict)
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
            
    # Activation One-Hot
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
        raise HTTPException(status_code=503, detail="Model not loaded")
        
    try:
        features = preprocess_input(input_data.dict())
        prediction = model.predict(features)[0]
        return {"prediction": int(prediction)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))