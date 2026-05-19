# Squelette M0-B1 — Service de criticité maintenance prédictive

> Repo de départ à cloner pour le brief M0-B1 (FastIA — intégration d'un modèle
> scikit-learn pré-entraîné dans une API REST). **Doit tourner dès le clone.**

## 🎯 Objectif 

Fournir une prédiction de maintenance en fonction des caractéristiques d'une machine, d'après le model déjà entrainé, via l'endpoint /predict.


## 🎯 Architecture

```
squelette/
├── app/
│   ├── __init__.py
│   ├── main.py             ← FastAPI : /health 
│   └── schemas.py          ← Pydantic : MachineInput, PredictionResponse
├── data/
│   ├── generate_dataset.py ← script de régénération du dataset (déjà exécuté)
│   └── maintenance_data.csv ← dataset synthétique 6 500 lignes
├── model/
│   ├── train_baseline.py   ← script d'entraînement (déjà exécuté)
│   └── model.joblib        ← modèle pré-entraîné, ~6.6 Mo (à charger au démarrage)
├── tests/
│   ├── __init__.py
│   └── test_health.py      ← test pytest 
├── Dockerfile              ← squelette 
├── requirements.txt        ← dépendances figées
├── .gitignore
└── README.md               ← (ce fichier)
```

## ⚙️ Pré-requis

- Python **3.11+**
- Un environnement virtuel **activé** (cf. mini-cours `01_Setup_environnement_essentiel.md`
  du brief P0)

## 🚀 Démarrage 

```bash
# 0. Se positionner dans le dossier /squelette

# 1. Installer les dépendances dans ton env virtuel activé
uv pip install -r requirements.txt

# 2. Lancer l'API en mode dev (rechargement automatique sur modification)
uvicorn app.main:app --reload
# À l'étape 2, tu peux ouvrir <http://localhost:8000/docs> pour voir l'interface
# Swagger générée automatiquement par FastAPI. L'endpoint `/health` doit déjà répondre
# `{"status": "ok", "model_loaded": true}`.

# 3. Dans un autre terminal : lancer les tests
pytest

# 4. Build image docker
docker build -t fastia-maintenance:dev .

# 5. Run image docker (Docker Desktop doit etre lancé)
docker run --rm -p 8000:8000 fastia-maintenance:dev

# 6. Accès via docker 
http://localhost:8000/health

# 7. Accès aux API via Swagger :
http://localhost:8000/docs

```

## 🔁 Régénérer le dataset ou le modèle (optionnel)

Le dataset et le modèle sont déjà fournis. Tu n'as **pas besoin** de les
régénérer pour le brief. Si tu veux le faire :

```bash
# Régénérer le dataset (déterministe, random_state=42)
python data/generate_dataset.py

# Réentraîner le modèle baseline (~30 secondes)
python model/train_baseline.py
```

## 🆘 En cas de problème au démarrage

| Symptôme | Cause probable | Solution |
|---|---|---|
| `ModuleNotFoundError` au lancement | env virtuel pas activé ou deps pas installées | `source .venv/bin/activate` puis `pip install -r requirements.txt` |
| `Modèle introuvable` au démarrage uvicorn | `model.joblib` absent ou mal placé | `python model/train_baseline.py` pour le régénérer |
| `pytest` échoue tout de suite | env virtuel actif ? deps installées ? | idem ligne 1 |
| Port 8000 déjà utilisé | un autre service tourne dessus | `uvicorn app.main:app --reload --port 8001` |

## 📚 Pour aller plus loin

Le brief M0-B1 (`brief.md`) liste les ressources et les compétences visées.
Les mini-cours synthétiques sont dans `briefs/M0-B1/ressources/` :

- `01_FastAPI_essentiel.md`
- `02_Docker_essentiel.md`
- `03_Loguru_essentiel.md`
- `04_Pytest_API_essentiel.md`