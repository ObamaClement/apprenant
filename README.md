 # Module apprenant STI (Backend FastAPI)
 
 Backend FastAPI pour un **module apprenant** (Learner Model) dans un Système Tuteur Intelligent.
 
 Le projet stocke et met à jour plusieurs dimensions de l’apprenant :
 
 - **Connaissances (modèle cognitif)** : overlay model + **BKT (Bayesian Knowledge Tracing)**
 - **Performance**
 - **Affectif**
 - **Comportement**
 - **Historique d’apprentissage** (source d’observations)
 
 ---
 
 ## 1) Ce qui est implémenté (état actuel)
 
 ### 1.1 Modèle de domaine (Concepts)
 
 Le domaine est représenté par des **concepts pédagogiques** (table `concepts`).
 
 Chaque concept embarque des **paramètres BKT** (configurables) :
 
 - `p_init` : probabilité initiale de maîtrise (P(K0))
 - `p_transit` : probabilité d’apprentissage entre deux opportunités (P(T))
 - `p_guess` : probabilité de réussite sans maîtrise (P(G), “deviner”)
 - `p_slip` : probabilité d’échec malgré la maîtrise (P(S), “étourderie”)
 
 ### 1.2 Modèle de connaissances (overlay + BKT)
 
 La connaissance de l’apprenant est représentée par un **overlay model** :
 
 - table `learner_knowledge`
 - clé logique `(learner_id, concept_id)`
 - valeur `mastery_level` qui correspond à **P(Know)**
 
 Mise à jour :
 
 - via la fonction `update_mastery()` (BKT standard : Bayes + transition)
 - en utilisant les paramètres portés par le concept
 - observation `correct` provenant de :
   - `LearningHistory.success` quand disponible
   - sinon conversion `score -> correct` via un seuil (configurable)
 
 Références (équations BKT) :
 
 - Corbett & Anderson (1995) (PDF) : http://act-r.psy.cmu.edu/wordpress/wp-content/uploads/2012/12/893CorbettAnderson1995.pdf
 - Van De Sande (PDF) : https://files.eric.ed.gov/fulltext/EJ1115329.pdf
 
 ### 1.3 Historique d’apprentissage
 
 Le modèle `LearningHistory` (table `learning_histories`) stocke les observations d’apprentissage :
 
 - type d’activité (`activity_type`)
 - référence d’activité (`activity_ref`)
 - réussite (`success`) et score (`score`)
 - temps passé (`time_spent`)
 - timestamp (`created_at`)
 
 Cet historique sert notamment à :
 
 - rejouer une séquence d’observations pour reconstruire `mastery_level` (BKT)
 - produire des résumés/statistiques
 
 ### 1.4 Moteur d’adaptation (orchestration)
 
 Le moteur d’adaptation orchestre plusieurs sous-modèles après une performance :
 
 - enregistrement d’une performance
 - mise à jour du modèle de connaissances (BKT)
 - mise à jour affectif/comportemental
 - génération de recommandations
 
 ---
 
 ## 2) Démarrage rapide
 
 ### 2.1 Variables d’environnement
 
 Créer/adapter `.env` à la racine (exemple) :
 
 ```env
 DATABASE_URL=postgresql://utilisateur_elsa:elsaelsa@localhost:5432/bdapprenant
 DEBUG=True
 SECRET_KEY=change-me
 ```
 
 ### 2.2 Lancer l’API
 
 ```bash
 source venv/bin/activate
 uvicorn app.main:app --reload
 ```
 
 Swagger : http://127.0.0.1:8000/docs
 
 ---
 
 ## 3) Architecture : comment les fichiers communiquent entre eux
 
 Flux global :
 
 1. **Route FastAPI** (`app/api/*`) reçoit une requête
 2. La route récupère une session DB via `Depends(get_db)`
 3. La route appelle un **service** (`app/services/*`) ou exécute une logique légère
 4. Les services lisent/écrivent des **modèles SQLAlchemy** (`app/models/*`)
 5. SQLAlchemy persiste dans PostgreSQL via `engine` (`app/core/database.py`)
 
 Dépendances techniques clés :
 
 - **Config** : `app/core/config.py` (lit `.env`)
 - **DB** : `app/core/database.py` (engine, SessionLocal, Base)
 - **Injection DB** : `app/core/deps.py` (`get_db()`)
 - **Entrée API** : `app/main.py`
 
 ---
 
 ## 4) Description des dossiers/fichiers (contenu + rôle)
 
 ### 4.1 `app/main.py`
 
 - Point d’entrée FastAPI.
 - Monte les routeurs (`app.include_router(...)`).
 - Crée les tables via `Base.metadata.create_all(bind=engine)`.
 
 **Important** : `create_all()` ne fait pas de migration sur une table existante. Pour des changements de schéma (ex: ajout des colonnes BKT dans `concepts`), il faut une migration (Alembic ou `ALTER TABLE`).
 
 ### 4.2 `app/core/config.py`
 
 - `Settings` (Pydantic Settings) : `DATABASE_URL`, `DEBUG`, etc.
 - Charge `.env` via `env_file = ".env"`.
 
 ### 4.3 `app/core/database.py`
 
 - Crée `engine = create_engine(settings.DATABASE_URL)`.
 - Configure `SessionLocal`.
 - Expose `Base = declarative_base()`.
 
 ### 4.4 Modèles SQLAlchemy (`app/models/`)
 
 - `concept.py`
   - Table `concepts` (domaine/compétences).
   - Contient maintenant les paramètres BKT : `p_init`, `p_transit`, `p_guess`, `p_slip`.
 
 - `learner.py`
   - Table `learners`.
   - Relations :
     - `learning_histories` → `LearningHistory`
     - `knowledge` → `LearnerKnowledge`
 
 - `learner_knowledge.py`
   - Table `learner_knowledge`.
   - Représente l’overlay : `(learner_id, concept_id) -> mastery_level`.
   - `mastery_level` = **P(Know)** (BKT).
 
 - `learning_history.py`
   - Table `learning_histories`.
   - Champs importants pour BKT :
     - `success` (bool) : observation binaire si disponible
     - `score` (0..100) : peut être converti en correct/incorrect via un seuil
     - `created_at` : pour rejouer les observations dans l’ordre chronologique
 
 - `learner_performance.py`, `learner_affective.py`, `learner_behavior.py`, `learner_cognitive.py`
   - Tables des autres sous-modèles utilisés par le moteur d’adaptation.
 
 ### 4.5 Schémas Pydantic (`app/schemas/`)
 
 - `concept.py`
   - Expose `p_init`, `p_transit`, `p_guess`, `p_slip` avec validation (bornes `[0,1]`).
 
 - `learner_knowledge.py`
   - Schémas d’entrée/sortie pour l’overlay (learner_id, concept_id, mastery_level).
 
 ### 4.6 Services (`app/services/`)
 
 #### 4.6.1 `knowledge_update_service.py` (BKT)
 
 Fonctions principales :
 
 - `_clamp01(value)` : borne une probabilité dans `[0,1]`.
 - `score_to_correct(score, threshold)` : convertit un score en observation binaire.
 - `bkt_update(p_mastery, correct, p_transit, p_guess, p_slip)` :
   - Étape Bayes : calcule `P(L|Correct)` ou `P(L|Incorrect)`.
   - Étape transition : `P(L_next) = P(L|obs) + (1 - P(L|obs)) * p_transit`.
 - `update_mastery(...)` : wrapper appelé par les autres modules.
 - `get_mastery_label(mastery_level)` : label (Non maîtrisé, Partiellement, etc.).
 
 #### 4.6.2 `knowledge_inference_service.py`
 
 - `infer_knowledge_from_activity(db, learner_id, concept_id, score)`
   - Charge le `Concept` pour récupérer les paramètres BKT.
   - Crée/charge `LearnerKnowledge`.
   - Met à jour `mastery_level` via BKT.
 
 - `infer_knowledge_from_history(db, learner_id, concept_id)`
   - Recharge les `LearningHistory`.
   - Rejoue les observations dans l’ordre chronologique (BKT) pour reconstruire `mastery_level`.
 
 - `get_learner_knowledge_summary(db, learner_id)`
   - Statistiques globales sur les concepts d’un apprenant.
 
 #### 4.6.3 `adaptation_engine.py`
 
 - `process_new_performance(...)` : orchestrateur.
   - Enregistre une performance.
   - Met à jour le modèle cognitif (BKT).
   - Met à jour l’affectif / comportement.
   - Retourne une recommandation.
 
 - `get_adaptation_summary(db, learner_id)` : résumé multi-modèles.
 
 Autres services :
 
 - `affective_service.py`
 - `behavior_service.py`
 - `performance_service.py`
 
 ### 4.7 API (routes) (`app/api/`)
 
 Les routeurs sont montés dans `app/main.py`.
 
 - `learners.py` : CRUD apprenants
 - `learning_history.py` : gestion historique
 - `concepts.py` : création/listing concepts (inclut les paramètres BKT)
 - `learner_knowledge.py` : endpoints overlay (lecture, mise à jour depuis activité, summary)
 - `adaptation.py` : orchestration “end-to-end” via le moteur d’adaptation
 - `learner_performance.py`, `learner_behavior.py`, `learner_cognitive.py`, `learner_affective.py`
 
 ---
 
 ## 5) Ce qui est déjà fait / ce qui reste à faire
 
 ### Déjà fait
 
 - Modèle cognitif centré sur `LearnerKnowledge` (overlay) opérationnel.
 - Architecture modulaire (API / services / modèles).
 - Modèle overlay opérationnel (table `learner_knowledge`).
 - Implémentation BKT (formules standard) + paramètres configurables par concept.
 - Démarrage uvicorn validé.
 
 ### Reste à faire pour un module apprenant “complet”
 
 1. **Migration DB**
    - Ajouter physiquement les colonnes BKT dans `concepts` (Alembic recommandé).
 
 2. **Contraintes d’intégrité**
    - Ajouter une contrainte d’unicité sur `learner_knowledge(learner_id, concept_id)` (éviter les doublons).
 
 3. **Rendre l’API `learner_knowledge` cohérente avec BKT**
    - Aujourd’hui `POST /learner-knowledge/` permet d’écrire `mastery_level` directement.
    - À décider :
      - soit on l’interdit (lecture seule + update via activité),
      - soit on garde mais en le réservant à l’initialisation/admin.
 
 4. **Lien activité → concept**
    - Actuellement `infer_knowledge_from_history` filtre avec `activity_ref.like("%{concept_id}%")`.
    - À améliorer : stocker explicitement `concept_id` dans `LearningHistory`.
 
 5. **Calibration des paramètres BKT**
    - Les valeurs par défaut sont des initialisations raisonnables, mais pas “universelles”.
    - Ajouter un processus d’estimation (EM / grid search) ou définir une stratégie par type d’activité.
 
 6. **Tests & qualité**
    - Tests unitaires : BKT update, endpoints principaux.
    - Jeux de données de démonstration.
 
