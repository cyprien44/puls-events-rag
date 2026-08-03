"""Calcule le taux de réussite à partir des jugements annotés."""
import json
from collections import Counter

with open("data/evaluation_annotee.json", encoding="utf-8") as f:
    data = json.load(f)

total = len(data)
jugements = Counter(d["jugement"] for d in data)

print("=" * 50)
print("RÉSULTATS DE L'ÉVALUATION")
print("=" * 50)
print(f"Total de questions : {total}")
for jug in ["correcte", "partielle", "incorrecte"]:
    n = jugements.get(jug, 0)
    print(f"  {jug:<12} : {n:>2} ({100*n/total:.0f}%)")

# Détail par type de question
print("\nDétail par type :")
types = set(d["type"] for d in data)
for t in sorted(types):
    sous = [d for d in data if d["type"] == t]
    ok = sum(1 for d in sous if d["jugement"] == "correcte")
    print(f"  {t:<10} : {ok}/{len(sous)} correctes")