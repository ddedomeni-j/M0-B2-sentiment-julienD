"""Tests fonctionnels de l'endpoint /predict.

Permet de tester la sortie dans dans le cas valide et dans le cas d'un type de machine invalide.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_predict_with_correct_input_returns_200() -> None:
    """L'endpoint /predict doit répondre 200 OK si l'entrée est correcte."""
    with TestClient(app) as client:
        data_ok = {"texte": "C'est un bel hôtel"}
        
        response = client.post("/predict", json=data_ok)
        assert response.status_code == 200


def test_predict_with_wrong_machine_type_returns_error_422() -> None:
    """L'endpoint /predict doit retourner une erreur 422  si le type de machine est incorrect."""
    
    with TestClient(app) as client:
        data_ko = {"age_machine_jours": 1500}
        
        response = client.post("/predict", json=data_ko)
        assert response.status_code == 422

