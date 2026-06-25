# Talento sin nombre: anonimización, LLMs y RAG en el cribado curricular

Repositorio de código del sistema **SISTAC** (Sistema Inteligente de Selección de Talento y Análisis Curricular).

**Trabajo Fin de Estudios — Máster en Inteligencia Artificial y Data Science**  
Universidad Internacional de La Rioja (UNIR) · Entrega: 15 julio 2026

**Autores:**
- David I. Madrid Oyanadel
- Mario A. Belvisi Lescano

---

## ¿Qué es SISTAC?

SISTAC es un sistema que ayuda a filtrar currículums en la primera etapa de un proceso de selección de personal con apoyo de inteligencia artificial. El proyecto no propone una única herramienta, sino que compara **cuatro formas distintas de hacer ese filtrado** para entender qué aporta cada pieza:

- **Revisión manual:** una persona de Recursos Humanos revisa los currículums, como se hace habitualmente. Es el punto de comparación.
- **Inteligencia artificial sola:** un modelo de lenguaje lee el currículum y la descripción del puesto y decide por su cuenta, solo con lo que aprendió durante su entrenamiento.
- **Inteligencia artificial con apoyo de contexto:** el mismo modelo, pero antes de decidir busca y recupera la información más relevante del currículum para fundamentar mejor su evaluación.
- **Inteligencia artificial con anonimización:** igual que la anterior, pero primero se borran del currículum los datos personales (nombre, contacto, etc.) para que no influyan en la decisión.

Sobre estas cuatro formas se midieron tres cosas, planteadas como preguntas:

- **¿Cuánto tiempo ahorra?** Mucho: las versiones automáticas reducen la revisión por candidato de varios minutos a unos pocos segundos.
- **¿Decide tan bien como un experto humano?** No del todo: la coincidencia con el criterio de un panel de especialistas se queda por debajo del nivel exigido, en buena parte por cómo está fijado el punto de corte que separa "apto" de "no apto".
- **¿Es más justa al anonimizar?** No se puede afirmar: las diferencias de trato entre hombres y mujeres no resultan estadísticamente concluyentes, sobre todo porque el grupo de mujeres analizado es muy pequeño.

> **Tecnología empleada:** el evaluador principal es el modelo Claude Sonnet 4.5; Gemini 2.5 Flash actúa como segunda opinión para comprobar la solidez de los resultados y para leer documentos escaneados. La búsqueda de contexto se apoya en Google Vertex AI Search y la anonimización en Microsoft Presidio con spaCy.

**Datos:** la evaluación se hizo sobre un conjunto público de 150 currículums (la mitad adecuados para el puesto y la mitad no), traducidos al español rioplatense. Un panel de especialistas de Recursos Humanos construyó la referencia de decisiones correctas, con un alto grado de acuerdo entre ellos.

---

## Estructura del proyecto

```
sistac/
├── README.md                        <- Este archivo
├── CLAUDE.md                        <- Contexto y reglas para el agente Claude
├── MEMORY.md                        <- Decisiones aprendidas entre sesiones
├── CHANGELOG.md                     <- Historial de cambios del proyecto
├── .env.example                     <- Variables de entorno requeridas (sin valores)
├── Bibliography_base.bib            <- Referencias APA 7 (Mendeley/Zotero)
│
├── paper/                           <- Documento TFE (fuente de verdad)
│   ├── SISTAC_TFE.docx              <- Documento principal Word
│   ├── sections/                    <- Capítulos redactados en Markdown (Cap 0 a 5 + Anexo)
│   ├── figures/                     <- Figuras generadas por scripts (.png 300 dpi)
│   │   ├── cap5/                    <- Diagramas de arquitectura del Capítulo 4
│   │   └── cap6/                    <- Gráficos de resultados del Capítulo 5
│   ├── tables/                      <- Tablas estadísticas (.csv / .docx / .xlsx)
│   └── backups/                     <- Copias de seguridad automáticas del .docx
│
├── data/
│   ├── raw/
│   │   ├── cvs/                     <- CVs sinteticos: CV_001.txt ... CV_300.txt
│   │   ├── job_descriptions/        <- JDs reales de Matriz Uruguay: JD_001...JD_005.txt
│   │   └── gold_standard/           <- ground_truth.csv + c0_times.csv
│   └── cleaned/
│       └── evaluation_sets/         <- train_ids.csv (240) + test_ids.csv (60)
│
├── scripts/python/                  <- Todo el codigo Python del proyecto
│   ├── config.py                    <- Configuracion global y rutas
│   ├── requirements.txt             <- Dependencias del proyecto
│   ├── data/                        <- Generacion y division del corpus
│   ├── evaluation/                  <- Metricas H1, H2, H3
│   ├── experiments/                 <- Orquestador del experimento factorial
│   ├── figures/                     <- Generacion de figuras y actualizacion del .docx
│   ├── llm/                         <- Abstraccion del proveedor LLM
│   ├── pii/                         <- Modulo de anonimizacion PII (H3)
│   ├── rag/                         <- Pipeline RAG y Azure AI Search (H2)
│   ├── scoring/                     <- Motor de scoring semantico
│   └── utils/                       <- Extraccion de texto desde PDF/DOCX/imagenes
│
├── explorations/                    <- Notebooks y scripts de investigacion exploratoria
├── quality_reports/                 <- Planes, logs de sesion y reportes de calidad
├── templates/                       <- Plantillas de documentos internos
└── .claude/                         <- Reglas, agentes y skills del asistente Claude
```

