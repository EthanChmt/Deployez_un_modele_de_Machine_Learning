import pytest
from fastapi.testclient import TestClient
from app.main import app, preprocess_input

# ==========================================
# JEU DE DONNÉES DE RÉFÉRENCE (FIXTURE)
# ==========================================
# Dictionnaire représentant un employé complet et valide
# Utilisé pour garantir la cohérence des tests unitaires et fonctionnels
VALID_EMPLOYEE_PAYLOAD = {
    "id_employee": 1,
    "age": 35,
    "revenu_mensuel": 5000,
    "nombre_experiences_precedentes": 2,
    "annee_experience_totale": 10,
    "annees_dans_le_poste_actuel": 3,
    "satisfaction_employee_environnement": 3,
    "note_evaluation_precedente": 3,
    "satisfaction_employee_nature_travail": 3,
    "satisfaction_employee_equipe": 3,
    "satisfaction_employee_equilibre_pro_perso": 3,
    "note_evaluation_actuelle": 3,
    "augmentation_salaire_pourcentage": 15,
    "nombre_participation_pee": 0,
    "nb_formations_suivies": 2,
    "niveau_education": 3,
    "annes_sous_responsable_actuel": 2,
    "annees_dans_l_entreprise": 5,
    "annees_depuis_la_derniere_promotion": 1,
    "distance_domicile_travail": 10,
    "genre": "M",
    "statut_marital": "Marié(e)",
    "departement": "Consulting",
    "poste": "Manager",
    "heure_supplementaires": "Non",
    "domaine_etude": "Marketing",
    "frequence_deplacement": "Occasionnel"
}

# ==========================================
# 1. TESTS UNITAIRES (LOGIQUE MÉTIER)
# ==========================================

def test_preprocess_input_logic():
    """
    Test unitaire de la fonction 'preprocess_input'.
    Vérifie l'exactitude du Feature Engineering (calcul des ratios)
    et de l'encodage (One-Hot) sans interaction avec l'API.
    """
    # Exécution de la transformation
    df = preprocess_input(VALID_EMPLOYEE_PAYLOAD)
    
    # Validation de la présence des colonnes générées
    assert "ratio_loyaute" in df.columns, "La colonne 'ratio_loyaute' doit être générée."
    assert "genre_M" in df.columns, "L'encodage One-Hot pour le genre doit générer 'genre_M'."
    
    # Validation arithmétique (Ratio Loyauté = Années Entreprise / Age)
    # 5 / 35 ≈ 0.1428. Utilisation de approx pour gérer la virgule flottante.
    expected_ratio = 5 / 35
    assert df.iloc[0]["ratio_loyaute"] == pytest.approx(expected_ratio, 0.01)
    
    # Validation de l'encodage binaire
    assert df.iloc[0]["genre_M"] == 1

# ==========================================
# 2. TESTS FONCTIONNELS (ENDPOINTS API)
# ==========================================

def test_health_check():
    """
    Test fonctionnel du endpoint racine '/'.
    Vérifie la disponibilité du service.
    """
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"status": "online", "service": "Attrition Prediction API"}

def test_predict_endpoint_success():
    """
    Test fonctionnel du endpoint '/predict' (Cas nominal).
    Vérifie que l'API accepte une payload valide et retourne une prédiction complète
    (classe + probabilité).
    """
    with TestClient(app) as client:
        response = client.post("/predict", json=VALID_EMPLOYEE_PAYLOAD)
        
        # Vérification du code statut HTTP
        assert response.status_code == 200
        
        # Vérification de la structure de la réponse
        json_response = response.json()
        
        # Validation du champ 'prediction'
        assert "prediction" in json_response
        assert json_response["prediction"] in [0, 1]
        
        # Validation du champ 'probability' (Nouveau critère)
        assert "probability" in json_response
        probability = json_response["probability"]
        assert isinstance(probability, (float, int)), "La probabilité doit être un nombre."
        assert 0 <= probability <= 100, "La probabilité doit être comprise entre 0 et 100%."

def test_predict_endpoint_validation_error():
    """
    Test fonctionnel du endpoint '/predict' (Gestion d'erreur).
    Vérifie que l'API rejette une requête incomplète (Validation Pydantic).
    """
    # Création d'une payload invalide (suppression d'un champ obligatoire)
    invalid_payload = VALID_EMPLOYEE_PAYLOAD.copy()
    del invalid_payload["age"]
    
    with TestClient(app) as client:
        response = client.post("/predict", json=invalid_payload)
        
        # Le code 422 Unprocessable Entity est attendu pour une erreur de validation
        assert response.status_code == 422