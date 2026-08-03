"""
Évaluation automatique avec Ragas — métrique de fidélité (faithfulness)
========================================================================
Mesure objectivement si les réponses du système s'appuient sur les
sources récupérées (détection d'hallucinations), sans jugement humain.

Étape Évaluation de la mission (complément automatique).
"""

import os
import asyncio
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics import Faithfulness
from ragas.dataset_schema import SingleTurnSample

from rag_chain import repondre, _vectorstore

load_dotenv()

# LLM et embeddings "juges" (Mistral), enveloppés pour Ragas
llm_juge = LangchainLLMWrapper(ChatMistralAI(model="mistral-small-latest", temperature=0))
emb_juge = LangchainEmbeddingsWrapper(MistralAIEmbeddings(model="mistral-embed"))

faithfulness = Faithfulness(llm=llm_juge)

# 3 questions représentatives (1 standard, 1 sens, 1 concert)
questions = [
    "Que puis-je faire avec mes enfants à Paris ?",
    "J'aimerais écouter des artistes jouer en direct",
    "Je cherche une exposition d'art contemporain",
]


async def evaluer():
    scores = []
    for question in questions:
        # On récupère la réponse ET les contextes utilisés
        documents = _vectorstore.similarity_search(question, k=4)
        contextes = [doc.page_content for doc in documents]
        sortie = repondre(question)

        echantillon = SingleTurnSample(
            user_input=question,
            response=sortie["reponse"],
            retrieved_contexts=contextes,
        )

        score = await faithfulness.single_turn_ascore(echantillon)
        scores.append(score)
        print(f"\nQuestion : {question}")
        print(f"  Fidélité (faithfulness) : {score:.2f}")

    moyenne = sum(scores) / len(scores)
    print("\n" + "=" * 50)
    print(f"SCORE MOYEN DE FIDÉLITÉ : {moyenne:.2f} / 1.00")
    print("=" * 50)
    print("(1.00 = aucune hallucination, réponses 100% fidèles aux sources)")


if __name__ == "__main__":
    asyncio.run(evaluer())