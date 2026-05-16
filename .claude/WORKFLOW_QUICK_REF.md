# Workflow Quick Reference — SISTAC TFE

**Proyecto:** SISTAC | **Institución:** UNIR | **Entrega:** 15 julio 2026

---

## Pipeline del TFE

```
/discover lit [tema]      → Revisión bibliográfica (Librarian + librarian-critic)
    ↓
/strategize [h1|h2|h3]   → Plan de análisis experimental (H1/H2/H3 + corpus)
    ↓
/analyze [--c0..c3|--h1..h3]  → Pipeline Python: scripts, outputs, code review (Coder + coder-critic)
    ↓
/write [sección]          → Redactar capítulo en español (Writer + writer-critic)
    ↓
/review [--doc|--code]    → Revisión de calidad con score (writer-critic / coder-critic + Verifier)
    ↓
/revise [reporte]         → Ciclo de corrección con tutora
```

Podés entrar en cualquier etapa. Para tareas puntuales, invocá el skill directamente.

---

## Los 7 comandos activos

| Comando | Qué hace |
|---------|---------|
| `/discover [lit\|data\|interview]` | Búsqueda bibliográfica, exploración de datos, entrevista de diseño |
| `/strategize [h1\|h2\|h3\|corpus\|full]` | Plan de análisis experimental C0-C3, métricas y criterios de éxito |
| `/analyze [--c0..c3\|--h1..h3\|--metrics\|--debug]` | Pipeline Python: scripts, métricas H1/H2/H3, code review |
| `/write [sección]` | Redactar secciones del TFE en español (output texto plano para Word) |
| `/review [--doc\|--code\|--verify\|--tutora]` | Revisión de calidad del documento o código + score 0-100 |
| `/revise [reporte]` | Procesar comentarios de la tutora, clasificar y rutear correcciones |
| `/tools [subcomando]` | commit, validate-bib, lint, journal, context, learn |

---

## Gates de calidad

| Score | Gate | Significado |
|-------|------|-------------|
| ≥ 95 | Entrega UNIR | Listo para entregar (todos los componentes ≥ 80) |
| ≥ 90 | PR `desarrollo` → `main` | Listo para merge |
| ≥ 80 | Commit en `desarrollo` | Listo para commit |
| < 80 | **Bloqueado** | Corregir issues críticos/mayores antes de continuar |

**Ponderación:** Literatura 10% + Datos 10% + Diseño experimental 25% + Código 15% + Documento 25% + Pulido 10% + Replicación 5%

---

## Estado del proyecto

| Componente | Archivo | Estado |
|------------|---------|--------|
| TFE (Cap. 1-4) | `paper/SISTAC_TFE.docx` | ✅ Escritos |
| TFE (Cap. 5-9) | `paper/SISTAC_TFE.docx` | 🟡 Por redactar |
| Corpus piloto (5 CVs) | `data/raw/cvs/` | 🟡 Piloto (David) |
| Pipeline RAG C2 | `scripts/python/rag/` | 🟡 Piloto funcional (David) |
| Módulo PII (Mario, H3) | `scripts/python/pii/anonymizer.py` | ✅ Completo (10/10 tests) |
| Abstracción LLM | `scripts/python/llm/provider.py` | ⬜ Pendiente |
| Métricas H1/H2/H3 | `scripts/python/evaluation/` | ✅ Implementadas |
| Experimento C0-C3 | `scripts/python/experiments/orquestador_c0_c3.py` | 🟡 Stub |

---

## Cuándo pido confirmación

- **Decisión de diseño:** "OpenAI vs Anthropic para el scorer — ¿cuál elegís?"
- **Desacuerdo con tutora:** "Comentario clasificado DESACUERDO — revisá vos"
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
| `Bibliography_base.bib` | Base bibliográfica APA 7 |

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

# Piloto RAG C2 (David)
cd scripts/python && python rag/evaluate_pilot_c2.py
```

---

**Próximos pasos:** crear `llm/provider.py` (abstracción LLM) → ampliar corpus → `/analyze --c2` con corpus completo → `/write cap5`
