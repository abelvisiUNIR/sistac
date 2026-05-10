# Workflow Quick Reference — SISTAC TFE

**Proyecto:** SISTAC | **Institución:** UNIR | **Entrega:** 15 julio 2026

---

## Pipeline del TFE

```
/discover lit [tema]      → Revisión bibliográfica (Librarian + librarian-critic)
    ↓
/strategize [pregunta]    → Estrategia experimental (Strategist + strategist-critic)
    ↓
/analyze [dataset]        → Pipeline Python: scripts, outputs, code review (Coder + coder-critic)
    ↓
/write [sección]          → Redactar capítulo en español (Writer + writer-critic)
    ↓
/review [archivo]         → Revisión de calidad con score (Writer-critic + Verifier)
    ↓
/revise [reporte]         → Ciclo de corrección con tutora
```

Podés entrar en cualquier etapa. Para tareas puntuales, invocá el skill directamente.

---

## Los 8 comandos activos

| Comando | Qué hace |
|---------|---------|
| `/discover [lit\|data\|interview]` | Búsqueda bibliográfica, exploración de datos, entrevista de descubrimiento |
| `/strategize [pregunta]` | Diseño del experimento factorial C0-C3, plan de análisis estadístico |
| `/analyze [dataset]` | Análisis end-to-end: scripts Python, métricas H1/H2/H3, code review |
| `/write [sección]` | Redactar secciones del TFE en español (output texto plano para Word) |
| `/review [archivo]` | Revisión de calidad del documento + score 0-100 |
| `/revise [reporte]` | Procesar comentarios de la tutora, clasificar y rutear correcciones |
| `/tools [subcomando]` | commit, validate-bib, learn, context |
| `/new-project [tema]` | Pipeline completo desde cero (solo para nueva investigación) |

### Comandos eliminados (no aplican a SISTAC)
`/talk`, `/submit [journal]` — Beamer y journals de economía eliminados del sistema.

---

## Gates de calidad

| Score | Gate | Significado |
|-------|------|-------------|
| ≥ 95 | Entrega UNIR | Listo para entregar (todos los componentes ≥ 80) |
| ≥ 90 | PR | Listo para merge / revisión de tutora |
| ≥ 80 | Commit | Listo para commit (corregir issues mayores antes de entrega) |
| < 80 | **Bloqueado** | Corregir issues críticos/mayores antes de continuar |

**Ponderación:** Literatura 10% + Datos 10% + Estrategia 25% + Código 15% + Documento 25% + Pulido 10% + Replicación 5%

---

## Estado del proyecto

| Componente | Archivo | Estado |
|------------|---------|--------|
| TFE (Cap. 1-4) | `paper/SISTAC_TFE.docx` | ✅ Escritos |
| TFE (Cap. 5-9) | `paper/SISTAC_TFE.docx` | 🟡 Por redactar |
| Dataset sintético | `data/raw/` | ⬜ No iniciado |
| Pipeline RAG (David, H2) | `scripts/python/rag/pipeline.py` | ⬜ No iniciado |
| Módulo PII (Mario, H3) | `scripts/python/pii/anonymizer.py` | ✅ Completo (10/10 tests) |
| Métricas H1/H2/H3 | `scripts/python/evaluation/` | ✅ Implementadas |
| Experimento C0-C3 | `scripts/python/experiments/orquestador_c0_c3.py` | 🟡 Stub |

---

## Cuándo pido confirmación

- **Decisión de diseño:** "FAISS vs. ChromaDB para el vector store — ¿cuál elegís?"
- **Desacuerdo con tutora:** "Comentario clasificado DISAGREE — revisá vos"
- **3 strikes:** "Coder y coder-critic no convergen — necesito tu criterio"
- **Borrar archivos:** siempre pido confirmación antes de eliminar

## Cuándo ejecuto directamente

- Bug obvio en código Python
- Verificación (validate-bib, tests pytest)
- Logs y commits de rutina
- Formato de tablas según `domain-profile.md`

---

## Archivos clave

| Archivo | Propósito |
|---------|-----------|
| `CLAUDE.md` | Contexto del proyecto (hipótesis, stack, estructura) |
| `MEMORY.md` | Decisiones aprendidas que persisten entre sesiones |
| `.claude/references/domain-profile.md` | Notación, métricas, umbrales, referencias seminales |
| `.claude/references/coding-standards-python.md` | Estándares de código Python para SISTAC |
| `paper/SISTAC_TFE.docx` | Fuente de verdad del TFE |
| `Bibliography_base.bib` | Base bibliográfica APA 7 (exportar a Mendeley/Zotero) |

---

## Comandos de uso frecuente

```bash
# Instalar dependencias
pip install -r scripts/python/requirements.txt
python -m spacy download es_core_news_lg

# Tests módulo PII
pytest scripts/python/pii/test_anonymization.py -v

# Demo anonimización (desde scripts/python/)
python -m pii.anonymizer

# Ejecutar experimentos
python scripts/python/experiments/orquestador_c0_c3.py

# Extraer texto de .docx fuente
python scripts/python/utils/docx_extractor.py
```

---

**Próximo paso:** `/analyze` cuando el corpus sintético esté listo → `/write cap5` → `/review`
