# Meta-Governance: SISTAC TFE

Este repositorio es el proyecto SISTAC — Trabajo Fin de Estudios del Máster en
Inteligencia Artificial y Data Science (UNIR). No es un template genérico.

## Propósito único

Desarrollar, versionar y documentar el sistema SISTAC que evalúa cuatro
configuraciones (C0-C3) de pre-selección de CVs con LLMs, midiendo eficacia
(H2), eficiencia (H1) y equidad algorítmica (H3).

## Qué va en el repo (Azure DevOps)

**SÍ versionar:**
- `scripts/python/` — todo el código (PII, RAG, scoring, evaluation, experiments)
- `paper/SISTAC_TFE.docx` — documento principal del TFE
- `paper/figures/` — figuras generadas por scripts (.png)
- `paper/tables/` — tablas exportadas por scripts (.csv)
- `Bibliography_base.bib` — referencias APA 7
- `.claude/` — configuración de agentes, reglas, skills
- `CLAUDE.md`, `MEMORY.md` — memoria del proyecto
- `data/` — estructura de carpetas solo (datos gitignoreados)

**NO versionar (gitignore):**
- `data/raw/*.csv`, `data/raw/*.jsonl` — CVs sintéticos (pueden contener proxies de datos personales)
- `data/cleaned/*.csv` — datasets procesados
- `data/vectorstore/`, `*.faiss`, `*.pkl` — índices vectoriales (regenerables)
- `.env` — API keys (solo `.env.example`)
- `master_supporting_docs/**/*.docx` — documentos fuente grandes (compartir por OneDrive)
- `guide/`, `paper/preambles/`, `paper/sections/` — carpetas heredadas del template, eliminadas

## Branches

| Branch | Uso |
|--------|-----|
| `desarrollo` | Todo el trabajo diario — commits frecuentes |
| `main` | Estable — solo recibe PR al cerrar hitos |

## Regla de commit

Antes de cada commit, verificar:
- El código corre sin errores (`python script.py`)
- Los tests pasan (`pytest pii/test_anonymization.py -v`)
- No hay rutas absolutas (usar `config.py`)
- No hay credenciales o datos personales en el diff
