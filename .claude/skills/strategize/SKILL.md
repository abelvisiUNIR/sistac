---
name: strategize
description: Diseño del plan de análisis de SISTAC — define cómo medir H1/H2/H3, qué configuraciones comparar, qué métricas usar y cómo interpretar los resultados. Produce el plan de análisis pre-experimental para documentar en el TFE. Usar antes de implementar experimentos o para refinar el diseño C0-C3.
argument-hint: "[hipótesis o componente] h1 | h2 | h3 | corpus | full"
allowed-tools: Read,Grep,Glob,Write,Task
---

# Strategize

Diseño del plan de análisis experimental de SISTAC. Define qué medir, cómo y con qué criterio de éxito.

**Input:** `$ARGUMENTS` — hipótesis objetivo o componente.

---

## Qué produce

Para cada hipótesis o componente:
1. **Plan de medición** — variables, métricas, fórmulas
2. **Criterios de éxito** — umbrales aceptados
3. **Diseño de comparación** — qué configuraciones se comparan y por qué
4. **Amenazas a la validez** — qué podría invalidar los resultados
5. **Decisiones de diseño pendientes** — flags para el usuario

Guardar en `quality_reports/plans/analysis_plan_[hipotesis].md`

---

## Modos

### `/strategize h1` — Plan para Eficiencia

**Pregunta:** ¿C1-C3 son significativamente más rápidos que C0 (screening manual)?

**Variable de outcome:** `T_cand` (segundos de procesamiento por candidato)

**Diseño de medición:**
- C0: tiempo real de un revisor RRHH (o estimación documentada)
- C1-C3: `time.perf_counter()` en el orquestador

**Comparación:** C0 vs {C1, C2, C3} — diferencia en medias + intervalo de confianza

**Criterio de éxito:** reducción estadísticamente significativa (p < 0.05) de T_cand en C1-C3 vs C0

**Amenazas:** variabilidad del hardware, tamaño del CV, latencia de API

---

### `/strategize h2` — Plan para Eficacia

**Pregunta:** ¿Las configuraciones RAG (C2, C3) alcanzan F1 ≥ 0.85 y AUC-ROC ≥ 0.90 contra el Gold Standard?

**Variable de outcome:** F1 macro, AUC-ROC

**Gold Standard:** etiquetas de expertos RRHH (al menos 2 revisores, Cohen's κ ≥ 0.70)

**Comparación:** C1 vs C2 vs C3 — F1 y AUC-ROC por configuración

**Umbrales:**
- F1 macro ≥ 0.85 → H2 soportada
- AUC-ROC ≥ 0.90 → H2 soportada

**Amenazas:** sesgo del Gold Standard, distribución del corpus (balance APTO/NO_APTO), prompt engineering

---

### `/strategize h3` — Plan para Equidad

**Pregunta:** ¿La anonimización PII en C3 reduce DIR y SPD respecto a C1 y C2?

**Variable de outcome:** DIR (Disparate Impact Ratio), SPD (Statistical Parity Difference)

**Atributo protegido:** género inferido del nombre (proxy) en C1/C2; eliminado en C3

**Comparación:** C1 vs C2 vs C3 — DIR y SPD por configuración y por atributo

**Umbrales:**
- DIR ≥ 0.80 en C3 → H3 soportada
- SPD próximo a 0 en C3 → evidencia adicional

**Amenazas:** proxies de PII residuales (cargo, empresa), tamaño de muestra por grupo

---

### `/strategize corpus` — Plan del corpus sintético

**Pregunta:** ¿El corpus de ≥300 CVs es representativo y balanceado para medir H1/H2/H3?

**Diseño:**
- n ≥ 300 pares CV-JD
- Split: 70% train / 15% val / 15% test
- Balance demográfico: 50% género M/F, distribución de edad 25-55, niveles educativos variados
- Balance de clases: ~50% APTO / 50% NO_APTO en Gold Standard

**Herramientas:** Faker `es_ES` + LLM augmentation (Claude/GPT) + seed fijo para reproducibilidad

**Amenazas:** nombres como proxy de etnia, distribuciones artificiales, sesgo de plantillas LLM

---

### `/strategize full` — Plan completo C0-C3

Producir el plan de análisis completo cubriendo H1 + H2 + H3 + corpus. Formato para incluir en Cap. 3 (Metodología) y Cap. 6 (Validación experimental) del TFE.

---

## Principios

- **Pre-especificar antes de implementar.** El plan se documenta antes de ver los resultados.
- **Umbrales justificados en literatura.** DIR ≥ 0.80 viene de EEOC 4/5 rule; F1 ≥ 0.85 de benchmarks del campo.
- **Amenazas documentadas.** El TFE debe reconocer qué podría invalidar cada hipótesis.
- **El usuario decide.** Si hay trade-offs (ej: umbral de score "APTO"), se escalará antes de implementar.
