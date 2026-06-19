# Mapa del Repositorio y Estructura del Proyecto SISTAC

Este documento describe la estructura organizativa definitiva del repositorio del proyecto **SISTAC** para tu Trabajo de Fin de Estudios (TFE). Detalla el propósito de cada carpeta y la función exacta de cada script en los procesos de ingesta, anonimización, indexación, evaluación de hipótesis y visualización web.

---

## 1. Árbol de Directorios del Proyecto

```text
clo-author/
│
├── app/                                 # Aplicación FastAPI y Frontend Web
│   ├── main.py                          # Servidor API de FastAPI, endpoints de simulación y descarga
│   └── static/                          # Archivos estáticos de la interfaz web
│       ├── index.html                   # Dashboard principal e interfaz del simulador interactivo
│       └── index_.html                  # Resguardo histórico de la interfaz anterior
│
├── data/                                # Almacenamiento de datos del experimento
│   ├── raw/                             # Datos crudos cargados localmente
│   │   ├── cvs/                         # 300 currículums sintéticos generados en formato .txt (CV_001.txt a CV_300.txt)
│   │   ├── job_descriptions/            # 5 descripciones de cargos/vacantes en formato .txt (JD_001.txt a JD_005.txt)
│   │   └── gold_standard/               # Datos del experimento humano (C0) y etiquetas de control
│   │       ├── ground_truth.csv         # Tabla maestra de CVs-JDs con etiquetas deseadas y columna 'eval_source'
│   │       └── c0_times.csv             # Registro de tiempos reales invertidos por los evaluadores en el screening manual
│   └── cleaned/                         # Datos procesados y divisiones experimentales
│       └── evaluation_sets/             # Particiones de entrenamiento y prueba
│           ├── train_ids.csv            # IDs de los 240 CVs de entrenamiento (se indexan en Azure Search)
│           └── test_ids.csv             # IDs de los 60 CVs de prueba (reservados para evaluar C1, C2 y C3)
│
├── scripts/python/                      # Lógica principal del proyecto y scripts experimentales
│   ├── config.py                        # Parámetros generales, umbrales de hipótesis, claves y rutas del proyecto
│   ├── requirements.txt                 # Dependencias y paquetes de Python necesarios en Docker y local
│   │
│   ├── data/                            # Scripts de administración e ingesta de datos
│   │   ├── seed_mongodb.py              # Sembrador inicial de MongoDB (cargos, cvs, ground truth y tiempos C0)
│   │   ├── split_corpus.py              # Genera la división train/test estratificada basada en el ground truth
│   │   ├── synthetic_corpus_generator.py # Generador local de los 300 CVs sintéticos mediante LLM (Claude)
│   │   └── mongo_transfer.py            # Script auxiliar para transferencias de datos en la base de datos
│   │
│   ├── pii/                             # Módulo de anonimización para mitigación de sesgos (Pipeline C3)
│   │   ├── anonymizer.py                # Motor de reemplazo de PII integrado con Microsoft Presidio
│   │   ├── recognizers.py               # Reconocedores customizados de entidades en español rioplatense
│   │   ├── test_anonymization.py        # Pruebas unitarias de anonimización
│   │   └── conftest.py                  # Configuraciones locales de pruebas unitarias
│   │
│   ├── rag/                             # Infraestructura RAG y conexiones con Azure AI Search
│   │   ├── create_index.py              # Crea el índice vectorial 'sistac-cvs' con sus campos en Azure AI Search
│   │   ├── index_corpus.py              # Sube los chunks vectorizados de CVs y JDs a la nube de Azure
│   │   ├── pipeline.py                  # Coordina el flujo RAG: Retrieval (Azure Search) + Prompting + Generación
│   │   ├── ragas_eval.py                # Evaluación de calidad RAG con métricas RAGAS
│   │   ├── evaluate_pilot_c2.py         # Evaluación inicial del piloto experimental de 5 casos
│   │   └── search_test.py               # Script rápido de prueba de consultas en Azure Search
│   │
│   ├── scoring/                         # Criterios del calificador automático
│   │   └── scorer.py                    # Prompt estructurado y lógica de evaluación de afinidad CV vs JD
│   │
│   ├── evaluation/                      # Algoritmos estadísticos y métricas del TFE
│   │   ├── efficiency_metrics.py        # Calcula diferencias de tiempo H1 (prueba Mann-Whitney U, Speedup, mediana)
│   │   ├── efficacy_metrics.py          # Evalúa concordancia H2 vs Gold Standard (F1-score macro y AUC-ROC)
│   │   ├── fairness_metrics.py          # Analiza impacto dispar H3 (DIR y SPD para evitar sesgo de género/edad)
│   │   └── export_excel_report.py       # Compila el reporte consolidado multimétrico y las gráficas en Excel
│   │
│   ├── experiments/                     # Orquestación del experimento científico
│   │   └── orquestador_c0_c3.py         # Corre el experimento de forma masiva evaluando las configuraciones C0, C1, C2 y C3
│   │
│   ├── figures/                         # Scripts de generación visual para la tesis
│   │   ├── gen_cap5_figures.py          # Genera las figuras del capítulo 5 (diagramas de arquitectura)
│   │   ├── gen_cap6_figures.py          # Genera las figuras estadísticas del capítulo 6 (Boxplots, curvas ROC y DIR)
│   │   └── insert_cap5_docx.py          # Inserta automáticamente las figuras dentro del documento Word (.docx)
│   │
│   ├── utils/                           # Utilidades auxiliares
│   │   ├── doc_extractor.py             # Extractor genérico de textos (soportando TXT, PDF, DOCX e imágenes/OCR)
│   │   ├── docx_extractor.py            # Utilidad específica de lectura estructural de archivos Word
│   │   └── insert_google_migration_docx.py # Utilidad para insertar la sección de migración a Google en la memoria .docx
│   │
│   └── scratch/                         # Scripts temporales e instrumentales de administración
│       ├── cleanup_empty_folders.py     # Script para remover carpetas vacías/bloqueadas en local por Drive
│       └── update_gt_csv.py             # Añade de forma retroactiva el campo 'eval_source' al ground_truth.csv
│
├── paper/                               # Memoria oficial y artefactos de resultados del TFE
│   ├── SISTAC_TFE.docx                  # Documento principal Word de la tesis
│   ├── sections/                        # Redacción de secciones del paper en markdown
│   │   ├── contribuciones_y_diseno_sistac.md # Detalle metodológico del capítulo 5
│   │   └── framework_validacion_experimental.md # Resultados de las hipótesis del capítulo 6
│   ├── tables/                          # Reporte Excel unificado generado por el sistema
│   │   └── reporte_completo_sistac.xlsx # Reporte unificado que contiene las pestañas H1, H2, H3, RAGAS y Raw
│   └── figures/                         # Archivos PNG de gráficos a alta resolución (300 DPI) para la memoria
│       ├── cap5/                        # Diagramas del sistema
│       └── cap6/                        # Gráficos de resultados (ROC, Boxplot de tiempos, DIR)
│
├── guide/                               # Documentación interactiva del proyecto (Quarto)
│   ├── _quarto.yml                      # Configuración del sitio estático Quarto
│   ├── index.qmd                        # Página de inicio de la guía
│   ├── architecture.qmd                 # Explicación de la arquitectura RAG
│   ├── rag-pipeline.qmd                 # Flujo detallado de recuperación de información
│   └── user-guide.qmd                   # Manual de usuario paso a paso del dashboard
│
├── results/                             # Logs y salidas temporales de las ejecuciones locales
│
├── Dockerfile                           # Definición de contenedor Docker para levantar FastAPI
├── docker-compose.yml                   # Orquestación de contenedores (sistac-app y base de datos mongodb)
├── azure-pipelines.yml                  # Configuración del pipeline CI/CD en Azure DevOps
├── ESTRUCTURA_PROYECTO.md               # Este archivo (mapa de referencia del proyecto)
├── MEMORY.md                            # Resumen técnico de hitos de desarrollo para el agente
├── README.md                            # Guía de inicio rápido e instalación local
├── Bibliography_base.bib                # Base de datos bibliográfica de la tesis
├── CHANGELOG.md                         # Registro histórico de versiones y cambios del código
└── CLAUDE.md                            # Guía de comandos del proyecto para el asistente de desarrollo
```

