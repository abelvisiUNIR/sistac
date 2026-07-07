# Estado tras la nueva versión | 23/06/2026

Revisión del documento `Preselección curricular con LLMs y Recuperación Aumentada… ESIT.docx` (687 párrafos, 29 referencias).

## YA APLICADO ✓
- Título nuevo en portada.
- **Resumen y Abstract** con cuerpo de texto.
- **Referencias: 29 entradas** (estaban 9). Se agregaron las faltantes.
- **"SISTAC" eliminado** en todo el documento.
- **Azure → Vertex** corregido en el índice de figuras (solo queda la mención legítima en §4.3.3).
- **Índice de figuras regenerado** y sincronizado (Figura 1–24); **Figura 12** con título propio (output JSON).
- **Cap 4 sin código en prosa** (RANDOM_SEED, rutas .py, SCORE_THRESHOLD, variables GCP, etc. convertidos).
- **Decimales a punto** (salvo 1 resto, ver abajo).
- **David agregado en la portada**.
- **Anexo B**: tabla módulo→archivo (Tabla B1).
- **Track 3 integrado**: Tabla 12 (eficacia con umbral calibrado), Tabla 15 (equidad por género con IC y Fisher), Figura 20 (F₁ vs umbral), Figura 22 (DIR con IC), Figura 24 (evaluaciones válidas de Gemini) y los párrafos de umbral óptimo, Fisher e in-sample.

## PENDIENTE ✗ (en orden de importancia)

1. **[IMPORTANTE] Discusión y conclusiones de equidad sin reencuadrar.** §5.8 ya muestra que las diferencias no son significativas (IC + Fisher), pero **§6.1.3 y §6.2.2 no se actualizaron**: la discusión puede seguir afirmando que la anonimización "empeoró" la equidad, lo que **contradice la tabla nueva**. → Pegar los párrafos de §6.1.3 y §6.2.2 de `INTEGRACION_track3.md` (reencuadre a "no concluyente / estudio subdimensionado").

2. **Pie de la Figura 20 mal formado.** Aparece como *"La Figura 20 muestra F₁-score macro…"* (frase de referencia) en lugar de un pie *"Figura 20. F₁-score macro según el umbral…"*. Corregir el pie y verificar que la **imagen** esté insertada, no solo el texto.

3. **"Tabla 2" duplicada.** Siguen existiendo dos: *Tabla 2. Síntesis de la literatura* y *Tabla 2. Adaptación de CRISP-DM*. Renumerar.

4. **Código en prosa en §5.3 (Métricas).** Queda: *"calculadas en Python con las bibliotecas `scipy.stats` y `scikit-learn`… `efficiency_metrics.py`, `efficacy_metrics.py` y `fairness_metrics.py`"*. Convertir a descripción funcional (esta sección es del Cap 5; no estaba en el Cap 4 corregido).

5. **Etiquetas H1/H2/H3 restantes.** En prosa quedan dos: la **nota de la Tabla 11** ("Umbral de aceptación de H2:") y el párrafo de limitaciones ("…afectan a la exactitud de las métricas H3"). En los **títulos** de Tabla 11 (H2), Tabla 14 (H3) y Tabla 16 (H3) siguen las siglas; quitarlas si se busca cumplir la convención.

6. **Coma decimal en el Resumen.** "κ de Cohen = 0,76" → "0.76" (para unificar con el resto).

7. **Puntuación del título.** Falta los dos puntos: "…Recuperación Aumentada **:** un estudio sobre eficiencia, eficacia y equidad algorítmica". Corregir en portada y título.

8. **Formato menor de numeración.** "Tabla 12 Eficacia…" y "Figura 22 Disparate…" no tienen el punto tras el número (debería ser "Tabla 12." y "Figura 22.").

9. **Verificaciones finales.** Confirmar que las **imágenes** de las Figuras 20 y 22 estén insertadas (no solo el pie); decidir si se incluye la tabla opcional de equidad por edad con IC; y **actualizar los índices** (campos de Word) tras renumerar.

10. **(Opcional) Abstract.** Si se adopta el reencuadre de equidad como "no concluyente", suavizar la frase del abstract "does not mitigate disparate impact by gender" a "no significant differences in fairness were observed".
