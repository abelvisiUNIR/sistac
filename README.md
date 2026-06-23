# SISTAC — Sistema Inteligente de Selección de Talento y Análisis Curricular

**Trabajo Fin de Estudios — Máster en Inteligencia Artificial y Data Science**  
Universidad Internacional de La Rioja (UNIR) · Entrega: 15 julio 2026

**Equipo:**
- David I. Madrid Oyanadel — Lead Engineer H2 (Pipeline RAG y scoring semántico)
- Mario A. Belvisi Lescano — Lead Analyst H3 (Módulo PII y equidad algorítmica)

**Socio organizacional:** Matriz Uruguay  
**Tutora:** Marta María Arguedas Lafuente

---

## ¿Qué es SISTAC?

SISTAC evalúa cuatro configuraciones de pre-selección de CVs con modelos de lenguaje (LLMs), midiendo su eficiencia, eficacia y equidad algorítmica mediante un diseño factorial:

| Config | Nombre | Descripción |
|--------|--------|-------------|
| **C0** | Screening Manual | Revisor humano RRHH (línea base) |
| **C1** | LLM Puro | Claude Sonnet sin contexto externo |
| **C2** | LLM + RAG | Claude Sonnet + Azure AI Search (retrieval híbrido) |
| **C3** | LLM + RAG + PII | C2 con anonimización de datos personales (Presidio + spaCy) |

**Hipótesis del Experimento:**
- **H1** — El sistema automatizado es significativamente más rápido que el screening manual (eficiencia).
- **H2** — Las configuraciones RAG alcanzan un F1-score >= 0.85 comparado con el Gold Standard de los expertos (eficacia).
- **H3** — La anonimización PII reduce significativamente la disparidad demográfica y el sesgo de género/edad respecto a C1/C2 (equidad).

---

## Estructura del Proyecto (Rama main)

Esta rama contiene exclusivamente el código fuente de la aplicación, backend web, frontend interactivo y scripts de lógica algorítmica:

```text
sistac/
├── README.md                        <- Este archivo (documentación del código)
├── CHANGELOG.md                     <- Historial de cambios del proyecto
├── .env.example                     <- Variables de entorno requeridas (sin valores)
├── .gitignore                       <- Archivos ignorados por Git
├── Dockerfile                       <- Definición de contenedor Docker para FastAPI
├── docker-compose.yml               <- Orquestación de contenedores (app + mongodb)
├── azure-pipelines.yml              <- Configuración de CI/CD
│
├── app/                             # Aplicación FastAPI y Frontend Web
│   ├── main.py                      # Servidor API de FastAPI y endpoints
│   └── static/                      # Interfaz web (dashboard interactivo)
│       └── index.html
│
├── data/                            # Insumos de datos para pruebas y inicialización
│   ├── raw/
│   │   ├── cvs/                     # CVs sintéticos (CV_001.txt a CV_300.txt)
│   │   ├── job_descriptions/        # Descripciones de cargos (JD_001.txt a JD_005.txt)
│   │   └── gold_standard/           # ground_truth.csv + c0_times.csv
│   └── cleaned/
│       └── evaluation_sets/         # train_ids.csv + test_ids.csv
│
└── scripts/python/                  # Código Python del backend y algoritmos
    ├── config.py                    # Configuración global y rutas
    ├── requirements.txt             # Dependencias del proyecto
    ├── data/                        # Ingesta y preparación de datos (seed_mongodb.py, etc.)
    ├── evaluation/                  # Lógica de cálculo de métricas (H1, H2, H3)
    ├── experiments/                 # Orquestador del experimento (orquestador_c0_c3.py)
    ├── llm/                         # Abstracción de modelos de lenguaje (provider.py)
    ├── pii/                         # Módulo de anonimización Presidio/spaCy (H3)
    ├── rag/                         # Pipeline RAG y búsquedas en Azure Search (H2)
    ├── scoring/                     # Motor de scoring semántico (scorer.py)
    └── utils/                       # Utilidades de extracción de texto (doc_extractor.py, docx_extractor.py)
```

