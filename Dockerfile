FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    libnss3 libxss1 libgconf-2-4 libatk-bridge2.0-0 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["streamlit", "run", "my_data_app.py"]
