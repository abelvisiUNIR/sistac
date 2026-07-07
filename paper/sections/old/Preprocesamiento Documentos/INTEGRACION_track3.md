# Integración del Track 3 en el documento | 23/06/2026

Guía de inserción: dónde va cada texto, cada tabla y cada figura del análisis complementario. Los números de tabla/figura son **sugeridos**; ajustar a la secuencia real tras renumerar (ver `respuestas_checklist.md`). Decimales con punto, para coincidir con el Cap 5 y 6.

Figuras generadas (300 dpi):
- `paper/figures/mejoras/fig_f1_vs_umbral.png`
- `paper/figures/mejoras/fig_dir_genero_ic.png`

Se regeneran con: `python scripts/python/figures/gen_track3_figures.py` (requiere haber corrido antes `analisis_mejoras_estadisticas.py`).

---

## CAPÍTULO 5 — Validación experimental y resultados

### → Sección 5.7 (Resultados de eficacia técnica)

**1. Pegar este párrafo** justo después del análisis de la Tabla 11 (la de F₁/AUC), antes de la Tabla RAGAS:

> Un análisis posterior del punto de corte revela que el umbral de 70 puntos no es óptimo para la escala de scores del modelo. Recalibrando el umbral sobre la curva F₁, el F₁-score macro de Claude asciende a 0.70 (C1), 0.69 (C2) y 0.69 (C3), con umbrales óptimos situados entre 34 y 48 puntos (Tabla 11b, Figura X1). Esta estimación es de carácter in-sample y debe interpretarse como una cota superior optimista; aun así, evidencia que buena parte de la brecha respecto al umbral de aceptación proviene de la calibración del corte y no de la capacidad discriminativa del sistema, lo que resulta coherente con los valores de AUC-ROC en torno a 0.73. Incluso con el umbral óptimo, el desempeño permanece por debajo de 0.85, por lo que la hipótesis de eficacia se mantiene rechazada, si bien por un margen sustancialmente menor al que sugiere el corte de 70.

**2. Insertar esta tabla** (diseñarla en Excel y pegar como imagen, igual que las demás):

**Tabla 11b. Eficacia con umbral de decisión calibrado (Claude Sonnet 4.5).**

| Configuración | F₁ macro (umbral 70) | Umbral óptimo | F₁ macro (umbral óptimo) | AUC-ROC |
|---|---|---|---|---|
| C1 (LLM puro) | 0.565 | 48 | 0.697 | 0.732 |
| C2 (LLM + RAG) | 0.520 | 37 | 0.693 | 0.735 |
| C3 (RAG + PII) | 0.540 | 34 | 0.691 | 0.729 |

*Nota. Umbral óptimo = punto de corte que maximiza el F₁ macro sobre la curva F₁ vs. umbral (optimización in-sample). Fuente: elaboración propia a partir de `tab_umbral_optimo.csv`.*

**3. Insertar esta figura** después de la curva ROC (Figura 19):

`paper/figures/mejoras/fig_f1_vs_umbral.png`

> **Figura X1. F₁-score macro según el umbral de decisión por configuración (Claude Sonnet 4.5).** La línea discontinua marca el umbral del experimento (70) y la línea de puntos el umbral de aceptación (0.85); los marcadores señalan el F₁ máximo de cada configuración. Fuente: elaboración propia.

---

### → Sección 5.8 (Resultados de equidad algorítmica)

**1. Pegar este párrafo** después de las tablas de DIR/SPD (Tablas 13 y 14):

> Al acompañar las métricas de equidad con intervalos de confianza por bootstrap (1 000 remuestreos) y la prueba exacta de Fisher, ninguna de las diferencias de DIR o SPD por género resulta estadísticamente significativa (p de Fisher entre 0.31 y 0.74; todos los intervalos de confianza incluyen el valor de paridad 1.0), tal como se detalla en la Tabla 13b y se ilustra en la Figura X2. El reducido tamaño del subgrupo femenino (n = 17) sitúa estas estimaciones en un régimen de alta incertidumbre, por lo que la variación observada del DIR entre C2 y C3 no puede atribuirse a un efecto real de la anonimización. La misma falta de significación se observa en el análisis por rango de edad, cuyos intervalos de confianza son igualmente amplios.

