"""API FastAPI — service de classification de criticité (M0-B1).

Expose un modèle scikit-learn pré-entraîné (cf. `model/train_baseline.py`) via
deux routes :

- `GET /health`  : santé du service (déjà fonctionnel)
- `POST /predict` : prédiction de criticité (🎯 à compléter par l'apprenant)

Le modèle est chargé une seule fois au démarrage via le `lifespan` FastAPI puis
réutilisé pour chaque requête.

Lancement local :
    uvicorn app.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
import time
from typing import Any

import joblib
from fastapi import FastAPI, HTTPException
from loguru import logger

import pandas as pd

from app.schemas import HealthResponse, MachineInput, PredictionResponse

MODEL_PATH = Path(__file__).resolve().parents[1] / "model" / "model.joblib"

# Mémoire d'application — peuplée par le lifespan
state: dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Charge le modèle au démarrage, libère à l'arrêt.

    Args:
        app: instance FastAPI.
    """
    if not MODEL_PATH.is_file():
        logger.error(
            f"Modèle introuvable : {MODEL_PATH}. "
            f"Lance d'abord : python model/train_baseline.py"
        )
        raise RuntimeError(f"Modèle introuvable : {MODEL_PATH}")

    logger.info(f"Chargement du modèle depuis {MODEL_PATH}")
    state["model"] = joblib.load(MODEL_PATH)
    logger.info("Modèle chargé.")

    yield

    state.clear()
    logger.info("Service arrêté, état libéré.")


app = FastAPI(
    title="FastIA — Service de criticité maintenance prédictive",
    description=(
        "API d'exposition d'un modèle scikit-learn de classification de criticité "
        "d'incidents machine (3 classes : basse, moyenne, haute)."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Retourne le statut du service et du modèle.

    Returns:
        HealthResponse — `status="ok"` si le modèle est chargé, `degraded` sinon.
    """
    logger.info("Vérification de la santé du service...")
    
    is_loaded = "model" in state
    return HealthResponse(
        status="ok" if is_loaded else "degraded",
        model_loaded=is_loaded,
    )


@app.post("/predict", response_model=PredictionResponse)
def predict(item: MachineInput) -> PredictionResponse:
    start_time = time.time()
    logger.info(f"Entrée : {item}")
                
    dataFrame = pd.DataFrame([item.model_dump()])
    model = state["model"]
    prediction = model.predict(dataFrame)[0] # classe de prédiction
    probabilities = model.predict_proba(dataFrame)[0] # probabilités pour chaque classe
    classes = model.classes_

    logger.info(f"Prédiction de la classe pour ce dataframe: {prediction}")

    logger.info(f"Duree du traitement de la requete: {time.time() - start_time:.2f} secondes")

    return PredictionResponse(
        criticite=prediction,
        probabilites={classes[i]: probabilities[i] for i in range(len(classes))}
    )

   