---

## Scripts Python — referencia completa

### `scripts/python/config.py`

**Configuracion global del proyecto.** Define todas las rutas relativas al `PROJECT_ROOT`,
constantes del experimento y variables leidas del `.env`.

Variables clave:
- `PROJECT_ROOT` — raiz del repositorio (detectada automaticamente)
- `CVS_RAW`, `JOB_DESCRIPTIONS`, `GOLD_STANDARD_DIR` — rutas de datos
- `EVAL_SETS` — rutas de los splits train/test
- `CHUNK_SIZE = 512`, `CHUNK_OVERLAP = 64` — hiperparametros de chunking
- `SCORE_THRESHOLD = 70` — umbral de decision APTO/NO_APTO
- `RANDOM_SEED = 42` — semilla global de reproducibilidad
- `VECTORSTORE_PROVIDER` — vector store activo (`google` por defecto; `azure` alternativo)
- `GCP_PROJECT_ID`, `GCP_DATA_STORE_ID`, `GCP_SEARCH_APP_ID` — config de Vertex AI Search (`.env`)
- `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_KEY`, `AZURE_SEARCH_INDEX` — config de Azure (`.env`, alternativa)
- `LLM_MODEL_PROD = "claude-sonnet-4-5-20241022"` — modelo evaluador principal del experimento

---

### `scripts/python/data/`

#### `synthetic_corpus_generator.py`

Genera el corpus sintetico de 300 CVs en espanol rioplatense, calibrado estadisticamente
a partir del Kaggle Resume Dataset (962 CVs, 25 categorias). Produce:

- `data/raw/cvs/CV_001.txt ... CV_300.txt` — CVs con PII ficticia
- `data/raw/gold_standard/ground_truth.csv` — etiquetas APTO/NO_APTO (Gold Standard algoritmico)
- `data/raw/gold_standard/c0_times.csv` — tiempos simulados de screening manual (C0)

```bash
py -3 scripts/python/data/synthetic_corpus_generator.py
```

#### `split_corpus.py`

Divide el corpus en train/test mediante muestreo estratificado por
`(jd_id, expected_label, group_gender)` con `RANDOM_SEED = 42`. Produce los archivos de
IDs en `data/cleaned/evaluation_sets/`.

```bash
py -3 scripts/python/data/split_corpus.py
```

#### `prepare_external_validation.py`

Prepara el **corpus de evaluación del experimento** a partir del dataset público
`netsol/resume-score-details` (Hugging Face): descarga 150 pares CV–JD balanceados
(75 APTO / 75 NO_APTO), los traduce al español rioplatense, infiere el género e imputa los
rangos de edad y los tiempos de la línea base C0. Cachea la muestra en JSON para
reproducibilidad. Produce el `ground_truth.csv` y los `c0_times.csv` en
`data/raw/gold_standard_external/`.

