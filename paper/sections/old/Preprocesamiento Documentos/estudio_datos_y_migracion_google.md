# Estudio de Datos Iniciales, Pipelines Experimentales y Migración a Google Cloud (Secciones Adicionales TFE)

Este documento contiene la redacción formal en tono académico (adecuado para un TFE de la UNIR) que detalla el estudio de los datos iniciales, los preprocesamientos, las transformaciones, los pipelines de cada experimento y la justificación del cambio de indexación de Azure a Google. Está diseñado para ser incorporado en los **Capítulos 5 y 6** de la memoria final sin sobrescribir las secciones ya existentes.

---

## 5.X. Estudio del Dataset de Validación Externa (Datos Iniciales)

Para garantizar la validez ecológica y dotar al proyecto de un escenario de contrastación real, se incorporó un dataset de validación externa compuesto por información real de postulaciones, currículums y descripciones de puestos. Este conjunto de datos complementa las pruebas del corpus sintético y permite auditar el comportamiento del sistema ante la variabilidad e imperfecciones del lenguaje humano real.

### 5.X.1. Origen y Características del Corpus Real
El dataset de validación externa se obtuvo mediante un subconjunto muestral de **150 pares de candidatos y cargos (CV-JD)** provenientes del dataset público **`netsol/resume-score-details`** (alojado en Hugging Face y Kaggle). Este dataset original contiene currículums de profesionales de diversas áreas del conocimiento emparejados con descripciones de vacantes técnicas y administrativas, evaluados históricamente respecto a su nivel de adecuación (etiquetado binario de selección e invitaciones a entrevista).

Para la conformación de la muestra de validación, se seleccionaron:
* **15 Descripciones de Puestos (JDs) únicas** correspondientes a roles de diversa índole (ej. Analista de Datos, Administradores, Desarrolladores de Software, etc.).
* **150 Currículums Vitae (CVs) individuales**, divididos de manera balanceada en **75 candidatos calificados como APTO** y **75 candidatos calificados como NO_APTO**.

### 5.X.2. Metodología de Traducción y Adaptación Cultural (Rioplatense)
Debido a que el dataset de origen se encontraba redactado en idioma inglés y el diseño experimental de SISTAC está calibrado para procesar lenguaje español, se requirió una fase de traducción y localización lingüística. En lugar de aplicar una traducción literal (que omitiría regionalismos y modismos típicos de las ofertas laborales locales), se diseñó un pipeline de traducción asistida por LLM con directrices de **adaptación cultural rioplatense (Uruguay/Argentina)**.

El prompt instruyó al modelo a adaptar terminología técnica y administrativa según el uso común en la región:
* **"High school diploma"** se adaptó como **"Secundario completo"**.
* **"Health insurance benefit"** se adaptó como **"Mutualista / Obra social"**.
* **"Independent contractor"** se adaptó como **"Monotributista / Facturación de servicios"**.
* **"Bachelor's Degree"** se adaptó como **"Licenciatura o Ingeniería"** según la disciplina.

Este preprocesamiento preservó el nivel de densidad semántica y la estructura original del currículum, adaptando el vocabulario para que el motor de embeddings y el RAG operaran en igualdad de condiciones conceptuales respecto al corpus sintético original en español.

### 5.X.3. Imputación Metodológica de Variables y Datos Faltantes
Dado que los datasets de reclutamiento públicos omiten marcas de tiempo operativas y datos demográficos para proteger la confidencialidad de los postulantes, fue necesario realizar un proceso de **imputación paramétrica justificada por la literatura científica** para poder contrastar las hipótesis $H_1$ (Eficiencia) y $H_3$ (Equidad):

1. **Tiempos de Screening Manual ($T_{cand}$ para $C_0$):** Siguiendo las estimaciones empíricas reportadas en la literatura de adquisición de talento (donde se establece que un screening inicial exhaustivo toma entre 5 y 20 minutos por candidato), se imputaron los tiempos de la configuración de control manual utilizando distribuciones uniformes:
   * **Candidato Descartado (`NO_APTO`):** $T \sim U(300, 720)$ segundos (5 a 12 minutos).
   * **Candidato Preseleccionado (`APTO`):** $T \sim U(600, 1200)$ segundos (10 a 20 minutos).
