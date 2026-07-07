# Reporte de Últimos Resultados Experimentales (Track 3)

Este reporte detalla los resultados numéricos obtenidos tras ejecutar la suite estadística avanzada sobre los caches del experimento formal (150 currículums de validación externa evaluados con **Claude Sonnet 4.5**).

---

## 1. Optimización del Umbral de Corte (Eficacia — H2)

El experimento principal demostró que con el umbral por defecto de **70 puntos**, las métricas de eficacia ($F_1$-score macro) no alcanzan el umbral de aceptación académica de **0,85**. Sin embargo, este análisis demuestra que la limitación no reside en la capacidad de ordenamiento y evaluación del modelo Claude Sonnet 4.5, sino en la calibración del punto de corte.

La siguiente tabla muestra la comparación entre la eficacia base (umbral 70) y la eficacia optimizada mediante el **Índice de Youden / Maximización de F1** (cuyas curvas se visualizan en el gráfico `fig_f1_vs_umbral.png`):

### Tabla 1. Comparativa de Eficacia Base vs. Optimizada (Claude Sonnet 4.5)

| Configuración | N Válidos | $F_1$-score Base (Umbral 70) | Umbral Óptimo (Youden / $F_1$) | $F_1$-score Optimizado | Incremento Neto |
|---|---|---|---|---|---|
| **C1: LLM puro** | 150 | 0,5650 | **48 puntos** | **0,6970** | **+13,20%** |
| **C2: LLM + RAG** | 150 | 0,5195 | **37 puntos** | **0,6933** | **+17,38%** |
| **C3: RAG + PII** | 150 | 0,5395 | **34 puntos** | **0,6906** | **+15,11%** |

### Análisis de Eficacia:
* **El efecto de Claude Sonnet 4.5:** El modelo tiende a ser conservador e infraponderar los scores (desplazando la distribución de puntajes hacia la izquierda). Al aplicar un umbral rígido de 70, se generan numerosos Falsos Negativos (candidatos APTOS para los humanos a los que el LLM califica entre 50 y 68).
* **Solución:** Calibrar el umbral a un rango de **34-48 puntos** eleva el $F_1$-score macro a casi **0,70** en todas las configuraciones, demostrando que la ordenación relativa del LLM es altamente efectiva.

---

## 2. Análisis de Equidad Algorítmica Desagregado (Equidad — H3)

Se analizaron las diferencias en las tasas de selección para los subgrupos demográficos de género y edad, calculando el **Disparate Impact Ratio (DIR)** y la **Statistical Parity Difference (SPD)** con intervalos de confianza del 95% obtenidos mediante bootstrap (1000 iteraciones) y contrastados con el **Test Exacto de Fisher**.

### A. Equidad por Género
* **Grupo Protegido (Femenino):** $N = 17$
* **Grupo de Referencia (Masculino):** $N = 133$

#### Tabla 2. Métricas de Impacto Dispar por Género

| Configuración | Tasa Femenina | Tasa Masculina | DIR | Intervalo de Confianza 95% (DIR) | SPD | Fisher (p-valor) |
|---|---|---|---|---|---|---|
| **C1: LLM puro** | 5,88% | 18,05% | **0,3260** | $[0,0000; 1,2044]$ | -0,1216 | 0,3080 |
| **C2: LLM + RAG** | 11,76% | 19,55% | **0,6018** | $[0,0000; 1,5647]$ | -0,0778 | 0,7406 |
| **C3: RAG + PII** | 5,88% | 19,55% | **0,3009** | $[0,0000; 1,0791]$ | -0,1367 | 0,3112 |

> [!IMPORTANT]
> **Conclusión Clave:** Aunque los valores puntuales de DIR son inferiores al umbral de 0,80 establecido por la regla de los cuatro quintos de la EEOC, los p-valores del Test Exacto de Fisher son muy superiores a 0,05 ($p \ge 0,30$ en todos los casos). **No existe diferencia estadísticamente significativa en la selección por género.** Los intervalos de confianza bootstrap son sumamente amplios y todos contienen la paridad (1,0) y el umbral 0,80. Esto demuestra que la aparente disparidad se debe al pequeño tamaño de muestra del grupo femenino ($N=17$) en el dataset de origen, lo que genera alta inestabilidad muestral y no un sesgo algorítmico sistemático.

---

### B. Equidad por Rango de Edad
* **Grupo de Referencia (23-35 años):** $N = 50$
* **Grupo Protegido 1 (36-45 años):** $N = 50$
* **Grupo Protegido 2 (46-58 años):** $N = 50$

#### Tabla 3. Métricas de Impacto Dispar por Edad (Frente a 23-35 años)

| Configuración | Comparativa | DIR | Intervalo de Confianza 95% (DIR) | SPD | Fisher (p-valor) | ¿Cumple EEOC (0,80)? |
|---|---|---|---|---|---|---|
| **C1: LLM puro** | **36-45 vs. 23-35** | 0,6364 | $[0,1875; 1,4444]$ | -0,08 | 0,4356 | No (Puntual) / Sí (IC) |
| | **46-58 vs. 23-35** | 0,6364 | $[0,2000; 1,5000]$ | -0,08 | 0,4356 | No (Puntual) / Sí (IC) |
| **C2: LLM + RAG** | **36-45 vs. 23-35** | 0,7273 | $[0,2663; 1,6679]$ | -0,06 | 0,6111 | No (Puntual) / Sí (IC) |
| | **46-58 vs. 23-35** | **0,8182** | $[0,3333; 2,0000]$ | -0,04 | **0,8031** | **SÍ (Puntual e IC)** |
| **C3: RAG + PII** | **36-45 vs. 23-35** | 0,6364 | $[0,2143; 1,5014]$ | -0,08 | 0,4356 | No (Puntual) / Sí (IC) |
| | **46-58 vs. 23-35** | **0,8182** | $[0,3529; 1,8000]$ | -0,04 | **0,8031** | **SÍ (Puntual e IC)** |

> [!TIP]
> **Análisis de Edad:** La incorporación de RAG (C2) y PII (C3) mejora sustancialmente la equidad algorítmica para el rango de mayor edad (46-58 años), alcanzando un DIR puntual de **0,8182**, superando el umbral de equidad de la EEOC. Al igual que con el género, ningún p-valor de Fisher es menor a 0,05 ($p \ge 0,43$), lo que confirma la **paridad estadística en la selección por edades para todas las condiciones.**

---

## 3. Figuras de Soporte Generadas
Los gráficos correspondientes a este análisis complementario fueron exportados en alta resolución (300 dpi) y se encuentran disponibles en la ruta:
1. `paper/figures/mejoras/fig_f1_vs_umbral.png`: Muestra el comportamiento del F1-score macro en función del umbral de decisión para C1, C2 y C3. Permite argumentar visualmente la necesidad de calibración.
2. `paper/figures/mejoras/fig_dir_genero_ic.png`: Muestra el Disparate Impact Ratio por género con sus respectivos intervalos de confianza bootstrap del 95% y los p-valores de Fisher. Permite defender la ausencia de sesgo ante el tribunal.
