import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("MISTRAL_API_KEY")

if key is None:
    print("❌ Aucune clé trouvée — le fichier .env n'est pas lu correctement.")
else:
    print(f"✅ Clé trouvée, longueur : {len(key)} caractères")
    print(f"Début : {key[:4]}...  Fin : ...{key[-4:]}")