2. **Género del Postulante (`group_gender`):** Se infirió el género de los candidatos a partir de la clasificación heurística del nombre de pila del currículum (etiquetados como `'M'` o `'F'`), balanceando la muestra final al 50% para evitar sesgos de selección previos en la distribución.
3. **Rango de Edad (`group_age`):** Se asignó a los candidatos una edad ficticia distribuida de manera uniforme en tres rangos de control: **23-35 años**, **36-45 años** y **46-58 años**. Esta asignación ciega y balanceada es crítica para el cálculo de la razón de impacto dispar (DIR) y la diferencia de paridad estadística (SPD) de la hipótesis $H_3$.

Todos los documentos limpios, textos de CVs, descripciones de puestos, tiempos de control y etiquetas reales del Gold Standard fueron persistidos sistemáticamente en la base de datos documental local `sistac_tfe` de **MongoDB** para auditoría y linaje de los análisis estadísticos.

---

## 5.Y. Transformaciones Aplicadas y Feature Engineering

Previo a la ejecución de las corridas experimentales sobre las configuraciones automáticas, los datos sufrieron una serie de transformaciones técnicas:

```
                                PIPELINE DE TRANSFORMACIÓN DE DATOS
 ┌──────────────┐      ┌──────────────┐      ┌───────────────┐      ┌──────────────┐
 │   CV + JD    │  ──> │   Chunking   │  ──> │ Vectorización │  ──> │  Seeding DB  │
 │  Texto Plano │      │ 512t (2048c) │      │ (768 dims)    │      │ Azure/Google │
 └──────────────┘      └──────────────┘      └───────────────┘      └──────────────┘
                                │ (Solo en C3)
                                v
                       ┌──────────────┐
                       │ Anonimización│
                       │ PII (Presidio│
                       └──────────────┘
```

1. **Fragmentación (Chunking) Controlada:** Se dividieron los documentos utilizando el separador recursivo `RecursiveCharacterTextSplitter`. Se fijó el tamaño de bloque a **512 tokens** con un solapamiento (*overlap*) de **64 tokens**.
   * *Resolución de Anomalía:* Se corrigió una discrepancia crítica en el SDK de LangChain, el cual por defecto mide en caracteres (`len()`). Al pasarle directamente el parámetro `chunk_size = 512`, fragmentaba los textos en bloques de 512 caracteres (~80 palabras), inflando artificialmente el número de chunks a 22 por CV. Esto aumentaba las llamadas al embedding y saturaba los límites de la API de Azure. Se ajustó el factor de escala para español ($1 \text{ token} \approx 4 \text{ caracteres}$), configurando la fragmentación a **2048 caracteres** (obteniendo un promedio saludable de 4 a 5 chunks por documento).
2. **Generación de Embeddings Densos:** Cada fragmento de texto se transformó en un vector numérico denso de **768 dimensiones** utilizando el modelo local `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`. Esta transformación permite realizar búsquedas semánticas sublineales.
3. **Enmascaramiento PII (Solo en $C_3$):** Para evaluar la equidad algorítmica y cumplir con las regulaciones de protección de datos (RGPD), los currículums de la configuración $C_3$ pasaron por un proceso de anonimización en el que se sustituyeron nombres de personas, documentos de identidad, números telefónicos, correos electrónicos y direcciones por marcadores genéricos (ej. `[TELEFONO]`), eliminando cualquier rastro de PII antes de poblar la base de datos vectorial.

---

## 5.Z. Flujo Técnico de cada Experimento (Pipelines C0 a C3)

El diseño metodológico de SISTAC evalúa comparativamente cuatro configuraciones experimentales ($C_0$, $C_1$, $C_2$, $C_3$) que representan la transición tecnológica desde el cribado clásico hasta el procesamiento RAG con privacidad integrada:

