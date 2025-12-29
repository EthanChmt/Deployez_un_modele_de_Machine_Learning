from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Vérifie que l'API est en ligne"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "online"}

def test_predict_valid():
    """Vérifie qu'une prédiction fonctionne"""
    payload = {
        "id_employee": 1, "age": 35, "revenu_mensuel": 5000, "nombre_experiences_precedentes": 2,
        "annee_experience_totale": 10, "annees_dans_le_poste_actuel": 3,
        "satisfaction_employee_environnement": 3, "note_evaluation_precedente": 3,
        "satisfaction_employee_nature_travail": 3, "satisfaction_employee_equipe": 3,
        "satisfaction_employee_equilibre_pro_perso": 3, "note_evaluation_actuelle": 3,
        "augmentation_salaire_pourcentage": 15, "nombre_participation_pee": 0,
        "nb_formations_suivies": 2, "niveau_education": 3, "annes_sous_responsable_actuel": 2,
        "annees_dans_l_entreprise": 5, "annees_depuis_la_derniere_promotion": 1,
        "distance_domicile_travail": 10, "genre": "M", "statut_marital": "Marié(e)",
        "departement": "Consulting", "poste": "Manager", "heure_supplementaires": "Non",
        "domaine_etude": "Marketing", "frequence_deplacement": "Occasionnel"
    }
    
    response = client.post("/predict", json=payload)
    

    assert response.status_code == 200, f"ÉCHEC API: {response.text}"