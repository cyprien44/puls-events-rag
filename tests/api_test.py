"""
Tests fonctionnels de l'API RAG Puls-Events
=============================================
Vérifie automatiquement que les endpoints de l'API répondent correctement.
Prérequis : l'API doit tourner (uvicorn api.main:app) dans un autre terminal.

Étape 5 de la mission : test fonctionnel de l'API.
"""

import requests

# Adresse de l'API lancée en local
BASE_URL = "http://127.0.0.1:8000"


def test_api_en_ligne():
    """Vérifie que l'API répond sur l'endpoint d'accueil."""
    reponse = requests.get(f"{BASE_URL}/")
    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "ok"
    print("✅ test_api_en_ligne : l'API est en ligne")


def test_question_valide():
    """Vérifie qu'une vraie question renvoie une réponse + des sources."""
    payload = {"question": "Que faire avec des enfants à Paris ?", "k": 4}
    reponse = requests.post(f"{BASE_URL}/ask", json=payload)

    assert reponse.status_code == 200
    data = reponse.json()

    # La réponse doit contenir un texte et une liste de sources
    assert "reponse" in data
    assert "sources" in data
    assert len(data["reponse"]) > 0
    assert len(data["sources"]) > 0
    print("✅ test_question_valide : réponse et sources bien renvoyées")
    print(f"   → {len(data['sources'])} sources retournées")


def test_question_vide():
    """Vérifie qu'une question vide est bien rejetée avec une erreur 400."""
    payload = {"question": "", "k": 4}
    reponse = requests.post(f"{BASE_URL}/ask", json=payload)

    assert reponse.status_code == 400
    print("✅ test_question_vide : question vide correctement rejetée (400)")


if __name__ == "__main__":
    print("Lancement des tests de l'API...\n")
    test_api_en_ligne()
    test_question_valide()
    test_question_vide()
    print("\n🎉 Tous les tests sont passés avec succès !")