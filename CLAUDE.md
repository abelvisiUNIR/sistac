# CLAUDE.MD -- SISTAC: Sistema Inteligente de Selección de Talento y Análisis Curricular

<!-- Keep this file under ~150 lines — Claude loads it every session. -->

**Project:** SISTAC — Sistema Inteligente de Selección de Talento y Análisis Curricular
**Institution:** UNIR — Universidad Internacional de La Rioja
**Field:** Inteligencia Artificial, NLP y Ética Algorítmica
**Branch activa:** `desarrollo` (todo el trabajo nuevo va aquí → PR a `main` al cerrar hitos)

---

## Project-Specific Context

**Tipo:** TFE Grupal — Máster en Inteligencia Artificial y Data Science
**Tutora:** Marta María Arguedas Lafuente
**Entrega:** 15 julio 2026 | Mínimo: 75 páginas
**Formato del documento:** Microsoft Word (.docx) — plantilla UNIR

**Equipo y Autoría:**
- **David I. Madrid Oyanadel** — Lead Engineer H2: Pipeline RAG y motor de scoring semántico (Cap. 5 parcial)
- **Mario A. Belvisi Lescano** — Lead Analyst H3: Módulo anonimización PII y análisis de equidad algorítmica (Cap. 5 parcial)
- **Ambos (Joint Ownership):** H1 (marco de validación experimental, Cap. 6) y Capítulos 1-4, 7-9

**Pregunta de Investigación:**
¿Cuál es el efecto diferencial de cuatro configuraciones C0-C3 — C0: screening manual, C1: LLM puro, C2: LLM+RAG, C3: LLM+RAG+PII anonimización — sobre eficacia (F1, AUC-ROC), eficiencia (tiempo/candidato) y equidad (DIR, SPD), evaluadas contra un Gold Standard de expertos RRHH?

**Hipótesis:**
- **H1 (Eficiencia — Ambos):** El sistema LLM es significativamente más rápido que el screening manual
- **H2 (Eficacia — David):** Las configuraciones RAG alcanzan F1 ≥ 0.85 frente al Gold Standard de expertos
- **H3 (Equidad — Mario):** La anonimización PII reduce significativamente DIR y SPD respecto a C1 y C2

---

## Framework Rule Overrides

- **Formato:** Documento Word (.docx) — NO LaTeX. Fuente de verdad: `paper/SISTAC_TFE.docx`
- **Language:** Idioma primario **ESPAÑOL**. Términos técnicos en inglés son aceptables.
- **Bibliografía:** Formato APA 7ª edición. Gestionar con Mendeley o Zotero. Referencia base: `Bibliography_base.bib`
- **Stack tecnológico:** Lenguaje primario **PYTHON** (no R). `scripts/python/` es el directorio activo.
- **scikit-learn:** Permitido ÚNICAMENTE para métricas de clasificación (F1, AUC-ROC) — no para inferencia causal.
- **Tablas:** Diseñadas en Excel → insertadas manualmente en `SISTAC_TFE.docx`. Scripts Python exportan datos como `.csv` para alimentar las tablas.
- **Figuras:** Diseñadas manualmente (Cap. 1-4 existentes) o generadas por scripts Python como `.png` → insertadas en Word. Desde Cap. 4 en adelante: diseño manual con herramienta gráfica.
- **INV-5/INV-6:** No aplican (tesis Word, no artículo LaTeX). Usar resumen bilingüe ES+EN.
- **Quality scoring:** Señal de calidad interna. No es gate de entrega de tesis.

---

## Core Principles

- **Plan first** -- entrar en plan mode antes de tareas no triviales; guardar planes en `quality_reports/plans/`
- **Verify after** -- abrir el .docx y confirmar formato al final de cada tarea
- **Single source of truth** -- `paper/SISTAC_TFE.docx` es autoritativo
- **Worker-critic pairs** -- cada creador tiene un crítico pareado; los críticos nunca editan archivos
- **Auto-memory** -- correcciones y preferencias se guardan automáticamente via Claude Code memory

---

## Folder Structure