> El corpus sintético de 300 CVs (generado por `synthetic_corpus_generator.py`) se usó como
> banco de pruebas durante el desarrollo; el experimento formal se ejecuta sobre el corpus
> externo preparado por este script.

```bash
py -3 scripts/python/data/prepare_external_validation.py
```

---

### `scripts/python/llm/`

#### `provider.py`

**Abstración del proveedor LLM.** Permite cambiar entre Anthropic, Google (Gemini) y OpenAI modificando la variable de entorno `LLM_PROVIDER` en el archivo `.env`.

Funciones expuestas:
- `get_chat_completion(prompt, system, max_tokens)` → `str` (soporta Claude, Gemini y GPT)
- `get_embedding(text)` → `list[float]` (local sentence-transformers de 768 dimensiones para Anthropic/Google; API de OpenAI para GPT)

---

### `scripts/python/rag/`

#### `create_index.py`

Crea el índice vectorial en el vector store activo. En la ruta **Vertex AI Search** (activa
en el experimento) la indexación es asíncrona desde un bucket de Google Cloud Storage; en la
ruta **Azure AI Search** (alternativa evaluada) crea el índice `sistac-cvs` con su schema
(9 campos: id, cv_id, jd_id, textos, embedding 768 dims, anonymized, chunk_index), búsqueda
híbrida y Semantic Ranker.

```bash
py -3 scripts/python/rag/create_index.py
```

#### `chunking.py`

Dos estrategias de segmentacion de texto:
- `chunk_text(text)` — chunking por caracteres (piloto, mantener por compatibilidad)
- `chunk_text_tokens(text, chunk_size, chunk_overlap)` — chunking por tokens con
  `RecursiveCharacterTextSplitter` de LangChain (512 tokens, overlap 64) — **funcion activa**

#### `index_corpus.py`

Indexa los CVs y JDs en Azure AI Search generando embeddings para cada chunk.

Argumentos:
- `--split train/test/all` — indexar solo el split indicado (usar `train` para el experimento)
- `--config c2/c3` — texto original (C2) o PII anonimizada antes de indexar (C3)
- `--dry-run` — calcular estadisticas sin subir datos
- `--batch-size N` — chunks por batch de upload (default: 50)

```bash
py -3 scripts/python/rag/index_corpus.py --split train             # indice C2
py -3 scripts/python/rag/index_corpus.py --split train --config c3 # indice C3
py -3 scripts/python/rag/index_corpus.py --split train --dry-run   # verificacion
```

#### `pipeline.py`

**Clase `SistacRAGPipeline`** — pipeline unificado C1/C2/C3. Metodo principal:

```python
pipeline = SistacRAGPipeline(config="c2")
resultado = pipeline.evaluate(cv_id, cv_text, jd_text)
# → {score, decision, justification, chunks_used, anonymized, time_seconds}
```

Flujo interno: [C3 → anonimizacion PII] → [C2/C3 → retrieval hibrido Azure] → scoring LLM

#### `ragas_eval.py`

Evaluacion tecnica in-vitro del pipeline RAG usando RAGAS. Metricas:
- `faithfulness` — la justificacion esta respaldada por los chunks recuperados
- `answer_relevancy` — la justificacion responde al cargo evaluado
- `context_precision` — los chunks recuperados son relevantes para la consulta

LLM juez: Claude Haiku via `ChatAnthropic` de LangChain (sin dependencia de OpenAI).

```bash
py -3 scripts/python/rag/ragas_eval.py
```

#### Archivos del piloto (referencia — David Madrid)

| Archivo | Descripcion |
|---------|-------------|
| `evaluate_pilot_c2.py` | Evaluacion piloto de 5 CVs con el pipeline C2 |
| `index_pilot_corpus.py` | Indexacion del corpus piloto (5 CVs) |
| `embedding_generator.py` | Generador de embeddings del piloto |
| `azure_upload.py` | Upload de chunks al indice Azure (piloto) |
| `search_test.py` | Pruebas de busqueda en el indice |
| `upload_test_chunks.py` | Upload de chunks de prueba |

---

### `scripts/python/scoring/`

#### `scorer.py`

**Motor de scoring semantico.** Funcion principal:

```python
score_candidate(cv_text, jd_text, context_chunks=None) → dict
# → {score: int (0-100), dimensions: dict, justification: str, decision: "APTO"|"NO_APTO"}
```

Cuatro dimensiones ponderadas:

| Dimension | Peso | Descripcion |
|-----------|------|-------------|
| Competencias tecnicas | 40% | Skills, herramientas, certificaciones |
| Experiencia laboral | 30% | Anios, roles, sector, nivel jerarquico |
| Formacion academica | 20% | Titulo, institucion, posgrados |
| Soft skills | 10% | Liderazgo, comunicacion, trabajo en equipo |

Configuracion: `temperature=0.0` (deterministico), umbral decision `SCORE_THRESHOLD=70`.

---

### `scripts/python/pii/`

#### `anonymizer.py`

**Clase `SistacAnonymizer`** — anonimizacion de datos personales (H3). Combina:
- Microsoft Presidio (>= 2.2.354) — motor de deteccion de entidades PII
- spaCy con modelo `es_core_news_lg` — NLP en espanol

Entidades detectadas y sustituidas por etiquetas genericas:

| Entidad | Etiqueta |
|---------|----------|
| Nombres de personas | `<PERSONA>` |
| Correos electronicos | `<EMAIL>` |
| Telefonos | `<TELEFONO>` |
| Numeros de identidad | `<ID>` |
| Edades / fechas de nacimiento | `<EDAD>` |
| Referencias de genero explicitas | `<GENERO>` |
| Direcciones fisicas | `<DIRECCION>` |

```python
anonymizer = SistacAnonymizer()
texto_anonimizado = anonymizer.anonymize(texto_cv)
```

#### `recognizers.py`

Reconocedores personalizados de Presidio para el contexto rioplatense: DNI uruguayo,
formatos de telefono locales, etc.

#### `test_anonymization.py`

Suite de 10 tests unitarios — estado: **10/10 PASSED**.

```bash
pytest scripts/python/pii/test_anonymization.py -v
```

---

### `scripts/python/evaluation/`

#### `efficiency_metrics.py`  *(H1)*

Mide tiempo de procesamiento por candidato (`T_cand`) para cada configuracion y calcula
la reduccion porcentual de C1-C3 respecto a C0 (screening manual, 5-10 min/CV).

#### `efficacy_metrics.py`  *(H2)*

Calcula F1-score y AUC-ROC con intervalos de confianza bootstrap comparando predicciones
del sistema contra el Gold Standard de expertos. Compara C1 vs C2 para aislar el efecto RAG.

#### `fairness_metrics.py`  *(H3)*

Métricas de equidad algorítmica:
- `compute_dir()` — Disparate Impact Ratio: `P(APTO|F) / P(APTO|M)` (umbral EEOC: >= 0.80)
- `compute_spd()` — Statistical Parity Difference: `P(APTO|F) - P(APTO|M)` (ideal: 0)
- `fairness_report()` — reporte completo exportado a `paper/tables/`

#### `consolidate_comparison.py`

Consolida los resultados experimentales de las tres hipótesis de todos los proveedores activos (Claude, Gemini, GPT) en una única tabla unificada de comparación de robustez, exportando los resultados a `paper/tables/` en formatos CSV, Markdown y Word (.docx).

#### `analisis_mejoras_estadisticas.py`

Análisis estadístico complementario (sin volver a llamar a los modelos), a partir de los caches `data/eval_cache_anthropic.json` y `data/eval_cache_google.json`. Calcula el umbral de decisión óptimo (Youden y F1-óptimo) y la curva F1-vs-umbral, los intervalos de confianza por bootstrap y el test exacto de Fisher para DIR/SPD por género y edad, y los recuentos por subgrupo. Salidas en `paper/tables/mejoras/`.

```bash
py -3 scripts/python/evaluation/analisis_mejoras_estadisticas.py
```

---

### `scripts/python/experiments/`

#### `orquestador_c0_c3.py`

**Orquestador del experimento factorial.** Ejecuta las cuatro configuraciones sobre el
corpus de evaluación, invoca los modulos de metricas y genera las tablas de resultados
del Capítulo 5 (Validación experimental y resultados) del TFE.

