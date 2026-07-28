"""
Chaîne RAG : recherche (Faiss) + génération (Mistral)
======================================================
Assemble le système complet : à partir d'une question, on récupère
les événements pertinents dans Faiss, puis Mistral rédige une
recommandation en langage naturel en s'appuyant sur ces événements.

Étape 4 de la mission : intégration LangChain / système RAG.
"""

import os
from dotenv import load_dotenv
from mistralai.client import Mistral
from langchain_community.vectorstores import FAISS
from build_vectorstore import MistralEmbeddings, CHEMIN_INDEX

load_dotenv()
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# On charge l'index Faiss une seule fois au démarrage
_embeddings = MistralEmbeddings()
_vectorstore = FAISS.load_local(
    CHEMIN_INDEX, _embeddings, allow_dangerous_deserialization=True
)


# Le prompt système : il cadre le comportement de Mistral
PROMPT_SYSTEME = """Tu es un assistant culturel qui recommande des événements à Paris.
Réponds UNIQUEMENT à partir des événements fournis dans le contexte ci-dessous.
Si aucun événement ne correspond à la demande, dis-le honnêtement sans inventer.
Pour chaque recommandation, indique le titre, la date et le lieu de l'événement.
Sois clair, chaleureux et concis."""


def formater_contexte(documents) -> str:
    """Met en forme les événements trouvés pour les donner à Mistral."""
    blocs = []
    for i, doc in enumerate(documents, 1):
        blocs.append(
            f"Événement {i} :\n"
            f"- Titre : {doc.metadata.get('titre')}\n"
            f"- Date : {doc.metadata.get('date')}\n"
            f"- Lieu : {doc.metadata.get('lieu')}\n"
            f"- Adresse : {doc.metadata.get('adresse')}\n"
            f"- Description : {doc.page_content[:300]}\n"
            f"- Lien : {doc.metadata.get('url')}"
        )
    return "\n\n".join(blocs)


def repondre(question: str, k: int = 4) -> dict:
    """Fonction principale du RAG : question -> réponse augmentée + sources."""
    # 1. RECHERCHE : trouver les k événements les plus pertinents
    documents = _vectorstore.similarity_search(question, k=k)
    contexte = formater_contexte(documents)

    # 2. GÉNÉRATION : Mistral rédige à partir du contexte
    messages = [
        {"role": "system", "content": PROMPT_SYSTEME},
        {"role": "user", "content": f"Contexte (événements disponibles) :\n\n{contexte}\n\nQuestion de l'utilisateur : {question}"},
    ]
    reponse = client.chat.complete(model="mistral-small-latest", messages=messages)
    texte_reponse = reponse.choices[0].message.content

    # 3. On renvoie la réponse ET les sources (pour la transparence)
    sources = [
        {"titre": d.metadata.get("titre"), "date": d.metadata.get("date"),
         "lieu": d.metadata.get("lieu"), "url": d.metadata.get("url")}
        for d in documents
    ]
    return {"reponse": texte_reponse, "sources": sources}


if __name__ == "__main__":
    questions_test = [
        "Que puis-je faire avec mes enfants à Paris ?",
        "Y a-t-il des concerts ou de la musique ?",
        "Je cherche une exposition d'art contemporain",
        "Peux-tu me recommander un match de football américain ?",  # question piège : peu probable dans les données
    ]

    for question in questions_test:
        print("\n" + "#" * 70)
        print(f"QUESTION : {question}")
        print("#" * 70)
        resultat = repondre(question)
        print(resultat["reponse"])