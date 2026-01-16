# Utilise une image Python légère
FROM python:3.11-slim

# Définit le dossier de travail dans le conteneur
WORKDIR /code

# Copie le fichier des dépendances
COPY ./requirements.txt /code/requirements.txt

# Installe les dépendances
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copie le contenu du dossier app
COPY ./app /code/app

# Commande pour lancer l'API sur le port 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]