```bash
py -3 scripts/python/experiments/orquestador_c0_c3.py
```

---

### `scripts/python/utils/`

#### `doc_extractor.py`

Extraccion de texto desde multiples formatos con estrategia escalonada:

| Formato | Motor | Condicion |
|---------|-------|-----------|
| PDF con texto nativo | `pdfplumber` | Extrae > 100 caracteres |
| DOCX | `python-docx` | Siempre |
| PDF escaneado / imagen | Gemini 2.5 Flash (OCR) | pdfplumber falla o imagen |

Gemini 2.5 Flash se elige por: acepta PDF nativo, ventana de 1M tokens, costo
~7x inferior a Claude Haiku en tareas de OCR.

#### `docx_extractor.py`

Extractor especifico para `.docx`, preservando estructura de parrafos y tablas.

---

### `scripts/python/figures/`

#### `gen_cap5_figures.py`

Genera las 6 figuras de arquitectura del Capitulo 5 en PNG (300 dpi) usando matplotlib.
Output: `paper/figures/cap5/*.png`

```bash
py -3 scripts/python/figures/gen_cap5_figures.py
```

#### `gen_cap6_figures.py`

Genera los gráficos de resultados (distribución de tiempos, curva ROC, impacto dispar)
en PNG (300 dpi). Output: `paper/figures/cap6/*.png`.

```bash
py -3 scripts/python/figures/gen_cap6_figures.py
```

#### `gen_track3_figures.py`

Genera las figuras del análisis estadístico complementario (F₁ vs. umbral y DIR por género
con intervalos de confianza) a partir de los CSV de `paper/tables/mejoras/`. Output:
`paper/figures/mejoras/*.png`.

```bash
py -3 scripts/python/figures/gen_track3_figures.py
```

#### `insert_cap5_docx.py`

Inserta el contenido de los capítulos técnicos en el `.docx` generando XML compatible
con la plantilla UNIR. Crea backup automatico antes de modificar.

```bash
py -3 -X utf8 scripts/python/figures/insert_cap5_docx.py
```

---

## Flujo de trabajo del experimento

```
1. Preparar el corpus de evaluación (dataset externo netsol/resume-score-details)
   py -3 scripts/python/data/prepare_external_validation.py
   # (opcional) corpus sintético de desarrollo:
   # py -3 scripts/python/data/synthetic_corpus_generator.py

2. Dividir en train/test (stratified, seed=42)
   py -3 scripts/python/data/split_corpus.py

3. Crear el índice en el vector store activo (Google Vertex AI Search por defecto)
   py -3 scripts/python/rag/create_index.py

4. Indexar el split de entrenamiento
   py -3 scripts/python/rag/index_corpus.py --split train             # indice C2
   py -3 scripts/python/rag/index_corpus.py --split train --config c3 # indice C3

5. Ejecutar el experimento factorial (C0-C3) sobre el split de test
   py -3 scripts/python/experiments/orquestador_c0_c3.py

6. (Opcional) Análisis estadístico complementario y figuras
   py -3 scripts/python/evaluation/analisis_mejoras_estadisticas.py
   py -3 scripts/python/figures/gen_track3_figures.py

7. Resultados: paper/tables/ y paper/figures/
```

---

## Variables de entorno (`.env`)

Copiar `.env.example` a `.env` y completar:

```
# Proveedor y Modelo LLM
LLM_PROVIDER=anthropic         # anthropic | google | openai
ANTHROPIC_API_KEY=...          # Claude Sonnet (LLM principal)
GOOGLE_API_KEY=...             # Gemini 2.5 Flash (extracción de documentos y LLM de Google)

# Vector Store Activo (google | azure)
VECTORSTORE_PROVIDER=google    # google (activo en el experimento) | azure (alternativa evaluada)

# Azure AI Search (si VECTORSTORE_PROVIDER=azure)
AZURE_SEARCH_ENDPOINT=...      # https://xxx.search.windows.net
AZURE_SEARCH_KEY=...           # API Key de Azure AI Search
AZURE_SEARCH_INDEX=sistac-cvs  # Nombre del índice vectorial

# Google Vertex AI Search (si VECTORSTORE_PROVIDER=google)
GCP_PROJECT_ID=...
GCP_LOCATION=global
GCP_DATA_STORE_ID=sistac-cvs-datastore
GCP_SEARCH_APP_ID=sistac-search-app
GOOGLE_APPLICATION_CREDENTIALS=...  # Ruta absoluta al archivo json de cuenta de servicio
```

