"""
Construction de la base vectorielle Faiss
==========================================
Transforme les événements nettoyés en vecteurs (embeddings Mistral)
et les indexe dans une base Faiss interrogeable par similarité sémantique.

Deux modes disponibles (voir tout en bas du fichier) :
  - mode_test()    : affiche des exemples sur 3 événements, sans rien construire
  - mode_complet() : vectorise les 881 événements et sauvegarde l'index Faiss

Étape 3 de la mission : Base de données vectorielle.
"""

import os
import time
import pandas as pd
from dotenv import load_dotenv
from mistralai.client import Mistral
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document

load_dotenv()
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

CHEMIN_INDEX = "data/faiss_index"
CHEMIN_DONNEES = "data/evenements_paris.json"


# ---------------------------------------------------------------------------
# Fonctions de préparation
# ---------------------------------------------------------------------------

def valeur_valide(v) -> bool:
    """Vérifie qu'une valeur n'est ni vide, ni None, ni 'nan'."""
    return v is not None and str(v).strip().lower() not in ("", "nan", "none")


def construire_texte(evenement: dict) -> str:
    """Fusionne les champs d'un événement en un seul bloc de texte cohérent."""
    parties = []
    if valeur_valide(evenement.get("title_fr")):
        parties.append(f"Titre : {evenement['title_fr']}")
    if valeur_valide(evenement.get("description_fr")):
        parties.append(f"Description : {evenement['description_fr']}")
    if valeur_valide(evenement.get("longdescription_fr")):
        parties.append(f"Détails : {evenement['longdescription_fr']}")
    if valeur_valide(evenement.get("category")):
        parties.append(f"Catégorie : {evenement['category']}")
    if valeur_valide(evenement.get("location_name")):
        parties.append(f"Lieu : {evenement['location_name']}")
    if valeur_valide(evenement.get("firstdate_begin")):
        parties.append(f"Date : {evenement['firstdate_begin']}")
    return "\n".join(parties)


def construire_documents(df: pd.DataFrame) -> list[Document]:
    """Crée un Document LangChain (texte + métadonnées) par événement."""
    documents = []
    for evenement in df.to_dict(orient="records"):
        texte = construire_texte(evenement)
        metadonnees = {
            "uid": evenement.get("uid"),
            "titre": evenement.get("title_fr"),
            "date": evenement.get("firstdate_begin"),
            "lieu": evenement.get("location_name"),
            "adresse": evenement.get("location_address"),
            "url": evenement.get("canonicalurl"),
        }
        documents.append(Document(page_content=texte, metadata=metadonnees))
    return documents


# ---------------------------------------------------------------------------
# Adaptateur d'embeddings Mistral pour LangChain
# ---------------------------------------------------------------------------

class MistralEmbeddings(Embeddings):
    """Permet à LangChain/Faiss d'utiliser les embeddings Mistral."""

    def _embed(self, textes: list[str]) -> list[list[float]]:
        vecteurs = []
        for i in range(0, len(textes), 50):  # par lots de 50
            lot = textes[i:i + 50]
            reponse = client.embeddings.create(model="mistral-embed", inputs=lot)
            vecteurs.extend([d.embedding for d in reponse.data])
            print(f"  Vectorisé : {min(i + 50, len(textes))}/{len(textes)}")
            time.sleep(0.5)  # pause pour respecter les limites de l'API gratuite
        return vecteurs

    def embed_documents(self, textes: list[str]) -> list[list[float]]:
        return self._embed(textes)

    def embed_query(self, texte: str) -> list[float]:
        return self._embed([texte])[0]


# ---------------------------------------------------------------------------
# MODE TEST — aperçu sur 3 événements, sans rien construire
# ---------------------------------------------------------------------------

def mode_test():
    print("=" * 60)
    print("MODE TEST — aperçu sur 3 événements")
    print("=" * 60)

    df = pd.read_json(CHEMIN_DONNEES)
    print(f"Événements chargés : {len(df)}")

    echantillon = df.head(3).to_dict(orient="records")

    print("\n--- Texte fabriqué pour le 1er événement ---")
    print(construire_texte(echantillon[0]))

    textes = [construire_texte(ev) for ev in echantillon]
    reponse = client.embeddings.create(model="mistral-embed", inputs=textes)

    print("\n--- Vectorisation de test réussie ---")
    print(f"Nombre de vecteurs générés : {len(reponse.data)}")
    print(f"Dimension de chaque vecteur : {len(reponse.data[0].embedding)}")


# ---------------------------------------------------------------------------
# MODE COMPLET — vectorise tout et sauvegarde l'index Faiss
# ---------------------------------------------------------------------------

def mode_complet():
    print("=" * 60)
    print("MODE COMPLET — construction de l'index Faiss")
    print("=" * 60)

    df = pd.read_json(CHEMIN_DONNEES)
    print(f"Événements chargés : {len(df)}")

    documents = construire_documents(df)
    print(f"Documents préparés : {len(documents)}")

    print("\nVectorisation en cours (1-2 minutes)...")
    embeddings = MistralEmbeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)

    vectorstore.save_local(CHEMIN_INDEX)
    print(f"\nIndex Faiss sauvegardé dans : {CHEMIN_INDEX}")
    print(f"   Nombre d'événements indexés : {vectorstore.index.ntotal}")


# ---------------------------------------------------------------------------
# Choix du mode à exécuter
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    #mode_test()       # aperçu rapide (par défaut)
    mode_complet()  # construction complète de l'index