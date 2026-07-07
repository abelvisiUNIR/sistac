# Plan de aplicación de mejoras — TFE SISTAC
Fecha: 23/06/2026. Guía para llevar los entregables al `.docx`. Marcar cada ítem al completarlo.

---

## TRACK 1 — Texto (ya redactado; solo pegar)

- [ ] **Referencias faltantes** → pegar el Grupo A de `referencias_faltantes.md`, resolver los `[VERIFICAR]` del Grupo B (un clic por enlace) y **reordenar toda la lista alfabéticamente** junto con las 9 ya presentes. Aplicar sangría francesa APA 7.
- [ ] **Resumen y Abstract** → pegar de `resumen_abstract.md` bajo cada título (hoy solo tienen las palabras clave).
- [ ] **Cap 2** → reemplazar el cuerpo del capítulo por `cap_2_corregido.md` (arregla la enumeración paralela de §2.1 y los guiones largos).
- [ ] **Cap 4** → reemplazar el cuerpo por `cap_4_corregido.md` (saca el código en prosa; nombres de modelo en cursiva).
- [ ] **Portada** → agregar a **David Ilich Madrid Oyanadel** como segundo autor (hoy solo figura Mario).

## TRACK 2 — Ediciones en Word (manuales, rápidas)

- [ ] **Azure → Vertex** en los dos pies del **índice de figuras** (Figura 5 y Figura 6 dicen "Azure AI Search"; el cuerpo ya usa Vertex). *Ojo:* si el índice es un campo automático, corregir primero el **texto del pie real** en el cuerpo y luego actualizar el campo.
- [ ] **Quitar `doc_extractor.py`** del título de la Figura 4 en el índice de figuras.
- [ ] **Pie de Figura 12**: hoy repite el texto de la Figura 11. Ya viene corregido en `cap_4_corregido.md` ("Estructura del output JSON del motor de scoring…").
- [ ] **Renumerar figuras y tablas duplicadas**: hay dos "Tabla 2" (síntesis de literatura en Cap 2 y CRISP-DM en Cap 3) y numeración de figuras solapada. Unificar numeración correlativa.
- [ ] **Actualizar los tres índices** (contenidos, figuras, tablas): clic derecho sobre cada uno → "Actualizar campos" → "Actualizar toda la tabla". Esto resuelve también el "X" de página en Tabla 1.
- [ ] **Separador decimal**: unificar. El Cap 2 y el Cap 3 usan coma (0,716); el Cap 5 y el Cap 6 usan punto (0.565). Elegir uno (la convención en español es la coma) y aplicarlo en todo el documento, incluidas las tablas de resultados.
- [ ] **Nombre del modelo**: unificar a una sola forma. Coexisten "Claude Sonnet 4.5" (Cap 4) y "Claude 4.5 Sonnet" (Cap 5/6 y tabla comparativa).
- [ ] **Título único**: que portada, resumen, repositorio y archivo usen el mismo título del trabajo.
- [ ] **Etiquetas H1/H2/H3 en prosa** (decisión de estilo): si se quiere cumplir la convención de no rotular hipótesis con "H1/H2/H3" en el texto, reemplazar por "la hipótesis de eficiencia / eficacia / equidad" en Cap 5 y Cap 6. Si se mantienen, al menos unificar el formato.
- [ ] **Anexo A**: convertir el enlace al repo en una tabla breve módulo→archivo (extracción, embeddings, retrieval, scoring, anonimización, métricas), para no perder trazabilidad al haber sacado los nombres de archivo del cuerpo.

## TRACK 3 — Recálculo analítico (script listo, sin correr)

Script: `scripts/python/evaluation/analisis_mejoras_estadisticas.py`. Lee los caches `data/eval_cache_anthropic.json` (Claude) y `data/eval_cache_google.json` (Gemini) y escribe en `paper/tables/mejoras/`.

- [ ] Ejecutar cuando decidan:
  ```bash
  python scripts/python/evaluation/analisis_mejoras_estadisticas.py
  ```
- [ ] Revisar `tab_umbral_optimo.csv`: si `f1_opt` (umbral óptimo) es muy superior a `f1_base_thr70`, queda demostrado que **H2 está limitada por el punto de corte (70), no por la capacidad del modelo** (mejora #1 de `SISTAC_puntos_mejora.md`). Llevar ese F1 al texto de §5.7 y §6.1.2 como análisis secundario.
- [ ] Usar `tab_equidad_genero_ic.csv` y `tab_equidad_edad_ic.csv` para añadir **intervalos de confianza y test de Fisher** a las afirmaciones de H3 (§5.8, §6.1.3). Con n=17 mujeres, los IC mostrarán la fragilidad de la métrica y permitirán degradar las afirmaciones a "exploratorias".
- [ ] `tab_recuentos_subgrupos.csv` documenta los n por subgrupo (trazabilidad).
- [ ] El CSV de equidad por edad cubre el "[VALOR SIN FUENTE EN CSV]" señalado en el informe.

> Qué NO hace el script: no recalcula recall@10 (mejora #5), porque requiere los logs de recuperación con relevancia de referencia. Si existe ese registro, se puede añadir; avisar para extender el script.

---

## Orden sugerido
1. Referencias + Resumen/Abstract + portada (bloqueante para la entrega).
2. Pegar Cap 2 y Cap 4 corregidos.
3. Correr el script del Track 3 y volcar 3-4 cifras nuevas a §5.7/§5.8/§6.1.
4. Ediciones de Word (Azure→Vertex, numeración, índices, decimales, nombre del modelo) en una pasada final.
5. Actualizar campos y revisar cita↔referencia una última vez.