---

## Primeros pasos — configuracion inicial desde cero

Seguir estos pasos en orden la primera vez que se clona el repositorio.

### 1. Requisitos previos

- Python 3.10 o superior
- Git (con acceso al repo en Azure DevOps)
- Credenciales de: Anthropic, Google AI Studio, Azure AI Search

Verificar version de Python:
```bash
python --version   # debe ser >= 3.10
```

### 2. Clonar el repositorio

```bash
git clone https://marioagustinbelvisi204@dev.azure.com/marioagustinbelvisi204/sistac/_git/sistac
```

El repo se descarga en una carpeta llamada `sistac`. Entrar a ella:

```bash
cd sistac
```

> Si ya tenes el repo descargado (carpeta `clo-author` u otro nombre), simplemente
> entrar a esa carpeta antes de continuar:
> ```
> cd clo-author
> ```
> Todos los comandos del README se ejecutan desde la raiz del repositorio.

### 3. Crear entorno virtual (recomendado)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac / Linux
source .venv/bin/activate
```

### 4. Instalar dependencias Python

```bash
pip install -r scripts/python/requirements.txt
```

> La instalacion puede tardar 3-5 minutos por la descarga de `sentence-transformers`
> y sus modelos de PyTorch.

### 5. Instalar el modelo de spaCy en espanol

Requerido para el modulo de anonimizacion PII (H3):

```bash
python -m spacy download es_core_news_lg
```

### 6. Configurar variables de entorno

```bash
# Copiar la plantilla
copy .env.example .env        # Windows
cp .env.example .env          # Mac / Linux
```

Abrir `.env` y completar los valores:

```
ANTHROPIC_API_KEY=sk-ant-api03-...     # https://console.anthropic.com
GOOGLE_API_KEY=AIza...                 # https://aistudio.google.com (gratis)
AZURE_SEARCH_ENDPOINT=https://...      # Portal Azure → tu servicio de busqueda
AZURE_SEARCH_KEY=...                   # Portal Azure → Claves de acceso
AZURE_SEARCH_INDEX=sistac-cvs
LLM_PROVIDER=anthropic
```

### 7. Verificar que todo funciona

```bash
# Test del modulo PII (debe mostrar 10/10 PASSED)
pytest scripts/python/pii/test_anonymization.py -v

# Verificar configuracion y rutas
python -c "from scripts.python.config import PROJECT_ROOT, SCORE_THRESHOLD; print('OK — ROOT:', PROJECT_ROOT)"
```

---

## Levantar la aplicacion web (opcional)

Si queres usar la interfaz web para evaluar CVs manualmente:

```bash
py -3 -m uvicorn app.main:app --reload --port 8000
```

Abrir en el navegador: [http://localhost:8000](http://localhost:8000)

La app permite:
- Subir la descripcion de cargo (DOCX/PDF) → indexa en Azure Search
- Subir CVs de candidatos (PDF/DOCX/imagen) → devuelve score, decision y justificacion
- Evaluacion por lotes de hasta 50 CVs con ranking

---

## Instalacion rapida (resumen de comandos)

```bash
git clone https://marioagustinbelvisi204@dev.azure.com/marioagustinbelvisi204/sistac/_git/sistac
cd sistac
python -m venv .venv && .venv\Scripts\activate
pip install -r scripts/python/requirements.txt
python -m spacy download es_core_news_lg
copy .env.example .env        # completar con las API keys
pytest scripts/python/pii/test_anonymization.py -v
```

---

## Control de versiones

- **Repositorio:** Azure DevOps — `https://dev.azure.com/marioagustinbelvisi204/sistac/_git/sistac`
- **Rama activa:** `desarrollo` (todo el trabajo nuevo va aqui)
- **Rama estable:** `main` (solo recibe PR al cerrar hitos)
- **Datos:** `data/raw/` y `data/cleaned/` estan en `.gitignore` (proxies de datos personales)