---

## 2. Descripción de las Carpetas Principales

### 1. `app/` (Visualización e Interfaz Interactiva)
*   **Propósito:** Proporcionar un portal web interactivo para los evaluadores de reclutamiento y coordinadores del experimento.
*   **`main.py`:** Define el servidor web FastAPI. Contiene endpoints clave como `/api/cargo` (ingesta), `/api/evaluar` (evaluación), `/api/casos/simular-candidato` (creación de PII uruguayo), `/api/casos/guardar-decision` (guardado de decisiones manuales) y `/api/admin/descargar-tablas` (generador dinámico de Excel y empaquetador ZIP).
*   **`static/index.html`:** El panel de control. Utiliza HTML5 semántico, CSS personalizado (glassmorphism premium y animaciones), Javascript nativo y Chart.js para renderizar los resultados de eficiencia, eficacia y equidad directo del backend.

### 2. `data/` (El Dataset)
*   **Propósito:** Almacenar de forma segura el corpus y los registros del experimento.
*   **`raw/`:** Contiene los insumos crudos. El subdirectorio `gold_standard/` sirve como el punto de comparación humana (tiempo y decisión) contra los tres algoritmos automatizados (C1, C2, C3).
*   **`cleaned/`:** Contiene la división train/test del corpus sintético para evitar *data leakage* (los 60 CVs de test jamás son indexados y actúan como datos no vistos).

### 3. `scripts/python/` (Núcleo Lógico)
*   **Propósito:** Contener todo el código Python estructurado que da soporte científico a las tres hipótesis (H1, H2, H3) del TFE.
*   **`rag/`:** Interactúa con Azure AI Search y gestiona el indexado vectorial.
*   **`pii/`:** Implementa la anonimización activa para neutralizar variables demográficas que puedan causar sesgo algorítmico.
*   **`evaluation/`:** Módulo matemático y estadístico que calcula las hipótesis, guardando las salidas tabulares y estructurando el archivo Excel dinámico.

### 4. `paper/` (Resultados de la Memoria)
*   **Propósito:** Alojar el documento Word maestro de tu tesis académica (`SISTAC_TFE.docx`) y todos los insumos necesarios para la redacción de sus capítulos.
*   **`sections/`:** Contiene capítulos redactados en markdown como soporte y referencia bibliográfica rápida.
*   **`tables/` y `figures/`:** Carpetas de salida física para las tablas estadísticas y gráficos generados a alta calidad (300 DPI) para copiar directamente a la memoria de la tesis.

### 5. `guide/` (Manual Técnico)
*   **Propósito:** Proveer una documentación dinámica del proyecto en Quarto para directores y evaluadores del TFE, explicando diagramas UML y flujos de datos paso a paso.
