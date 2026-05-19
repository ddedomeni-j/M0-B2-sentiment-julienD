"""Tests fonctionnels de l'endpoint /predict.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
import pytest


def test_predict_returns_200() -> None:
    """L'endpoint /predict doit répondre 200 OK avec la structure vérifiée."""
    with TestClient(app) as client:
        response = client.post("/predict", json={
            "age_machine_jours": 1500,
            "derniere_maintenance_jours": 45,
            "nb_incidents_3_mois": 2,
            "pression_moyenne": 7.8,
            "temperature_moyenne": 68.5,
            "type_machine": "compresseur",
            "vibration_moyenne": 3.2
        })  
        assert response.status_code == 200
        body = response.json()
        assert body["criticite"] == "basse"
        assert len(body["probabilites"]) == 3


def test_predict_invalid_input() -> None:
    """L'endpoint /predict doit répondre 422 si entrée incorrecte."""
    with TestClient(app) as client:
        response = client.post("/predict", json={
            "tot": 0,  # champ invalide
        })
        assert response.status_code == 422


@pytest.mark.parametrize(
    "type_machine",
    ["pompe", "compresseur", "convoyeur", "presse", "four"],
)
def test_predict_all_types(type_machine: str) -> None:
    """Teste l'endpoint /predict pour les 5 types de machines du dataset."""
    payload = {
        "age_machine_jours": 1500,
        "derniere_maintenance_jours": 45,
        "nb_incidents_3_mois": 2,
        "pression_moyenne": 7.8,
        "temperature_moyenne": 68.5,
        "type_machine": type_machine,
        "vibration_moyenne": 3.2,
    }

    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["criticite"] == "basse"
        assert len(body["probabilites"]) == 3
        probs = body["probabilites"]
        assert set(probs.keys()) == {"basse", "moyenne", "haute"}
        assert sum(probs.values()) == pytest.approx(1.0, rel=1e-6)

