# Image de départ : une version légère de Python 3.10
FROM python:3.10-slim

# Dossier de travail à l'intérieur de la boîte
WORKDIR /app

# 1. On copie d'abord la liste des dépendances (pour optimiser le cache Docker)
COPY requirements.txt .

# 2. On installe toutes les bibliothèques
RUN pip install --no-cache-dir -r requirements.txt

# 3. On copie tout le code du projet dans la boîte
COPY src/ ./src/
COPY api/ ./api/
COPY data/ ./data/

# 4. On expose le port 8000 (celui de l'API)
EXPOSE 8000

# 5. Commande lancée au démarrage de la boîte : démarrer l'API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]