```
sistac/
├── CLAUDE.md                    # Este archivo
├── MEMORY.md                    # Decisiones aprendidas entre sesiones
├── .env.example                 # Template de variables de entorno
├── Bibliography_base.bib        # Referencias APA 7 (exportar a Mendeley/Zotero)
├── .claude/                     # Reglas, skills, agentes, hooks
│   ├── agents/                  # writer, coder, strategist, etc.
│   ├── rules/                   # invariantes, workflow, calidad
│   ├── skills/                  # /write, /analyze, /discover, etc.
│   ├── references/              # domain-profile, coding-standards-python
│   └── hooks/                   # pre-compact, post-compact-restore
├── paper/
│   ├── SISTAC_TFE.docx          # Documento principal — FUENTE DE VERDAD
│   ├── figures/                 # Figuras .png generadas por scripts
│   └── tables/                  # Tablas .csv exportadas por scripts
├── data/
│   ├── raw/                     # CVs sintéticos (PrivBayes) — gitignoreados
│   └── cleaned/                 # Datasets procesados — gitignoreados
├── scripts/python/
│   ├── config.py                # Rutas y configuración global
│   ├── requirements.txt         # Dependencias
│   ├── pii/                     # Módulo PII — SistacAnonymizer (Mario, H3) ✅
│   ├── rag/                     # Pipeline RAG (David, H2) 🔵
│   ├── scoring/                 # Scorer LLM
│   ├── evaluation/              # Métricas H1/H2/H3 ✅
│   ├── experiments/             # Orquestador C0-C3
│   ├── data/                    # Generación corpus sintético
│   └── utils/                   # docx_extractor, logger
├── explorations/                # Sandbox de investigación
├── quality_reports/             # Planes y logs de sesión
└── templates/                   # Plantillas de sesión y calidad
```

---

## Commands

```bash
# Instalar dependencias del proyecto
pip install -r scripts/python/requirements.txt
python -m spacy download es_core_news_lg

# Tests módulo PII (H3)
pytest scripts/python/pii/test_anonymization.py -v

# Demo de anonimización
python -m pii.anonymizer   # desde scripts/python/

# Ejecutar experimentos (cuando estén implementados)
python scripts/python/experiments/orquestador_c0_c3.py

# Extraer texto de .docx fuente
python scripts/python/utils/docx_extractor.py
```

---

## Quality Thresholds

| Score | Gate | Applies To |
|-------|------|------------|
| 80 | Commit en `desarrollo` | Bloqueante |
| 90 | PR `desarrollo` → `main` | Bloqueante |
| 95 | Entrega UNIR | Todos los componentes ≥ 80 |

---

## Skills Quick Reference

| Comando | Qué hace |
|---------|---------|
| `/discover [mode] [topic]` | Discovery: entrevista, literatura, datos |
| `/strategize [question]` | Estrategia experimental o plan de pre-análisis |
| `/analyze [dataset]` | Análisis de datos end-to-end |
| `/write [section]` | Redactar secciones del TFE (salida en texto para insertar en Word) |
| `/review [file/--flag]` | Revisiones de calidad del documento |
| `/revise [report]` | Ciclo de revisión con tutora |
| `/tools [subcommand]` | Utilidades: commit, validate-bib, journal |

---

## Output Organization

Output organization: by-script

---

## Current Project State

| Component | File | Status |
|-----------|------|--------|
| Cap. 1-4 | `paper/SISTAC_TFE.docx` | ✅ Escritos (David + Mario) |
| Cap. 5 — Pipeline RAG + PII | `paper/SISTAC_TFE.docx` | 🔵 En redacción (estructura definida) |
| Cap. 6 — Validación experimental | `paper/SISTAC_TFE.docx` | 🔵 En redacción (estructura definida) |
| Cap. 7-9 — Resultados, Discusión, Conclusiones | `paper/SISTAC_TFE.docx` | ⬜ Post-experimento |
| Dataset sintético | `data/raw/` | ⬜ No iniciado (PrivBayes + LLM) |
| Pipeline RAG (David, H2) | `scripts/python/rag/` | ⬜ No iniciado |
| Módulo PII (Mario, H3) | `scripts/python/pii/` | ✅ Completo — 10/10 tests PASSED |
| Métricas H1/H2/H3 | `scripts/python/evaluation/` | ✅ Implementadas |
| Orquestador C0-C3 | `scripts/python/experiments/` | 🔵 Scaffolded (stubs) |