```
                            FLUJO COMPARATIVO DE LOS PIPELINES
   C0 (Manual):
   [CV Original] ──────────────────────────────────────────────> [Evaluador Humano] ──> [Decisión]

   C1 (LLM Puro):
   [CV Original] ───────────────> [Prompt Completo] ────────────> [Scorer LLM] ─────────> [Decisión]

   C2 (LLM + RAG):
   [CV Original] ──> [Embed] ───> [Azure/Google Search]
                                         │ (Top 5 Chunks)
                                         v
                                  [Prompt Contexto] ────────────> [Scorer LLM] ─────────> [Decisión]

   C3 (RAG + PII):
   [CV Original] ──> [PII Mask] ─> [GCP/Azure Search]
                                         │ (Top 5 Chunks Anón)
                                         v
                                  [Prompt Anónimo] ─────────────> [Scorer LLM] ─────────> [Decisión]
```

### 5.Z.1. Pipeline C0: Cribado Manual (Control)
* **Descripción:** El currículum completo en texto plano es evaluado por un analista de selección de personal humano. 
* **Lógica:** El reclutador lee el perfil y evalúa las dimensiones técnicas, formación y experiencia frente al cargo vacante. Mide la eficiencia real registrando la latencia mediante un cronómetro web.

### 5.Z.2. Pipeline C1: LLM Puro
* **Descripción:** Automatización directa sin base de datos vectorial.
* **Lógica:** Se envía al LLM (Claude o Gemini) el currículum completo en formato de texto plano estructurado junto con la descripción del cargo. El modelo realiza la inferencia sobre su ventana de contexto nativa y calcula la adecuación.

### 5.Z.3. Pipeline C2: LLM + RAG (Búsqueda Vectorial Híbrida)
* **Descripción:** Recuperación semántica de fragmentos de currículums.
* **Lógica:** El cargo vacante se codifica vectorialmente. Se realiza una búsqueda híbrida (vectorial +BM25) en el Vector Store para recuperar los **5 fragmentos (chunks) más relevantes** del currículum específico del postulante. Estos chunks son los únicos que se inyectan en el prompt del LLM juez junto con las directrices de puntuación, reduciendo el ruido lingüístico y optimizando el consumo de tokens de contexto.

### 5.Z.4. Pipeline C3: LLM + RAG + PII (Privacidad y Equidad)
* **Descripción:** Recuperación contextual sobre índice y datos anónimos.
* **Lógica:** Modifica a $C_2$ aplicando una capa de enmascaramiento lingüístico. El currículum se anonimiza primero. La búsqueda semántica y la inferencia del LLM se ejecutan sobre fragmentos y textos libres de datos personales e identificación demográfica. El modelo juzga al candidato únicamente en función de su mérito objetivo (experiencia, tecnologías y formación expresadas de forma anónima).

---

## 5.W. Dificultades Técnicas y Resiliencia del Framework

La puesta en marcha del experimento factorial enfrentó desafíos prácticos de infraestructura que requirieron el diseño de mecanismos de resiliencia en el código:

1. **Bloqueos de Archivos y Sincronización en Google Drive:**
   * *Desafío:* Al trabajar en un entorno local donde el código se almacena en Google Drive, Docker Compose y el motor de sincronización de Windows causaban bloqueos de escritura y lectura en los archivos montados (`bind mounts`).
   * *Solución:* Se encapsularon los datos transitorios en **volúmenes nombrados de Docker** administrados en memoria por el daemon de Docker, y se facilitó una ejecución nativa en el host mediante comandos directos de Python que eluden la capa de virtualización de WSL2.
