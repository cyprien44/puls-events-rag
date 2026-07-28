
"""
Récupération et nettoyage des événements Open Agenda
=====================================================
Récupère tous les événements du filtre retenu (Paris, 2 mois),
via pagination, ne garde que les champs utiles, nettoie le HTML,
et sauvegarde un jeu de données propre pour la suite (Faiss).

Étape 2 de la mission : Pré-processing des données Open Agenda.
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date, timedelta

API_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"
VILLE = "Paris"
PERIODE_JOURS = 60
TAILLE_PAGE = 100  # maximum autorisé par l'API en un seul appel

# Le filtre retenu à l'étape précédente
aujourdhui = date.today().isoformat()
dans_x_jours = (date.today() + timedelta(days=PERIODE_JOURS)).isoformat()
WHERE_CLAUSE = (
    f'location_city="{VILLE}" '
    f'and firstdate_begin >= date\'{aujourdhui}\' '
    f'and firstdate_begin <= date\'{dans_x_jours}\''
)

# Les seuls champs qu'on garde (inutile de tout télécharger)
CHAMPS_A_GARDER = [
    "uid", "title_fr", "description_fr", "longdescription_fr",
    "firstdate_begin", "firstdate_end",
    "location_name", "location_address", "location_city",
    "category", "keywords_fr", "canonicalurl",
]


def nettoyer_html(texte: str) -> str:
    """Retire les balises HTML (<p>, <br>, etc.) et ne garde que le texte."""
    if not texte:
        return ""
    return BeautifulSoup(texte, "html.parser").get_text(separator=" ").strip()


def recuperer_tous_les_evenements() -> list[dict]:
    """Récupère tous les événements du filtre, page par page."""
    tous_les_evenements = []
    offset = 0

    while True:
        params = {
            "where": WHERE_CLAUSE,
            "select": ",".join(CHAMPS_A_GARDER),  # on ne demande que les champs utiles
            "limit": TAILLE_PAGE,
            "offset": offset,
        }
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        resultats = data["results"]
        tous_les_evenements.extend(resultats)
        print(f"  Page récupérée : offset={offset}, {len(resultats)} événements (total cumulé : {len(tous_les_evenements)})")

        if len(resultats) < TAILLE_PAGE:
            break  # on a atteint la dernière page
        offset += TAILLE_PAGE

    return tous_les_evenements


def nettoyer_evenements(evenements: list[dict]) -> pd.DataFrame:
    """Transforme la liste brute en DataFrame propre."""
    df = pd.DataFrame(evenements)

    # Nettoyage du HTML dans la description longue
    df["longdescription_fr"] = df["longdescription_fr"].apply(nettoyer_html)

    # Suppression des doublons (au cas où) sur l'identifiant unique
    df = df.drop_duplicates(subset="uid")

    # Suppression des lignes sans titre ou sans description (inutilisables pour le RAG)
    avant = len(df)
    df = df.dropna(subset=["title_fr", "description_fr"])
    print(f"\nLignes supprimées car titre/description manquant : {avant - len(df)}")

    return df


if __name__ == "__main__":
    print(f"Récupération des événements ({WHERE_CLAUSE})...\n")
    evenements_bruts = recuperer_tous_les_evenements()

    print(f"\nTotal récupéré : {len(evenements_bruts)} événements")

    df = nettoyer_evenements(evenements_bruts)
    print(f"Total après nettoyage : {len(df)} événements")
    print(f"\nColonnes finales : {df.columns.tolist()}")

    # Sauvegarde pour la suite du projet
    df.to_csv("data/evenements_paris.csv", index=False)
    df.to_json("data/evenements_paris.json", orient="records", force_ascii=False, indent=2)

    print("\nFichiers sauvegardés : data/evenements_paris.csv et data/evenements_paris.json")