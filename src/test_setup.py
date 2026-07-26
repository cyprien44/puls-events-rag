import os
from dotenv import load_dotenv
from mistralai.client import Mistral

# Charge les variables du fichier .env (dont ta clé secrète)
load_dotenv()

# Se connecte à Mistral avec ta clé
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# Test 1 : demander une phrase à Mistral
resp = client.chat.complete(
    model="mistral-small-latest",
    messages=[{"role": "user", "content": "Dis bonjour en une phrase."}],
)
print("Réponse Mistral :", resp.choices[0].message.content)

# Test 2 : transformer un texte en vecteur (embedding)
emb = client.embeddings.create(model="mistral-embed", inputs=["concert de jazz"])
print("Taille du vecteur :", len(emb.data[0].embedding))