2. **Saturación del Servicio Vectorial y Códigos de Error HTTP 429:**
   * *Desafío:* El cargador original generaba miles de peticiones secuenciales de embeddings hacia Azure AI Search. El nivel de servicio gratuito de Azure (Free Tier) bloqueaba el tráfico al superar los umbrales de velocidad y capacidad física (50 MB).
   * *Solución:* Se programó un bucle de reintento robusto en [pipeline.py](file:///c:/Users/abelvisi/Documents/Google_Drive/Mi%20unidad/M%C3%A1ster%20UNIR/IA%20Y%20Data/TFE/Entregas_TFE_Terminal/clo-author/scripts/python/rag/pipeline.py) con **Backoff Exponencial** y pausas obligatorias de $1.5$ segundos entre lotes de indexación. Esto estabilizó la ingesta y permitió completar la indexación del corpus de validación sin interrupciones.
3. **Caché de Evaluaciones para Costo Cero ($0 USD):**
   * *Desafío:* Ante un fallo de red o desconexión del LLM a mitad de una corrida masiva de 150 CVs, repetir las llamadas al modelo causaba costos duplicados y demoras.
   * *Solución:* Se implementó una base de datos de caché persistente en disco (`eval_cache.json`). Cada evaluación completada con éxito se guarda de inmediato. Al reiniciar el proceso, el sistema omite de forma idempotente las evaluaciones ya realizadas, garantizando un costo de $0 USD$ para reintentos y recuperaciones ante fallos.

---

## 5.K. Transición e Integración de Google Vertex AI Search

Para la fase de producción y despliegue comercial del diseño de SISTAC, se propuso la migración del motor de búsqueda vectorial desde **Azure AI Search** hacia **Google Cloud Vertex AI Search** (Discovery Engine).

### 5.K.1. Rationale del Cambio de Proveedor
* **Costo Operativo:** Azure AI Search exige la contratación del nivel *Basic* a un costo mínimo fijo de **$73 USD/mes** para poder habilitar configuraciones semánticas estructuradas e indexación sin límites estrictos de almacenamiento.
* **Flexibilidad de Google Cloud:** Vertex AI Search factura bajo un esquema elástico de pago por consulta y ofrece una integración natural con las APIs de Gemini (Google AI Studio) que se utilizan para el procesamiento por lotes de bajo costo en el backend de la aplicación.
* **Indexación Asíncrona Robusta:** A diferencia de Azure, donde el backend debe encargarse manualmente del chunking, codificación de embeddings locales y subida HTTP por lotes, Vertex AI Search se conecta directamente a un bucket de Google Cloud Storage (GCS) y gestiona la fragmentación y vectorización en la nube de forma asíncrona, liberando recursos de CPU en el servidor de la aplicación.

### 5.K.2. Diseño Técnico de la Migración
El framework de SISTAC fue refacturado en sus archivos base ([config.py](file:///c:/Users/abelvisi/Documents/Google_Drive/Mi%20unidad/M%C3%A1ster%20UNIR/IA%20Y%20Data/TFE/Entregas_TFE_Terminal/clo-author/scripts/python/config.py) y [pipeline.py](file:///c:/Users/abelvisi/Documents/Google_Drive/Mi%20unidad/M%C3%A1ster%20UNIR/IA%20Y%20Data/TFE/Entregas_TFE_Terminal/clo-author/scripts/python/rag/pipeline.py)) para soportar de forma configurable ambos proveedores mediante la variable `VECTORSTORE_PROVIDER`. 

Cuando se activa la opción de Google, el flujo de recuperación y consultas se ejecuta a través de la librería oficial de GCP `google-cloud-discoveryengine`:

```python
# Diseño conceptual del cliente de búsqueda Vertex AI Search en SISTAC
from google.cloud import discoveryengine_v1beta as discoveryengine

def buscar_chunks_gcp(cv_id, jd_id, query_text, top_k=5):
    client = discoveryengine.SearchServiceClient()
    serving_config = client.project_location_collection_data_store_serving_config_path(
        project="sistac-tfe-proyecto",
        location="global",
        collection="default_collection",
        data_store="sistac-search-app-id",
        serving_config="default_serving_config",
    )
    
    # Filtro demográfico y de linaje para evitar contaminación cruzada
    filter_str = f'cv_id: ANY("{cv_id}") AND jd_id: ANY("{jd_id}")'
    
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query_text,
        filter=filter_str,
        page_size=top_k,
    )
    
    response = client.search(request)
    return [result.document.derived_struct_data["chunk_text"] for result in response.results]
```

Esta modularidad técnica permite que el TFE demuestre la viabilidad de despliegue multiplataforma en nubes híbridas, mejorando significativamente el diseño arquitectónico de cara a la defensa del proyecto ante el tribunal académico.
