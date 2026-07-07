# Interpretación del recálculo (Track 3) | 23/06/2026

Lectura de los CSVs generados por `analisis_mejoras_estadisticas.py`. Tres conclusiones, dos confirman las mejoras propuestas y una es un hallazgo nuevo.

---

## 1. Eficacia (H2): el umbral de 70 explica casi toda la brecha — CONFIRMADO

Con el punto de corte calibrado, el F₁ macro de Claude sube de ~0,52–0,57 a ~0,69–0,70:

| Config | F₁ con umbral 70 | Umbral óptimo | F₁ con umbral óptimo | Ganancia |
|---|---|---|---|---|
| C1 | 0,565 | 48 | **0,697** | +0,132 |
| C2 | 0,520 | 37 | **0,693** | +0,174 |
| C3 | 0,540 | 34 | **0,691** | +0,151 |

El umbral óptimo cae entre 34 y 48 puntos, muy por debajo de los 70 fijados. Esto coincide exactamente con la matriz de confusión (sensibilidad 28 %): el corte de 70 era demasiado estricto para la escala de scores del modelo. **El F₁ "real" del sistema ronda 0,70, no 0,52**; gran parte de la baja eficacia era un artefacto del punto de corte.

**Matiz honesto e imprescindible:** este umbral óptimo se eligió sobre el mismo conjunto de test (optimización *in-sample*), por lo que 0,70 es una **cota optimista**. Para reportarlo con rigor conviene calibrar el umbral por validación cruzada o sobre una partición separada. Aun así, el mensaje se sostiene: el corte de 70 está lejos del óptimo y reduce artificialmente el F₁. Y aclarar también que, incluso optimizado, **sigue por debajo del umbral de 0,85** (la hipótesis de eficacia se mantiene rechazada, pero por un margen mucho menor).

---

## 2. Equidad (H3): las diferencias de género NO son significativas — CONFIRMADO (y más fuerte de lo esperado)

Con intervalos de confianza por bootstrap y test de Fisher, **ninguna** diferencia de DIR/SPD por género resulta estadísticamente significativa:

| Modelo · Config | DIR género | IC 95 % | Fisher p | ¿Significativo? |
|---|---|---|---|---|
| Claude C1 | 0,326 | [0,00 – 1,20] | 0,308 | No |
| Claude C2 | 0,602 | [0,00 – 1,56] | 0,741 | No |
| Claude C3 | 0,301 | [0,00 – 1,08] | 0,311 | No |
| Gemini C2 | 1,250 | [0,41 – 2,33] | 0,751 | No |
| Gemini C3 | 0,462 | [0,00 – 1,15] | 0,216 | No |

Todos los IC **incluyen el 1,0** (paridad) y todos los p de Fisher están muy por encima de 0,05. Con n=17 mujeres, la métrica no distingue sesgo de no-sesgo. **La afirmación de que la anonimización "empeoró" el DIR de 0,602 a 0,301 no tiene respaldo estadístico** (p=0,74 y p=0,31): es ruido muestral, tal como anticipaba la mejora #3.

Por **edad** ocurre lo mismo: en Claude C2 el grupo 46-58 da DIR 0,818 pero con IC [0,33 – 2,00] y p=0,80; no se puede afirmar que esté "libre de sesgo". Todas las comparaciones por edad son no significativas.

**Reencuadre recomendado para H3:** pasar de "la anonimización empeora la equidad de género" a "**no se detectan diferencias estadísticamente significativas en equidad entre configuraciones; el estudio está subdimensionado para evaluar el sesgo de género (n=17)**". Es una conclusión más débil pero defendible, y de hecho más interesante metodológicamente.

---

## 3. HALLAZGO NUEVO: la réplica con Gemini se apoya en datos incompletos

El recálculo expone que **Gemini dejó muchas evaluaciones sin score** (fallos de parseo): 14 en C1, **46 en C2 (31 % del corpus)** y 41 en C3. Claude no tuvo ninguno.

| Modelo · Config | n total | n con score nulo | n válido |
|---|---|---|---|
| Gemini C1 | 150 | 14 | 136 |
| Gemini C2 | 150 | 46 | 104 |
| Gemini C3 | 150 | 41 | 109 |

Esto significa que las cifras de robustez de Gemini (F₁, DIR) se calcularon sobre una fracción del corpus o tratando los fallos como NO_APTO. **Conviene declararlo como limitación** del análisis de robustez: la comparación Claude vs. Gemini no es del todo simétrica porque Gemini produjo hasta un tercio menos de evaluaciones válidas en C2. Refuerza, además, la elección de Claude como evaluador principal.

---

## Frases listas para pegar

**§5.7 (Resultados de eficacia), tras la tabla de F₁:**
> Un análisis posterior del punto de corte revela que el umbral de 70 puntos no es óptimo para la escala de scores del modelo. Recalibrando el umbral sobre la curva F₁, el F₁ macro de Claude asciende a 0,70 (C1), 0,69 (C2) y 0,69 (C3), con umbrales óptimos situados entre 34 y 48 puntos. Esta estimación es de carácter *in-sample* y debe interpretarse como una cota superior optimista, pero evidencia que buena parte de la brecha respecto al umbral de aceptación proviene de la calibración del corte y no de la capacidad discriminativa del sistema, coherente con los valores de AUC-ROC en torno a 0,73. Aun con el umbral óptimo, el desempeño permanece por debajo de 0,85, por lo que la hipótesis de eficacia se mantiene rechazada.

**§5.8 (Resultados de equidad), tras las tablas de DIR/SPD:**
> Al acompañar las métricas de equidad con intervalos de confianza por bootstrap (1 000 remuestreos) y la prueba exacta de Fisher, ninguna de las diferencias de DIR o SPD por género resulta estadísticamente significativa (p de Fisher entre 0,31 y 0,74; todos los intervalos de confianza incluyen el valor de paridad 1,0). El reducido tamaño del subgrupo femenino (n=17) sitúa estas estimaciones en un régimen de alta incertidumbre, por lo que la variación observada entre C2 y C3 no puede atribuirse a un efecto real de la anonimización. La misma falta de significación se observa en el análisis por rango de edad.

**§6.1.3 (Discusión de la equidad):**
> El resultado debe leerse con cautela estadística: las diferencias de equidad por género y edad no alcanzan significación, de modo que el estudio resulta subdimensionado para contrastar formalmente el efecto de la anonimización sobre el sesgo. Antes que demostrar un empeoramiento, la evidencia indica que el diseño no tiene potencia suficiente para detectar diferencias en un grupo protegido de diecisiete personas, lo que constituye en sí mismo un hallazgo metodológico relevante.

**§5.10 / Limitaciones (réplica de robustez):**
> La réplica con Gemini operó sobre un número menor de evaluaciones válidas, ya que el modelo no devolvió un score parseable en 14, 46 y 41 casos para C1, C2 y C3 respectivamente. Esta asimetría en la completitud de los datos debe considerarse al comparar ambos modelos y refuerza la elección de Claude Sonnet 4.5 como evaluador principal.

---

## Sugerencia de figura
Con `tab_curva_f1_umbral.csv` se puede graficar F₁ vs. umbral por configuración, marcando el corte de 70 y el óptimo. Es la figura que mejor comunica la mejora #1 en la defensa.
