---
name: review
description: Revisiones de calidad de SISTAC — rutea al critic apropiado según el tipo de archivo. .docx o sección TFE → writer-critic + verifier. Archivo .py → coder-critic. Sin flags → revisión completa del documento Word.
argument-hint: "[archivo o sección] Opciones: --doc, --code [archivo.py], --verify, --tutora"
allowed-tools: Read,Grep,Glob,Write,Bash,Task
---

# Review

Revisiones de calidad de SISTAC. Rutea al critic correcto según el target.

**Input:** `$ARGUMENTS` — path al archivo o flag de modo.

---

## Routing por tipo de input

### `/review` o `/review --doc` — Revisión del documento TFE

**Target:** `paper/SISTAC_TFE.docx` o sección de texto extraída

**Agentes:** writer-critic → verifier (standard mode)

**Workflow:**
1. Leer la sección indicada (texto extraído del .docx)
2. Leer `.claude/references/domain-profile.md` para calibrar notación
3. Despachar **writer-critic** — revisar calidad de escritura, APA 7, H1/H2/H3 respaldo, notación
4. Despachar **verifier** (standard mode) — integridad de artefactos referenciados
5. Reportar score compuesto

**Checks del writer-critic:**
- Calidad de escritura académica en español
- Alineación afirmaciones-evidencia (H1/H2/H3)
- Cumplimiento APA 7 (citas, referencias)
- Notación consistente (DIR, SPD, F1, T_cand)
- Hedging apropiado (sin sobre-cobertura)
- Convenciones UNIR (sin LaTeX en Word, tablas numeradas)

---

### `/review --code [archivo.py]` — Revisión de código Python

**Target:** script o módulo en `scripts/python/`

**Agente:** coder-critic (standalone)

**Workflow:**
1. Leer el archivo Python objetivo
2. Leer `content-invariants.md` (INV-14 a INV-19)
3. Leer `coding-standards-python.md`
4. Despachar **coder-critic** con las 7 categorías de revisión:
   - Alineación con hipótesis H1/H2/H3
   - Invariantes INV-14 a INV-19
   - Calidad Python (imports, types, docstrings)
   - Manejo de llamadas LLM
   - Reproducibilidad (seed, requirements.txt)
   - Correctitud de métricas (F1, DIR, SPD)
   - Cobertura de tests

---

### `/review --verify` — Verificación de infraestructura

**Agente:** verifier (standard o entrega según contexto)

**Workflow:**
1. Ejecutar checks 1-4 (standard): scripts Python, pytest, integridad de artefactos, frescura
2. Si contexto de PR a main: ejecutar checks 1-7 (entrega)
3. Reportar PASS/FAIL por check

---

### `/review --tutora` — Simulación de revisión de la Dra. Arguedas Lafuente

**Agente:** writer-critic en modo máxima severidad

**Workflow:**
1. Leer la sección indicada
2. Despachar writer-critic con severidad ADVERSARIAL (deducciones duplicadas)
3. Verificar cobertura completa de hipótesis H1/H2/H3
4. Verificar marco teórico, diseño experimental, métricas
5. Reportar score con nivel de severidad explícito

---

## Verificación post-review

En todos los modos, después del critic:

```
Score >= 90 → PASS — listo para PR
Score 80-89 → WARN — corregir issues mayores antes de PR
Score < 80  → FAIL — bloqueado, corrección obligatoria
```

---

## Outputs

- Reporte del critic: `quality_reports/review_[fecha]_[target].md`
- Reporte del verifier: `quality_reports/verify_[fecha].md`
- Score final reportado al usuario con desglose
