# M0-B2 : sentiment FR Aubergine Hôtels

Ce code propose une interface permettant d'analyser les commentaires reçus par une chaîne d'hôtels. 
L'application est composée de 2 services. Le premier développé avec STreamlit est une UI qui permet d'appeler
un service basé sur le modèle DistilCamemBERT permettant de classer les avis en positifs, négatifs ou neutre.

## Architecture

<img src="./images/ArchitectureM0_B2.jpg" width="1500">

## Organisation du repo

```
M0-B1-maintenance-JulienD/
├── data/
│   ├── README.md
│   ├── sample_reviews.csv             ← Cas tests
├── images/                            ← illustrations Readme     
├── postman/
│   └── M0-B2_collection.json          ← Collection des tests manuels
├── services/  
│   ├── api-nlp/                       ← FastAPI + transformers
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── main.py                ← routes (lifespan + /health + /info + /predict)
│   │   │   ├── schemas.py             ← Pydantic ReviewIn / SentimentOut
│   │   │   └── inference.py           ← Appel du modèle
│   │   └── tests/
│   │       └── test_health.py         ← test healthcheck
│   │       └── test_predict.py        ← test inférence
│   └── ui-streamlit/                  ← UI utilisateur
│       ├── Dockerfile
│       ├── requirements.txt
│       └── app.py                     ← UI permettantb de saisir un commentaire et d'appeler le modèle
├── docker-compose.yml                 ← Fichier d'orchestration des services
├── .gitignore
└── README.md                          ← (ce fichier)
```

## Modèle utilisé

**`cmarkea/distilcamembert-base-sentiment`** — DistilCamemBERT FR,
68 M paramètres, ~270 Mo.

⚠️ Les 5 classes de sortie du modèle (`'1 star'` … `'5 stars'`) sont mappées en classes
pour des raisons métier (`négatif/neutre/positif`).

Pour le mapping on va utiliser le critère utilisé dans l'article HuggingFace consiste à sommer les scores 1 étoile et 2 étoiles pour obtenir le score du sentiment "négatif", à sommer les scores 4 et 5 étoiles pour obtenir le score du sentiment positif, et garder le score 3 étoiles pour le score neutre.

On pourrait sommer 2, 3 et 4 étoiles pour le score neutre et ne garder que les extrêmes pour les sentiment négatifs et positifs. 

Pour améliorer les résultats, on pourrait calculer une régression sur les cas tests ou réentrainer le modèle sur les données test pour adapter à une sortie sur 3 classes.

---

## Endpoints API

| Endpoint
|---|---|---|
| `GET /health`
| `GET /info`
| `POST /predict`

---

## Healthcheck

Le `docker-compose.yml` inclut un `healthcheck` sur `api-nlp`. Au bout de
~40 s (le temps que le modèle se charge), le service passe `healthy`.
Vérification :

```bash
docker compose ps
# m0b2-api-nlp        Up X seconds (healthy)
```

Si le service reste `unhealthy` au bout de 2 min, regarde les logs :
`docker compose logs api-nlp`.

Logs en temps réel : `docker compose logs -f api-nlp`.

## Variables d'environnement (`.env`)

| Variable | Défaut | Usage |
|---|---|---|
| `MODEL_NAME_HF` | `cmarkea/distilcamembert-base-sentiment` | Modèle HF à charger |
| `MAX_TEXT_LENGTH` | `2000` | Validation Pydantic (longueur max texte) |

---

## Tests

Lancement des tests **dans le conteneur API** :

```bash
docker compose exec api-nlp pytest -v
```

## Limites du modèle

Certains avis ne sont pas classés conformément à la note client

1. Review positive classée neutre : "Pas mauvais du tout, on s'attendait à pire vu les avis. Bonne surprise sur le rapport qualité-prix."

```
{
    "sentiment": "neutre",
    "scores_5_stars": {
        "3 stars": 0.6678569912910461,
        "2 stars": 0.1897788941860199,
        "4 stars": 0.11319638788700104,
        "1 star": 0.018008295446634293,
        "5 stars": 0.01115933433175087
    },
    "model_name": "cmarkea/distilcamembert-base-sentiment",
    "latence_ms": 19.54174041748047
}
```

Le LLM semble mal analyser les relations entre les mots privilégiant "pas mauvais", "on s'attendait àpire" à "Bonne surprise". Ce n'est pas un contre-sens complet mais on note que la classe qui arrive deuxième est 2 étaoiles. Le modèle aurait dû privilégier la classe 4 étoiles en 2 deuxième, ce qui confirme que les éléments individuels ont été déterminants plus que l'association de ce éléments.

2. Review neutre classée positive : "Etablissement standard, conforme à  la description. Rien à signaler de particulier."

```
{
    "sentiment": "positif",
    "scores_5_stars": {
        "4 stars": 0.5424525141716003,
        "5 stars": 0.35321828722953796,
        "3 stars": 0.09587699919939041,
        "2 stars": 0.006946119945496321,
        "1 star": 0.0015061176382005215
    },
    "model_name": "cmarkea/distilcamembert-base-sentiment",
    "latence_ms": 23.793935775756836
}
```

Il s'agit clairement d'une erreur manifeste du modèle. Rien dans la phrase n'est positif, le score 3 étoiles aurait dû être largement supérieur à ceux des 4 autres classes.

3. Review négative classée positive : "On a passé un séjour qu'on n'oubliera pas. La climatisation en panne en plein août, sympa."

{
    "sentiment": "positif",
    "scores_5_stars": {
        "4 stars": 0.5082716345787048,
        "5 stars": 0.39503979682922363,
        "3 stars": 0.08835653215646744,
        "2 stars": 0.006615230347961187,
        "1 star": 0.0017168421763926744
    },
    "model_name": "cmarkea/distilcamembert-base-sentiment",
    "latence_ms": 32.874345779418945
}

Le modèle n'a pas analysé correctement les relations entre les éléments de la phrase. Encore une fois les élements sympa, "séjour qu'on n'oubliera pas" ont pris le pas sur le sens global et l'ironie du message.

Les scores associés à ces requêtes montre que la correction de ces erreurs ne pourra se faire qu'avec un meilleur modèle avec plus de paramètres ou en faisant un finetuning sur un  corpus de données plus représentatif des avis hôtelier. Améliorer le mapping ne suffira pas à améliorer les résultats.

---
