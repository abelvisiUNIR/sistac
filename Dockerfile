FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema (spaCy necesita compilador)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Dependencias Python
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn python-multipart

# Modelo spaCy español
RUN python -m spacy download es_core_news_lg

# Código del proyecto
RUN echo "rebuild-1"
COPY sistac/ sistac/
COPY app/ app/
COPY data/ data/
COPY paper/ paper/

# Variables de entorno (las reales vienen de Azure DevOps / Azure App Service)
ENV LLM_PROVIDER=anthropic
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
