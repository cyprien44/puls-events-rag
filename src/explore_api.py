"""
Exploration de l'API Open Agenda (via Opendatasoft)
=====================================================
Ce script documente les tests réalisés pour comprendre la structure
des données d'événements culturels et calibrer les filtres (ville, période)
utilisés pour construire le jeu de données du POC "Puls-Events".

Étape 2 de la mission : Pré-processing des données Open Agenda.
"""

import requests
from datetime import date, timedelta

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"
VILLE = "Paris"
PERIODE_JOURS = 60  # fenêtre de 2 mois retenue pour le POC


# ---------------------------------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------------------------------

def interroger_api(where_clause: str, limit: int = 1) -> dict:
    """Envoie une requête à l'API Opendatasoft avec un filtre `where` donné."""
    params = {"where": where_clause, "limit": limit}
    response = requests.get(API_URL, params=params)
    response.raise_for_status()  # déclenche une erreur claire si le statut n'est pas 200
    return response.json()


def compter_evenements(where_clause: str) -> int:
    """Retourne uniquement le nombre total d'événements correspondant au filtre."""
    data = interroger_api(where_clause, limit=1)
    return data.get("total_count", 0)


# ---------------------------------------------------------------------------
# Test 1 : découvrir la structure des données (schéma)
# ---------------------------------------------------------------------------

def test_schema():
    print("=" * 60)
    print("TEST 1 — Découverte du schéma des données")
    print("=" * 60)

    data = interroger_api(f'location_city="{VILLE}"', limit=1)
    premier = data["results"][0]

    print(f"Nombre de champs disponibles : {len(premier.keys())}")
    print("\nChamps clés retenus pour le projet :")
    for champ in ["title_fr", "description_fr", "firstdate_begin", "location_city", "canonicalurl"]:
        print(f"  - {champ} : {str(premier.get(champ))[:80]}")
    print()


# ---------------------------------------------------------------------------
# Test 2 : calibrer le filtre (ville seule, puis ville + période)
# ---------------------------------------------------------------------------

def test_calibrage_filtres():
    print("=" * 60)
    print("TEST 2 — Calibrage des filtres ville / période")
    print("=" * 60)

    # a) Ville seule, sans filtre de date
    total_ville_seule = compter_evenements(f'location_city="{VILLE}"')
    print(f"a) {VILLE}, toutes dates confondues              : {total_ville_seule:>6} événements")

    # b) Ville + 1 an (recommandation générale de la mission)
    il_y_a_un_an = (date.today() - timedelta(days=365)).isoformat()
    where_1an = f'location_city="{VILLE}" and firstdate_begin >= date\'{il_y_a_un_an}\''
    total_1an = compter_evenements(where_1an)
    print(f"b) {VILLE}, depuis {il_y_a_un_an}                : {total_1an:>6} événements")

    # c) Ville + fenêtre resserrée retenue pour le POC
    aujourdhui = date.today().isoformat()
    dans_x_jours = (date.today() + timedelta(days=PERIODE_JOURS)).isoformat()
    where_poc = (
        f'location_city="{VILLE}" '
        f'and firstdate_begin >= date\'{aujourdhui}\' '
        f'and firstdate_begin <= date\'{dans_x_jours}\''
    )
    total_poc = compter_evenements(where_poc)
    print(f"c) {VILLE}, du {aujourdhui} au {dans_x_jours}        : {total_poc:>6} événements  <-- filtre retenu")
    print()

    return where_poc, total_poc


# ---------------------------------------------------------------------------
# Exécution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_schema()
    where_final, total_final = test_calibrage_filtres()

    print("=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print(f"Filtre retenu pour la suite du projet :\n  {where_final}")
    print(f"Volume estimé : {total_final} événements (adapté à un POC)")