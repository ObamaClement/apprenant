
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Module apprenant STI"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://enspysti:i3BB41ShGAPKpeMo2LRhRAldyUfgSl87@dpg-d5512lggjchc7386uong-a.frankfurt-postgres.render.com/expert_db"
    
 
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignorer les variables supplémentaires du .env


settings = Settings()

"""
Configuration de l'application STI Learner

INSTRUCTIONS DE CONFIGURATION DE LA BASE DE DONNÉES
====================================================

1️⃣ CRÉER UN UTILISATEUR POSTGRESQL
-----------------------------------

Ouvrir un terminal et se connecter à PostgreSQL:
    sudo -u postgres psql

Créer un nouvel utilisateur:
    CREATE USER sti_user WITH PASSWORD 'password';
    CREATE USER apprenant_elsa WITH PASSWORD 'elsaelsa';

Donner les permissions:
    ALTER ROLE sti_user SET client_encoding TO 'utf8';
    ALTER ROLE sti_user SET default_transaction_isolation TO 'read committed';
    ALTER ROLE sti_user SET default_transaction_deferrable TO on;
    ALTER ROLE sti_user SET default_transaction_level TO 'read committed';

2️⃣ CRÉER LA BASE DE DONNÉES
----------------------------

Créer la base de données:
    CREATE DATABASE sti_db OWNER sti_user;
    CREATE DATABASE bdapprenant OWNER utilisateur_elsa;

Donner les permissions:
    GRANT ALL PRIVILEGES ON DATABASE sti_db TO sti_user;

3️⃣ VÉRIFIER LA CONNEXION
------------------------

Se connecter à la base de données:
    psql -U sti_user -d sti_db -h localhost

Si demandé, entrer le mot de passe: password

4️⃣ CONFIGURER LE FICHIER .env
------------------------------

Créer un fichier .env à la racine du projet:
    DATABASE_URL=postgresql://sti_user:password@localhost:5432/sti_db
    DEBUG=True
    APP_NAME=Module apprenant STI
    APP_VERSION=1.0.0

5️⃣ DÉMARRER L'APPLICATION
--------------------------

Installer les dépendances:
    pip install -r requirements.txt

Lancer l'application:
    python -m uvicorn app.main:app --reload

L'API sera disponible sur: http://127.0.0.1:8000
Documentation: http://127.0.0.1:8000/docs

6️⃣ RÉINITIALISER LA BASE DE DONNÉES
-----------------------------------

Si vous voulez recommencer à zéro:

    # Se connecter en tant que superuser
    sudo -u postgres psql
    
    # Supprimer la base de données
    DROP DATABASE IF EXISTS sti_db;
    
    # Supprimer l'utilisateur
    DROP USER IF EXISTS sti_user;
    
    # Puis refaire les étapes 1 et 2


"""