---

## Componentes Principales — Referencia del Código

### 1. `app/` (Backend y Frontend de la Aplicación)
* **`app/main.py`:** Servidor web FastAPI. Expone la API del sistema:
  * `/api/cargo` (Ingesta de perfiles y creación de índices).
  * `/api/evaluar` (Evaluación de candidatos en tiempo real).
  * `/api/casos/simular-candidato` (Generación de PII).
  * `/api/admin/descargar-tablas` (Exportador dinámico de reportes).
* **`app/static/index.html`:** Dashboard interactivo que permite subir ofertas de cargo, evaluar currículums (individualmente o por lotes), visualizar puntuaciones, comparar modelos lingüísticos y descargar reportes consolidados en Excel.

### 2. `scripts/python/` (Núcleo Algorítmico)
* **`scripts/python/config.py`:** Inicialización y configuración del proyecto. Define hiperparámetros como el tamaño de chunk (512 tokens), overlap (64), umbral de aptitud (70) y selección de modelos de lenguaje.
* **`scripts/python/pii/anonymizer.py` (H3):** Sistema de anonimización de datos sensibles basado en Microsoft Presidio y spaCy (`es_core_news_lg`), que neutraliza variables como nombre, género, edad, datos de contacto y locación para mitigar el sesgo algorítmico.
* **`scripts/python/rag/pipeline.py` (H2):** Pipeline RAG que coordina la recuperación híbrida en Azure AI Search, el armado de prompts dinámicos y la generación de la calificación.
* **`scripts/python/scoring/scorer.py`:** Motor de scoring que evalúa a los candidatos en base a cuatro dimensiones ponderadas: Competencias Técnicas (40%), Experiencia Laboral (30%), Formación Académica (20%) y Habilidades Blandas (10%).
* **`scripts/python/evaluation/`:** Módulos estadísticos encargados de procesar la velocidad de screening (H1), calcular concordancia F1-score y curvas ROC (H2), y medir la equidad a través del impacto dispar (DIR/SPD) en la contratación (H3).

---

## Primeros Pasos — Instalación y Ejecución

Sigue estos pasos en orden para levantar la aplicación e inicializarla:

### 1. Requisitos Previos
* Python 3.10 o superior instalado.
* Base de datos MongoDB levantada localmente o un endpoint activo.
* Credenciales de Azure AI Search y API Keys de proveedores de LLM.

### 2. Clonación e Instalación
```bash
# Entrar a la carpeta del proyecto
cd clo-author

# Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\activate          # En Windows
source .venv/bin/activate        # En Mac / Linux

# Instalar dependencias
pip install -r scripts/python/requirements.txt

# Instalar el modelo lingüístico de spaCy para español
python -m spacy download es_core_news_lg
```

### 3. Configuración del Archivo `.env`
Copia el archivo `.env.example` como `.env` y rellena las credenciales correspondientes:
```bash
copy .env.example .env          # En Windows
cp .env.example .env            # En Mac / Linux
```

### 4. Inicializar Base de Datos (Seeding)
Para sembrar MongoDB con los datos sintéticos iniciales de currículums, ofertas y tablas maestras para pruebas:
```bash
python scripts/python/data/seed_mongodb.py
```

### 5. Levantar el Servidor de Desarrollo
```bash
python -m uvicorn app.main:app --reload --port 8000
```
La aplicación web estará disponible en: [http://localhost:8000](http://localhost:8000)

---

## Control de Versiones

* **Rama `main` (Estable / Evaluación):** Contiene el código fuente depurado del sistema listo para la revisión del tribunal.
* **Rama `desarrollo` (Activa):** Utilizada por el equipo de desarrollo para incorporar nuevas funcionalidades, experimentos, redactar la memoria de tesis y almacenar los resultados físicos detallados.
