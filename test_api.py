import requests

# Les données à envoyer (Celles qui posent problème)
data = {
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

try:
    response = requests.post("http://127.0.0.1:8000/predict", json=data)
    print(f"Statut Code: {response.status_code}")
    print("Réponse du serveur :")
    print(response.json())
except Exception as e:
    print(f"Erreur de connexion : {e}")
    