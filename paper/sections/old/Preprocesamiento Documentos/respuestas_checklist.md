# Respuestas a los ítems del checklist | 23/06/2026

Resoluciones concretas para cuatro ítems del `SISTAC_plan_aplicacion.md`.

---

## 1. Título único

Hoy conviven dos títulos:
- Portada y cuerpo: **"Selección de Talento Automatizada y Equitativa: Un Enfoque basado en LLMs y Recuperación Aumentada"**
- Archivo y repositorio: "Optimización del Proceso de Selección de Talento" (grupo 4 ESIT)

**Decisión recomendada:** adoptar el de la portada como **título canónico** y replicarlo en los cuatro lugares. Es el más preciso y el que ya aparece en el documento.

Título canónico (copiar tal cual):

> **Selección de Talento Automatizada y Equitativa: un enfoque basado en LLMs y Recuperación Aumentada**

Aplicar en:
- **Portada** del `.docx` (ya está).
- **Encabezado/pie** si el documento repite el título.
- **Nombre del archivo**: renombrar a `SISTAC_TFE_Seleccion_Talento_Automatizada_Equitativa.docx` (o similar), retirando "Optimizacion… grupo 4 ESIT".
- **Repositorio**: el repo puede conservar el nombre corto `sistac`, pero el README debe abrir con el título canónico.

> Observación (opcional, requiere visto bueno de la tutora): la palabra **"Equitativa"** en el título puede leerse como una promesa que los resultados no cumplen (la hipótesis de equidad se rechazó). Si quieren alinear el título con los hallazgos, una alternativa más neutra sería: *"Preselección curricular con LLMs y Recuperación Aumentada: un estudio sobre eficiencia, eficacia y equidad algorítmica"*. No es obligatorio; solo lo señalo por honestidad con el resultado.

---

## 2. Etiquetas H1 / H2 / H3 en prosa

**Decisión recomendada:** retirar las etiquetas literales "H1/H2/H3" de la prosa y los títulos, y nombrar cada hipótesis por su dimensión (eficiencia, eficacia, equidad). Se mantienen, si se desea, solo dentro de las figuras/tablas como sigla entre paréntesis una sola vez. Buscar y reemplazar (Cap 5 y Cap 6):

| Buscar | Reemplazar por |
|---|---|
| `Resultados de H1: eficiencia` | `Resultados de eficiencia` |
| `Resultados de H2: eficacia técnica` | `Resultados de eficacia técnica` |
| `Resultados de H3: equidad algorítmica` | `Resultados de equidad algorítmica` |
| `Hipótesis 1 sobre eficiencia` | `Hipótesis sobre la eficiencia` |
| `Hipótesis 2 sobre eficacia técnica` | `Hipótesis sobre la eficacia técnica` |
| `Hipótesis 3 sobre equidad algorítmica` | `Hipótesis sobre la equidad algorítmica` |
| `Discusión de H1: reducción del tiempo de preselección (Eficiencia)` | `Discusión de la eficiencia: reducción del tiempo de preselección` |
| `Discusión de H2: alcance del umbral de eficacia técnica (Eficacia)` | `Discusión de la eficacia técnica: alcance del umbral` |
| `Discusión de H3: efecto de la anonimización sobre los sesgos (Equidad)` | `Discusión de la equidad: efecto de la anonimización sobre los sesgos` |
| `H1 — Eficiencia.` | `Eficiencia.` |
| `H2 — Eficacia técnica.` | `Eficacia técnica.` |
| `H3 — Equidad algorítmica.` | `Equidad algorítmica.` |
| `Hipótesis H1 (Eficiencia): Se acepta` | `Hipótesis de eficiencia: se acepta` |
| `Hipótesis H2 (Eficacia): Se rechaza` | `Hipótesis de eficacia: se rechaza` |
| `Hipótesis H3 (Equidad): Se rechaza` | `Hipótesis de equidad: se rechaza` |
| `rechaza formalmente la hipótesis nula de H1` | `rechaza formalmente la hipótesis nula de eficiencia` |
| `la generalización de la hipótesis H1` | `la generalización de la hipótesis de eficiencia` |
| `para la aceptación de la hipótesis H2` | `para la aceptación de la hipótesis de eficacia` |
| `Los resultados de la hipótesis H3 sobre la mitigación` | `Los resultados sobre la mitigación` |
| `las tres hipótesis de eficiencia (H1), eficacia técnica (H2) y equidad algorítmica (H3)` | `las tres hipótesis de eficiencia, eficacia técnica y equidad algorítmica` |

En los **títulos de tabla** quitar la sigla final: `Tabla 10. Métricas de eficiencia por configuración (H1).` → `Tabla 10. Métricas de eficiencia por configuración.` (ídem Tabla 11 `(H2)`, Tablas 13 y 14 `(H3)`). En la **nota** de la Tabla 11: `Umbral de aceptación de H2:` → `Umbral de aceptación de la hipótesis de eficacia:`.

