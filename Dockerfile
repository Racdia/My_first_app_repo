FROM python:3.12-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    libnss3 libxss1 libgconf-2-4 libatk-bridge2.0-0 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Définir les variables d'environnement pour Chromium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Définir le répertoire de travail dans le container
WORKDIR /app

# Copier l'ensemble de votre projet dans le container
COPY . /app

# Installer les dépendances Python depuis requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Commande de démarrage de l'application Streamlit
CMD ["streamlit", "run", "my_data_app.py"]
