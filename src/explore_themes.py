"""
Exploration des données par thème
==================================
Analyse les vraies données d'événements pour construire un jeu de test
annoté crédible : on regarde ce qui existe réellement dans la base,
indépendamment du système RAG.

Étape Évaluation de la mission.
"""

import pandas as pd

df = pd.read_json("data/evenements_paris.json")
print(f"Total d'événements : {len(df)}\n")

# --- 1. Que contient la colonne 'category' ? ---
print("=" * 60)
print("CONTENU DE LA COLONNE 'category'")
print("=" * 60)
print(df["category"].value_counts(dropna=False).head(15))
print()

# --- 2. Comptage par mots-clés dans titre + description ---
print("=" * 60)
print("COMPTAGE PAR THÈME (recherche de mots-clés)")
print("=" * 60)

# On fusionne titre + description pour chercher dedans
texte = (df["title_fr"].fillna("") + " " + df["description_fr"].fillna("")).str.lower()

themes = {
    "concert / musique": ["concert", "musique", "musical", "récital"],
    "exposition / art": ["exposition", "expo", "galerie", "art contemporain"],
    "enfants / famille": ["enfant", "famille", "jeune public"],
    "visite guidée": ["visite", "guidée", "parcours"],
    "atelier": ["atelier", "initiation"],
    "conférence": ["conférence", "rencontre", "débat"],
    "patrimoine": ["patrimoine", "monument", "historique"],
    "théâtre / spectacle": ["théâtre", "spectacle", "pièce"],
}

for theme, mots in themes.items():
    # un événement compte s'il contient AU MOINS un des mots-clés
    masque = texte.str.contains("|".join(mots), regex=True)
    print(f"{theme:<25} : {masque.sum():>4} événements")


def montrer_exemples(mots_cles: list, n: int = 5):
    """Affiche n exemples d'événements correspondant à des mots-clés."""
    masque = texte.str.contains("|".join(mots_cles), regex=True)
    exemples = df[masque].head(n)
    for _, ev in exemples.iterrows():
        print(f"  - {ev['title_fr']}  ({ev['location_name']})")


# --- 3. Exemples concrets pour quelques thèmes ---
print("\n" + "=" * 60)
print("EXEMPLES D'ÉVÉNEMENTS PAR THÈME")
print("=" * 60)

for theme, mots in [("CONCERTS", ["concert", "musique"]),
                    ("EXPOSITIONS", ["exposition", "galerie"]),
                    ("ENFANTS", ["enfant", "famille"])]:
    print(f"\n--- {theme} ---")
    montrer_exemples(mots)