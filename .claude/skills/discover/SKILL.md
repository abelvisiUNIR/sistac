---
name: discover
description: Fase de discovery de SISTAC — entrevista de diseño, búsqueda bibliográfica y exploración de datos. Rutea a Librarian (literatura ACL/FAccT/Expert Systems/arXiv), Explorer (corpus CVs sintéticos) o conduce entrevista de diseño experimental. Usar al iniciar un tema nuevo, buscar papers o explorar opciones de datos.
argument-hint: "[modo] interview | lit [tema] | data [tema]"
allowed-tools: Read,Grep,Glob,Write,Edit,WebSearch,WebFetch,Task
---

# Discover

Fase de discovery de SISTAC. Tres modos según el tipo de exploración.

**Input:** `$ARGUMENTS` — modo seguido de tema o pregunta.

---

## Modos

### `/discover interview` — Entrevista de diseño

Conducir una entrevista estructurada para clarificar un aspecto del diseño experimental o del TFE antes de implementar.

**Cuándo usar:**
- Antes de implementar un módulo nuevo
- Cuando hay ambigüedad en los requerimientos de H1/H2/H3
- Para tomar decisiones de diseño (ej: threshold de score para "APTO")

**Protocolo (preguntar una a la vez):**
1. ¿Cuál es el objetivo específico de este componente?
2. ¿Qué hipótesis (H1/H2/H3) impacta principalmente?
3. ¿Qué métricas de éxito son aceptables?
4. ¿Hay restricciones técnicas o de tiempo?
5. ¿Qué decisiones ya tomadas debo respetar?

**Output:** Especificación de requerimientos guardada en `quality_reports/specs/YYYY-MM-DD_[tema].md`

---

### `/discover lit [tema]` — Búsqueda bibliográfica

Despachar **Librarian** para buscar y organizar literatura relevante.

**Venues prioritarios para SISTAC:**
- ACL Anthology (ACL, EMNLP, NAACL)
- FAccT, AIES (fairness algorítmica)
- Expert Systems with Applications, AI & Ethics
- arXiv cs.CL, cs.IR, cs.AI (últimos 3 años)

**Output del Librarian:**
1. `quality_reports/literature/annotated_bibliography.md`
2. `quality_reports/literature/references.bib` (claves `AutorYear_keyword`)
3. `quality_reports/literature/frontier_map.md`
4. `quality_reports/literature/positioning.md`

**Después del Librarian:** despachar **librarian-critic** para revisar cobertura H1/H2/H3, venues y recencia.

**Temas habituales de SISTAC:**
- `lit llm cv screening` — scoring semántico de CVs con LLMs
- `lit rag recruitment` — RAG aplicado a RRHH
- `lit fairness hiring` — sesgo algorítmico en reclutamiento
- `lit pii anonymization` — anonimización PII en NLP
- `lit eu ai act` — marco normativo EU AI Act 2024/1689

---

### `/discover data [tema]` — Exploración de corpus

Despachar **Explorer** para evaluar opciones de generación o adquisición de datos para SISTAC.

**Qué evalúa el Explorer:**
- SDV (PrivBayes) para distribuciones demográficas realistas
- Faker `es_ES` para nombres, empresas y direcciones en español
- LLM-augmentation para textos de CV realistas
- Datasets públicos de referencia (ResuméAtlas, O*NET/ESCO)

**Output del Explorer:**
1. `quality_reports/data-assessment/corpus_options.md`
2. `quality_reports/data-assessment/generation_plan.md`
3. `quality_reports/data-assessment/demographic_targets.md`

**Después del Explorer:** despachar **explorer-critic** para verificar n≥300, balance demográfico y reproducibilidad.

---

## Reglas

- Siempre despachar el critic pareado después del worker
- Guardar outputs en `quality_reports/` antes de avanzar a la siguiente fase
- Si el tema intersecta literatura Y datos, correr ambos modos en paralelo
