# Project Memory — SISTAC

Corrections and learned facts that persist across sessions.
Append `[LEARN:category]` entries below. Most recent at bottom.
**Mantener bajo ~150 líneas.**

---

## Workflow del proyecto

[LEARN:workflow] Plan-first para tareas no triviales (>1 hora o >3 archivos). Spec-then-plan: AskUserQuestion (máx 5 preguntas) → spec en `quality_reports/specs/` con MUST/SHOULD/MAY → aprobación → plan → implementar.

[LEARN:workflow] Antes de compresión: (1) actualizar MEMORY.md, (2) session log al día, (3) plan activo en disco, (4) preguntas abiertas documentadas.

[LEARN:workflow] Capítulo 5 del TFE se inserta via `scripts/python/figures/insert_cap5_docx.py` (script de inserción con restauración desde backup). Siempre restaurar backup antes de correr el script.

---

## SISTAC — Stack técnico

[LEARN:stack] Stack activo: Python + LangChain + Azure AI Search + spaCy + Presidio + sentence-transformers + scikit-learn (solo métricas clasificación) + python-docx. NO R, Julia, LaTeX. Documento principal: `paper/SISTAC_TFE.docx` (Word, fuente de verdad).

[LEARN:stack] Extracción de texto en `utils/doc_extractor.py`: pdfplumber para PDF nativo (gratis); Gemini 2.5 Flash para PDF escaneado e imágenes. Necesita `GOOGLE_API_KEY` en .env para imágenes/PDFs escaneados.

[LEARN:stack] Embeddings: `paraphrase-multilingual-mpnet-base-v2` (sentence-transformers, 768 dims, local). Singleton `_ST_MODEL` en `llm/provider.py` — se carga UNA sola vez por proceso. `HF_TOKEN` en .env evita warning de unauthenticated requests y rate limiting de HuggingFace.

---

## SISTAC — LLM y modelos

[LEARN:llm] Anthropic cambió la convención de nombres en modelos 2025+: usar `claude-haiku-4-5`, `claude-sonnet-4-5`, `claude-opus-4-5` (sin fecha, sin "3-5"). Los nombres estilo `claude-3-5-haiku-20241022` retornan 404. Actualizado en `provider.py` y `config.py`.

[LEARN:llm] Proveedor activo: Anthropic (LLM_PROVIDER=anthropic en .env). Embeddings: sentence-transformers local (no API externa). `provider.py` detecta automáticamente el proveedor y usa el backend correcto.

---

## SISTAC — Azure AI Search

[LEARN:azure] Free tier (50 MB) fue superado: 206/240 CVs indexados = 51.11 MB (45.63 MB vector + 5.48 MB otros). Tier Free no soporta Semantic Search (`queryType: semantic`). Upgrade a Basic tier recomendado (~$73/mes, 2 GB). Usuario confirmó intención de crear Basic tier.

[LEARN:azure] `index_corpus.py` tiene flags `--split {train,test,all}` (default: all) y `--resume` (salta CVs ya indexados via paginación `$select=cv_id&$top=1000&$skip=N`). Ejecutar siempre desde `clo-author/`: `py -3 scripts/python/rag/index_corpus.py --split train`.

[LEARN:azure] Al crear nuevo servicio Basic tier: actualizar `AZURE_SEARCH_ENDPOINT` y `AZURE_SEARCH_KEY` en `.env`, recrear el índice (`rag/create_index.py`) y re-indexar los 240 CVs de train.

---

## SISTAC — Web app (`app/`)

[LEARN:webapp] El "Failed to Fetch" en la app web se produce cuando código bloqueante (SistacRAGPipeline, SentenceTransformer, requests a Azure) corre directamente en función `async def`. Solución: envolver TODO en `run_in_threadpool()` de Starlette. Implementado en ambos endpoints (`/api/evaluar` y `/api/evaluar/batch`).

[LEARN:webapp] Startup correcto: desde `clo-author/` ejecutar `py -3 -m uvicorn app.main:app --reload --port 8000 --timeout-keep-alive 300`. También disponible `app/run.bat` (doble clic desde el Explorador). NO correr desde `clo-author/app/`.

[LEARN:webapp] Endpoint diagnóstico: `GET /api/diagnostico` reporta estado de API keys, dependencias instaladas y si C1/C2/C3 están listos. Usar antes de evaluar CVs para detectar problemas.

[LEARN:webapp] SistacRAGPipeline se instancia UNA sola vez por request batch (fuera del for loop) y se reutiliza para todos los CVs del lote. Tanto la instanciación como evaluate() van dentro de run_in_threadpool.

---

## SISTAC — Estado del documento

[LEARN:doc] Capítulos 1-4 escritos (David + Mario). Cap. 5 en redacción: 9 secciones H2, 6 figuras insertadas. Cap. 6 en redacción (estructura definida). Caps. 7-9 post-experimento.

[LEARN:doc] Sección 5.2 tiene 6 subsecciones: 5.2.1 Kaggle Resume Dataset (referencia estadística para calibrar generador sintético — CVs en inglés, NO usar directamente), 5.2.2 Gold Standard híbrido (algorítmico threshold=60 + validación experto RRHH Matriz, Cohen's κ≥0.70 en muestra 30-50 CVs), 5.2.3 JDs reales de Matriz Uruguay (5 JDs reales, NO adaptadas de portales), 5.2.4-6 extracción/chunking/split.

[LEARN:doc] Backups del .docx en `paper/backups/` con fecha en el nombre. Siempre crear backup antes de edición estructural (INV-W1).

---

## SISTAC — VCS y entorno

[LEARN:vcs] Control de versiones: Azure DevOps. Remote: `https://marioagustinbelvisi204@dev.azure.com/marioagustinbelvisi204/sistac/_git/sistac`. Branch activa: `desarrollo`. Merge a `main` solo al cerrar hitos.

[LEARN:vcs] Usuario corre Python 3.14 (del nombre `cpython-314.pyc` en __pycache__). Algunos paquetes pesados (ragas, sdv) pueden tener incompatibilidades. Reportar si hay errores de importación.

[LEARN:vcs] `.env` debe tener: `ANTHROPIC_API_KEY`, `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_KEY`, `AZURE_SEARCH_INDEX=sistac-cvs`, `LLM_PROVIDER=anthropic`, `HF_TOKEN` (opcional, evita warnings HuggingFace), `GOOGLE_API_KEY` (opcional, para PDF escaneados e imágenes).

---

## SISTAC — Módulo PII (H3)

[LEARN:pii] Módulo PII completo: `scripts/python/pii/`. 10/10 tests PASSED (`pytest scripts/python/pii/test_anonymization.py -v`). SistacAnonymizer implementado y funcional.

---

## SISTAC — Decisiones de infraestructura (Cap. 5)

[LEARN:infra] Vector store: Azure AI Search (Semantic Ranker nativo reemplaza cross-encoder). Embeddings: `paraphrase-multilingual-mpnet-base-v2` cuando LLM_PROVIDER=anthropic; `text-embedding-3-small` (OpenAI) cuando LLM_PROVIDER=openai. Score threshold unificado: 70 (calibrado con piloto C2, 5 CVs). Piloto David en `rag/` conservado como referencia.

[LEARN:infra] RAGAS configurado con Claude Haiku como LLM juez (via LangchainLLMWrapper / ChatAnthropic). Si falla: fallback a métricas proxy (ROUGE-L para faithfulness, coseno para context precision).
