# Rúbricas de puntuación — Agentes críticos SISTAC

Archivo centralizado de tablas de puntuación. Cada critic referencia su sección.
Modificar aquí para actualizar la rúbrica de todos los critics simultáneamente.

---

## coder-critic

**Puntuación base: 100. Deducir por cada problema encontrado.**

| Problema | Deducción |
|----------|-----------|
| Hipótesis no implementada correctamente (H1/H2/H3) | -25 |
| INV-16 violado (ruta absoluta) | -15 |
| Métricas DIR/SPD calculadas incorrectamente | -15 |
| INV-14 violado (seed ausente con elemento estocástico) | -10 |
| Sin manejo de errores en llamadas LLM | -10 |
| Sin tests para el módulo | -10 |
| `anthropic`/`openai` importado directamente fuera de `llm/provider.py` | -10 |
| INV-15 violado (imports tardíos) | -5 |
| `requirements.txt` sin versiones pinadas | -5 |
| Sin docstrings en funciones públicas | -5 |

---

## writer-critic

**Puntuación base: 100. Deducir por cada problema encontrado.**

| Problema | Deducción |
|----------|-----------|
| Hipótesis H1/H2/H3 sin evidencia en tabla/figura | -20 |
| Números en texto no coinciden con tablas (INV-11) | -15 |
| Citas sin entrada en Bibliography_base.bib (INV-W4) | -10 por cita |
| Lenguaje causal injustificado (INV-8) | -10 |
| Notación inconsistente (INV-7) | -10 |
| Sobre-cobertura ("prueba", "demuestra definitivamente") | -5 |
| Anglicismos innecesarios o coloquialismos | -5 |
| Marcadores LaTeX en texto Word | -5 |

**Modo tutora:** duplicar todas las deducciones.

---

## explorer-critic

**Puntuación base: 100. Deducir por cada problema encontrado.**

| Problema | Deducción |
|----------|-----------|
| n < 300 alcanzable o no justificado | -25 |
| Atributos protegidos no controlados explícitamente | -20 |
| Texto CV insuficiente para scoring semántico LLM | -15 |
| Sin seed fijo o reproducibilidad no garantizada | -15 |
| JDs no contempladas en el plan | -10 |
| Spot-check de calidad ausente | -10 |
| Grades de viabilidad inconsistentes con el stack real | -5 |

---

## librarian-critic

**Puntuación base: 100. Deducir por cada problema encontrado.**

| Problema | Deducción |
|----------|-----------|
| Falta literatura sobre alguna hipótesis (H1/H2/H3) | -20 |
| No hay papers de venues principales (ACL/FAccT/Expert Systems) | -15 |
| No hay papers de los últimos 2 años | -10 |
| Marco normativo ausente (EU AI Act, EEOC) | -10 |
| Sin frontier_map ni identificación del gap | -10 |
| Puntuaciones de proximidad inconsistentes | -5 |
| Entradas BibTeX faltantes o mal formateadas | -5 por paper |