**2. Insertar esta tabla:**

**Tabla 13b. Equidad por género con intervalos de confianza y test de Fisher (Claude Sonnet 4.5).**

| Configuración | DIR | IC 95% (DIR) | SPD | Fisher p | ¿Significativo? |
|---|---|---|---|---|---|
| C1 (LLM puro) | 0.326 | [0.00, 1.20] | -0.122 | 0.308 | No |
| C2 (LLM + RAG) | 0.602 | [0.00, 1.56] | -0.078 | 0.741 | No |
| C3 (RAG + PII) | 0.301 | [0.00, 1.08] | -0.137 | 0.311 | No |

*Nota. Grupo protegido: femenino (n = 17); referencia: masculino (n = 133). IC por bootstrap de 1 000 remuestreos (semilla = 42). Fuente: elaboración propia a partir de `tab_equidad_genero_ic.csv`.*

**3. (Opcional) Tabla de edad con IC** — si quieren reforzar el punto, añadir junto a la Tabla 14:

**Tabla 14b. Equidad por rango de edad con intervalos de confianza (Claude Sonnet 4.5).**

| Configuración | Grupo | DIR | IC 95% (DIR) | Fisher p |
|---|---|---|---|---|
| C2 | 36–45 | 0.727 | [0.27, 1.67] | 0.611 |
| C2 | 46–58 | 0.818 | [0.33, 2.00] | 0.803 |
| C3 | 36–45 | 0.636 | [0.21, 1.50] | 0.436 |
| C3 | 46–58 | 0.818 | [0.35, 1.80] | 0.803 |

*Nota. Grupo de referencia de edad: 23–35 años. Fuente: elaboración propia a partir de `tab_equidad_edad_ic.csv`.*

**4. Insertar esta figura** después de la Figura 20 (DIR por género):

`paper/figures/mejoras/fig_dir_genero_ic.png`

> **Figura X2. Disparate Impact Ratio por género con intervalos de confianza (bootstrap, 1 000 remuestreos).** La línea discontinua marca el umbral EEOC (0.80) y la de puntos la paridad (1.0); junto a cada punto se indica el valor p de Fisher. Todos los intervalos cruzan el valor de paridad. Fuente: elaboración propia.

---

### → Sección 5.10 (Análisis de robustez)

**Pegar este párrafo** al cierre de la comparación Claude vs. Gemini:

> La réplica con Gemini operó sobre un número menor de evaluaciones válidas, ya que el modelo no devolvió un score parseable en 14, 46 y 41 casos para C1, C2 y C3 respectivamente (Tabla 16b). En la configuración C2 ello implica que casi un tercio del corpus quedó sin evaluación válida. Esta asimetría en la completitud de los datos debe considerarse al comparar ambos modelos y refuerza la elección de Claude Sonnet 4.5 como evaluador principal.

**Insertar esta tabla** (pequeña):

**Tabla 16b. Evaluaciones válidas por configuración en la réplica con Gemini 2.5 Flash.**

| Configuración | n total | Sin score (fallo de parseo) | n válido |
|---|---|---|---|
| C1 | 150 | 14 | 136 |
| C2 | 150 | 46 | 104 |
| C3 | 150 | 41 | 109 |

*Nota. Claude Sonnet 4.5 no registró fallos de parseo. Fuente: elaboración propia a partir de `tab_recuentos_subgrupos.csv`.*

---

## CAPÍTULO 6 — Discusión y conclusiones

### → Sección 6.1.2 (Discusión de la eficacia técnica)

**Añadir al final de la sección:**

