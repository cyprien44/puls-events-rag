"""
Évaluation du système RAG — Niveau 1 (classification manuelle assistée)
========================================================================
Pose chaque question du jeu de test annoté au système RAG, affiche la
réponse et les sources, et enregistre le tout pour une évaluation
correcte / partielle / incorrecte.

Étape Évaluation de la mission.
"""

import json
from rag_chain import repondre

CHEMIN_JEU_TEST = "data/jeu_de_test.json"
CHEMIN_RESULTATS = "data/resultats_evaluation.json"


def charger_jeu_test() -> list:
    with open(CHEMIN_JEU_TEST, encoding="utf-8") as f:
        return json.load(f)


def evaluer():
    jeu_test = charger_jeu_test()
    resultats = []

    for cas in jeu_test:
        print("\n" + "#" * 70)
        print(f"QUESTION {cas['id']} [{cas['type']}] : {cas['question']}")
        print(f"Thème attendu : {cas['theme_attendu']}")
        print("#" * 70)

        # On interroge le système RAG
        sortie = repondre(cas["question"])

        print("\n--- RÉPONSE DU SYSTÈME ---")
        print(sortie["reponse"])

        print("\n--- SOURCES RÉCUPÉRÉES (thème vérifiable ici) ---")
        for s in sortie["sources"]:
            print(f"  - {s['titre']} ({s['lieu']})")

        # On enregistre pour analyse (le jugement sera ajouté ensuite)
        resultats.append({
            "id": cas["id"],
            "question": cas["question"],
            "type": cas["type"],
            "theme_attendu": cas["theme_attendu"],
            "reponse_systeme": sortie["reponse"],
            "sources": [s["titre"] for s in sortie["sources"]],
            "jugement": "",  # à remplir : "correcte" / "partielle" / "incorrecte"
        })

    # Sauvegarde des résultats
    with open(CHEMIN_RESULTATS, "w", encoding="utf-8") as f:
        json.dump(resultats, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print(f"✅ {len(resultats)} questions évaluées.")
    print(f"Résultats enregistrés dans : {CHEMIN_RESULTATS}")
    print("=" * 70)
    print("\n👉 Étape suivante : ouvre ce fichier et remplis le champ 'jugement'")
    print("   pour chaque question (correcte / partielle / incorrecte).")


if __name__ == "__main__":
    evaluer()