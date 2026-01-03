import pandas as pd
from sqlalchemy import create_engine, Column, Integer, JSON, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func
import sys
import os

# --- Configuration ---
DB_USER = "postgres"
DB_PASSWORD = "301002"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "attrition_db"
CSV_FILE_PATH = "data/mon_dataset_final.csv"

# URL de connexion
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

Base = declarative_base()

# --- Modèles (Tables) ---
class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    features = Column(JSON)
    target = Column(Integer)

class PredictionLog(Base):
    __tablename__ = "prediction_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    input_data = Column(JSON)
    prediction = Column(Integer)

# --- Exécution ---
def init_database():
    # 1. Connexion et Création des tables
    print(f"Connexion a la base {DB_NAME}...")
    try:
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        print("Tables creees avec succes.")
    except Exception as e:
        print(f"Erreur de connexion : {e}")
        sys.exit(1)

    # 2. Lecture du CSV
    if not os.path.exists(CSV_FILE_PATH):
        print(f"Fichier CSV introuvable : {CSV_FILE_PATH}")
        sys.exit(1)

    print("Lecture et insertion des donnees...")
    df = pd.read_csv(CSV_FILE_PATH)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        # Vérification anti-doublon
        if session.query(Employee).count() > 0:
            print("La base contient deja des donnees. Insertion ignoree.")
            return

        # Transformation et insertion
        employees = []
        for _, row in df.iterrows():
            target = 1 if row['a_quitte_l_entreprise'] == 'Yes' else 0
            features = row.drop('a_quitte_l_entreprise').to_dict()
            employees.append(Employee(features=features, target=target))
        
        session.add_all(employees)
        session.commit()
        print(f"Succes : {len(employees)} employes ajoutes.")
        
    except Exception as e:
        session.rollback()
        print(f"Erreur d'insertion : {e}")
    finally:
        session.close()

if __name__ == "__main__":
    init_database()