> La descomposición del resultado por umbral de decisión matiza la lectura de la eficacia. Con el corte fijado en 70 puntos, el sistema aparenta un F₁ macro en torno a 0.52–0.57, pero ese valor está dominado por una sensibilidad baja derivada de un umbral demasiado exigente para la escala de scores del modelo. Al calibrar el punto de corte, el F₁ asciende a aproximadamente 0.70, lo que reconcilia el desempeño con el AUC-ROC observado (~0.73) e indica que la limitación es de calibración y no de capacidad de ordenamiento. La eficacia, por tanto, no se alcanza en términos absolutos, pero su margen de mejora reside en una decisión de diseño corregible.

### → Sección 6.1.3 (Discusión de la equidad)

**Reemplazar la conclusión de "empeoramiento" por:**

> El resultado debe leerse con cautela estadística: las diferencias de equidad por género y por edad no alcanzan significación (test de Fisher no significativo en todas las configuraciones; intervalos de confianza que incluyen la paridad), de modo que el estudio resulta subdimensionado para contrastar formalmente el efecto de la anonimización sobre el sesgo. Antes que demostrar un empeoramiento de la equidad, la evidencia indica que el diseño no tiene potencia suficiente para detectar diferencias en un grupo protegido de diecisiete personas. Esta indeterminación constituye en sí misma un hallazgo metodológico relevante y orienta el trabajo futuro hacia el balanceo del corpus.

### → Sección 6.1.4 (Limitaciones del estudio)

**Añadir dos limitaciones a la lista:**

> Potencia estadística en el análisis de equidad: el subgrupo femenino (n = 17) es demasiado pequeño para estimar el DIR con precisión; las conclusiones de equidad por género deben considerarse exploratorias.

> Completitud de la réplica de robustez: el modelo alternativo (Gemini 2.5 Flash) no produjo un score válido en hasta un tercio de los casos de C2, por lo que su comparación con el evaluador principal no es plenamente simétrica.

### → Sección 6.2.2 (Conclusiones por hipótesis)

**Ajustar las conclusiones de eficacia y equidad:**

> Hipótesis de eficacia: se rechaza. Las configuraciones con recuperación semántica no alcanzan el umbral de F₁ macro ≥ 0.85 y AUC-ROC ≥ 0.90 frente al Gold Standard experto. No obstante, el análisis de calibración muestra que el F₁ efectivo del sistema se aproxima a 0.70 con un umbral de decisión ajustado, lo que sitúa la brecha en el terreno de la calibración antes que en el de la capacidad discriminativa.

> Hipótesis de equidad: no concluyente. La anonimización de PII directas no produjo diferencias estadísticamente significativas en el impacto dispar por género respecto a las configuraciones no anonimizadas; el tamaño del subgrupo protegido impide afirmar tanto una mejora como un empeoramiento.

---

## Resumen de inserciones

| Ubicación | Texto | Tabla nueva | Figura nueva |
|---|---|---|---|
| §5.7 Eficacia | 1 párrafo | Tabla 11b | Figura X1 (F₁ vs umbral) |
| §5.8 Equidad | 1 párrafo | Tabla 13b (+ 14b opcional) | Figura X2 (DIR con IC) |
| §5.10 Robustez | 1 párrafo | Tabla 16b | — |
| §6.1.2 Discusión eficacia | 1 párrafo | — | — |
| §6.1.3 Discusión equidad | reemplazo | — | — |
| §6.1.4 Limitaciones | 2 viñetas | — | — |
| §6.2.2 Conclusiones | 2 reemplazos | — | — |

> Recordatorio: tras insertar, renumerar tablas y figuras en secuencia y actualizar los índices (campos de Word). El resumen/abstract ya mencionan "no alcanza los umbrales de eficacia" y "la anonimización superficial no mitiga el impacto dispar"; si adoptan el reencuadre de equidad como "no concluyente", suavizar también esa frase del abstract a "no se observan diferencias significativas en equidad".
