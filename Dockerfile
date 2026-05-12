FROM python:3.11-slim

WORKDIR /app

# Install curl to download sprites
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY app.py .
COPY templates/ templates/

# Download APRS symbol sprites from hessu/aprs-symbols (aprs.fi open source set)
RUN curl -fsSL "https://raw.githubusercontent.com/hessu/aprs-symbols/master/png-dist/aprs-symbols-24.png" \
        -o templates/static/aprs-symbols-24-0.png && \
    curl -fsSL "https://raw.githubusercontent.com/hessu/aprs-symbols/master/png-dist/aprs-symbols-24-2.png" \
        -o templates/static/aprs-symbols-24-1.png

EXPOSE 3169

CMD ["python", "app.py"]
