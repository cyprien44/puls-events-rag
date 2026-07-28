"""
Test de la recherche sémantique dans l'index Faiss
===================================================
Charge l'index Faiss et teste la recherche par similarité :
on pose une question, on récupère les événements les plus proches.

Étape 3 de la mission : validation de la base vectorielle.
"""

from langchain_community.vectorstores import FAISS
from build_vectorstore import MistralEmbeddings, CHEMIN_INDEX

# On recharge l'index sauvegardé (pas besoin de tout recalculer)
embeddings = MistralEmbeddings()
vectorstore = FAISS.load_local(
    CHEMIN_INDEX,
    embeddings,
    allow_dangerous_deserialization=True,  # nécessaire pour charger un index local
)
print(f"Index chargé : {vectorstore.index.ntotal} événements\n")


def rechercher(question: str, k: int = 3):
    """Affiche les k événements les plus proches de la question."""
    print("=" * 60)
    print(f"QUESTION : {question}")
    print("=" * 60)

    resultats = vectorstore.similarity_search(question, k=k)
    for i, doc in enumerate(resultats, 1):
        print(f"\n--- Résultat {i} ---")
        print(f"Titre : {doc.metadata.get('titre')}")
        print(f"Date  : {doc.metadata.get('date')}")
        print(f"Lieu  : {doc.metadata.get('lieu')}")
    print()


if __name__ == "__main__":
    # On teste plusieurs questions de nature différente
    rechercher("expositions d'art contemporain")
    rechercher("concert de musique")
    rechercher("activités pour les enfants")