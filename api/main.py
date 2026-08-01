"""
API REST du système RAG Puls-Events
=====================================
Expose le chatbot de recommandation d'événements via une API REST.

Endpoints :
  - GET  /            : vérifie que l'API est en ligne
  - POST /ask         : pose une question, reçoit une réponse augmentée + sources
  - POST /rebuild     : reconstruit l'index vectoriel Faiss à partir des données

Étape 5 de la mission : exposition du système via une API.
"""

import sys
import os

# Permet d'importer les modules du dossier src/
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag_chain import repondre

app = FastAPI(
    title="Puls-Events RAG API",
    description="Assistant intelligent de recommandation d'événements culturels à Paris.",
    version="1.0.0",
)


# --- Modèles de données (ce que l'API attend et renvoie) ---

class QuestionRequest(BaseModel):
    question: str
    k: int = 4  # nombre d'événements à récupérer (optionnel)


# --- Endpoints ---

@app.get("/")
def accueil():
    """Vérifie que l'API fonctionne."""
    return {"message": "API Puls-Events RAG en ligne", "statut": "ok"}


@app.post("/ask")
def poser_question(requete: QuestionRequest):
    """Prend une question et renvoie une réponse augmentée + les sources."""
    # Gestion d'erreur : question vide
    if not requete.question or not requete.question.strip():
        raise HTTPException(status_code=400, detail="La question ne peut pas être vide.")

    try:
        resultat = repondre(requete.question, k=requete.k)
        return resultat
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement : {str(e)}")


@app.post("/rebuild")
def reconstruire_index():
    """Reconstruit l'index vectoriel Faiss à partir des données."""
    try:
        from build_vectorstore import mode_complet
        mode_complet()
        return {"message": "Index Faiss reconstruit avec succès."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la reconstruction : {str(e)}")