> Si prefieren conservar las siglas (es defendible como convención propia), basta con **unificar el formato** a uno solo, por ejemplo "(H1)" entre paréntesis, y evitar la variante con guion largo "H1 — …".

---

## 3. Anexo A — Tabla módulo → archivo (rutas reales del repo)

Insertar como Anexo A, después del enlace al repositorio. Rutas verificadas en `scripts/python/`.

| Componente funcional | Archivo(s) en el repositorio |
|---|---|
| Configuración global (rutas, umbral, semilla) | `config.py` |
| Extracción de texto (PDF/DOCX/OCR) | `utils/doc_extractor.py` |
| Generación del corpus sintético de desarrollo | `data/synthetic_corpus_generator.py` |
| Preparación del corpus de evaluación (Hugging Face) | `data/prepare_external_validation.py` |
| División entrenamiento/test | `data/split_corpus.py` |
| Segmentación en fragmentos (chunking) | `rag/chunking.py` |
| Generación de embeddings | `rag/embedding_generator.py` |
| Indexación en el almacén vectorial | `rag/index_corpus.py`, `rag/create_index.py` |
| Pipeline RAG (retrieval + orquestación) | `rag/pipeline.py` |
| Evaluación técnica del pipeline (RAGAS) | `rag/ragas_eval.py` |
| Motor de scoring semántico | `scoring/scorer.py` |
| Proveedor de modelos de lenguaje (Claude/Gemini) | `llm/provider.py` |
| Anonimización PII (SistacAnonymizer) | `pii/anonymizer.py`, `pii/recognizers.py` |
| Métricas de eficiencia (H eficiencia) | `evaluation/efficiency_metrics.py` |
| Métricas de eficacia (F₁, AUC-ROC) | `evaluation/efficacy_metrics.py` |
| Métricas de equidad (DIR, SPD) | `evaluation/fairness_metrics.py` |
| Orquestador del experimento C0–C3 | `experiments/orquestador_c0_c3.py` |
| Consolidación comparativa entre modelos | `evaluation/consolidate_comparison.py` |
| Generación de figuras de resultados | `figures/gen_cap5_figures.py`, `figures/gen_cap6_figures.py` |
| Persistencia en base de datos | `data/mongo_transfer.py`, `data/seed_mongodb.py` |

Pie sugerido: *Tabla A1. Correspondencia entre los módulos funcionales del sistema y los archivos del repositorio. Fuente: elaboración propia.*

---

## 4. Separador decimal — qué unificar y dónde

**Diagnóstico exacto:** la coma decimal aparece en **solo 8 párrafos** (todos en Cap 2 y Cap 3). El punto decimal aparece en ~120 párrafos (todo el Cap 5 y Cap 6) y en **todas** las tablas, figuras y CSVs, que se generan por código.

**Decisión recomendada: unificar a PUNTO decimal.** Razón práctica: cambiar 8 párrafos es trivial; cambiar a coma obligaría a reescribir ~120 párrafos **y regenerar todas las tablas, figuras y CSVs** (riesgo alto antes de la entrega). El punto decimal es, además, consistente con el dato numérico ya presente en todo el aparato de resultados.

**Correcciones puntuales (los 8 párrafos a tocar):**

| Sección aprox. | Buscar | Reemplazar por |
|---|---|---|
| §2.1 | `0,716` · `0,910` | `0.716` · `0.910` |
| §2.2 | `87,73 %` · `0,716` · `0,757` · `0,824` · `0,866` · `0,910` · `15,85 %` | `87.73 %` · `0.716` · `0.757` · `0.824` · `0.866` · `0.910` · `15.85 %` |
| §2.2 | `0,24 %` · `0,28 %` | `0.24 %` · `0.28 %` |
| §2.5 | `85,1 %` · `DIR ≥ 0,8` | `85.1 %` · `DIR ≥ 0.8` |
| §2.8 | `0,910` | `0.910` |
| §3.2 (OE2) | `recall@10 … 0,80` | `recall@10 … 0.80` |
| §3.2 (OE3) | `precisión y recall … ≥ 0,95` | `≥ 0.95` |
| §3.2 (OE4) | `κ de Cohen … ≥ 0,70` | `≥ 0.70` |

**Cuidado con el separador de miles.** Si el decimal pasa a punto, evitar el punto como separador de miles para que no haya ambigüedad. Usar **espacio** en las cuatro/cinco cifras: `50.000` → `50 000`, `270.000` → `270 000`, `28.000` → `28 000`, `1.730` → `1 730`, `1.116` → `1 116`, `1.000` → `1 000`. Estas cifras están en los mismos párrafos del Cap 2 (y en §5.3/§5.5 del Cap 5).

> Alternativa estricta (norma RAE = coma decimal): solo si están dispuestos a regenerar las tablas/figuras/CSVs con coma y a reescribir los ~120 párrafos del Cap 5–6. No se recomienda a esta altura del cronograma.
