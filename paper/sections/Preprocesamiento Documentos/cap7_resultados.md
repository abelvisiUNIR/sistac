# Capítulo 7 — Resultados

> Estructura de resultados con todas las cifras en `[PENDIENTE]`, lista para
> completarse tras la re-ejecución del experimento. Este capítulo presenta los
> resultados sin interpretarlos; la interpretación se desarrolla en el Capítulo 8.
> Voz impersonal, sin citas, prosa sin guiones largos. La fuente de cada valor se
> indica en la checklist final.

El presente capítulo reporta los resultados del experimento factorial ejecutado
sobre el corpus descrito en la sección 5.2.7, organizados por hipótesis. Cada
sección presenta la tabla de métricas correspondiente y describe los valores
observados sin emitir juicios interpretativos. La síntesis integrada de todas las
métricas por configuración se ofrece en la sección 7.4.

---

## 7.1  Resultados de H1: eficiencia

La Tabla 7.1 reporta el tiempo de procesamiento por candidato, T_cand, para cada
configuración, junto con el factor de aceleración respecto al cribado manual C0 y el
resultado de la prueba U de Mann-Whitney unilateral.

**Tabla 7.1. Métricas de eficiencia por configuración (H1).**

| Configuración | Mediana C0 (s) | Mediana Cx (s) | IQR Cx (s) | Factor de aceleración | U de Mann-Whitney | p-valor | H1 aceptada |
|---|---|---|---|---|---|---|---|
| C1 (LLM puro) | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| C2 (LLM + RAG) | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| C3 (LLM + RAG + PII) | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |

*Nota.* Medianas e IQR en segundos por candidato. La columna de p-valor corresponde a
la comparación unilateral de cada configuración automática frente a C0. Fuente:
elaboración propia a partir de `paper/tables/tab_resultados_h1.csv`.

La mediana del tiempo de cribado manual C0 fue de [PENDIENTE] segundos por
candidato. Las tres configuraciones automáticas redujeron ese tiempo a [PENDIENTE]
segundos en C1, [PENDIENTE] segundos en C2 y [PENDIENTE] segundos en C3, lo que
corresponde a factores de aceleración de [PENDIENTE], [PENDIENTE] y [PENDIENTE]
respectivamente. La prueba U de Mann-Whitney arrojó un p-valor de [PENDIENTE] en las
tres comparaciones, [PENDIENTE: por debajo o por encima] del nivel de significancia
de 0.05. El incremento de tiempo de C2 y C3 respecto a C1, atribuible a la
generación de embeddings y a la consulta al índice vectorial, fue de [PENDIENTE]
segundos.

---

## 7.2  Resultados de H2: eficacia técnica

La Tabla 7.2 reporta el F1-score macro y el AUC-ROC de cada configuración automática
frente al Gold Standard, con el intervalo de confianza al noventa y cinco por ciento
del AUC-ROC estimado por bootstrap. La configuración C0 no aparece, dado que
constituye la propia referencia humana y no produce una métrica de eficacia.

**Tabla 7.2. Métricas de eficacia frente al Gold Standard (H2).**

| Configuración | F1-score macro | AUC-ROC | IC 95% AUC-ROC | H2 aceptada |
|---|---|---|---|---|
| C1 (LLM puro) | [PENDIENTE] | [PENDIENTE] | ([PENDIENTE], [PENDIENTE]) | [PENDIENTE] |
| C2 (LLM + RAG) | [PENDIENTE] | [PENDIENTE] | ([PENDIENTE], [PENDIENTE]) | [PENDIENTE] |
| C3 (LLM + RAG + PII) | [PENDIENTE] | [PENDIENTE] | ([PENDIENTE], [PENDIENTE]) | [PENDIENTE] |

*Nota.* Intervalos de confianza calculados con bootstrap de mil remuestreos. Umbral
de aceptación de H2: F1 mayor o igual a 0.85 y AUC-ROC mayor o igual a 0.90. Fuente:
elaboración propia a partir de `paper/tables/tab_resultados_h2.csv`.

El F1-score macro fue de [PENDIENTE] en C1, [PENDIENTE] en C2 y [PENDIENTE] en C3,
mientras que el AUC-ROC fue de [PENDIENTE], [PENDIENTE] y [PENDIENTE]
respectivamente. La comparación entre C1 y C2 muestra una diferencia de [PENDIENTE]
puntos de F1 atribuible al componente de recuperación. Respecto al umbral de
aceptación, [PENDIENTE: indicar qué configuraciones superan F1 mayor o igual a 0.85 y
AUC-ROC mayor o igual a 0.90].

La Figura 7.1 presenta la matriz de confusión de la configuración con mejor F1-score,
y la evaluación técnica in-vitro del pipeline RAG mediante RAGAS se reporta en la
Tabla 7.3.

`[FIGURA 7.1 — Matriz de confusión de la configuración con mejor F1-score frente al Gold Standard. Fuente: elaboración propia. REEMPLAZAR: imagen]`

**Tabla 7.3. Métricas RAGAS de la evaluación técnica in-vitro del pipeline (C2).**

| Faithfulness | Answer relevancy | Context precision |
|---|---|---|
| [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |

*Nota.* Métricas complementarias de diagnóstico del pipeline RAG, no constituyen la
métrica primaria de H2. Fuente: elaboración propia a partir de
`paper/tables/tab_ragas_c2.csv`.

---

## 7.3  Resultados de H3: equidad algorítmica

La equidad se reporta sobre dos atributos protegidos, el género y la edad. La Tabla
7.4 presenta el Disparate Impact Ratio, DIR, y el Statistical Parity Difference, SPD,
por género para las configuraciones C1, C2 y C3. La Tabla 7.5 presenta las mismas
métricas desglosadas por rango de edad.

**Tabla 7.4. Métricas de equidad por género (H3).**

| Configuración | DIR (género) | SPD (género) | H3 aceptada (DIR ≥ 0.80) |
|---|---|---|---|
| C1 (LLM puro) | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| C2 (LLM + RAG) | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| C3 (LLM + RAG + PII) | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |

*Nota.* Grupo protegido femenino, grupo de referencia masculino. DIR ideal mayor o
igual a 0.80; SPD ideal cero. Fuente: elaboración propia a partir de
`paper/tables/tab_resultados_h3.csv`.

**Tabla 7.5. Métricas de equidad por rango de edad (H3).**

| Configuración | Rango de edad | DIR (edad) | SPD (edad) |
|---|---|---|---|
| C2 (LLM + RAG) | 23–35 | [PENDIENTE] | [PENDIENTE] |
| C2 (LLM + RAG) | 36–45 | [PENDIENTE] | [PENDIENTE] |
| C2 (LLM + RAG) | 46–58 | [PENDIENTE] | [PENDIENTE] |
| C3 (LLM + RAG + PII) | 23–35 | [PENDIENTE] | [PENDIENTE] |
| C3 (LLM + RAG + PII) | 36–45 | [PENDIENTE] | [PENDIENTE] |
| C3 (LLM + RAG + PII) | 46–58 | [PENDIENTE] | [PENDIENTE] |

*Nota.* Grupo de referencia de edad: 23–35. DIR ideal mayor o igual a 0.80; SPD ideal
cero. Fuente: elaboración propia a partir de `paper/tables/tab_resultados_h3_edad.csv`
(generar al re-correr, desglosando por `group_age`).

Por género, el DIR fue de [PENDIENTE] en C1, [PENDIENTE] en C2 y [PENDIENTE] en C3,
con valores de SPD de [PENDIENTE], [PENDIENTE] y [PENDIENTE] respectivamente. La
comparación entre C2 y C3 muestra una variación del DIR de [PENDIENTE], que mide el
efecto de la anonimización. Por edad, el comportamiento del DIR y del SPD se reporta
en la Tabla 7.5, observándose [PENDIENTE: describir el patrón por rango de edad].

---

## 7.4  Resumen integrado de resultados

La Tabla 7.6 consolida todas las métricas por configuración en una sola vista.

**Tabla 7.6. Resumen integrado de métricas por configuración.**

| Configuración | T_cand (s) | F1 macro | AUC-ROC | DIR (género) | SPD (género) | DIR (edad) | SPD (edad) |
|---|---|---|---|---|---|---|---|
| C0 | [PENDIENTE] | — | — | — | — | — | — |
| C1 | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| C2 | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| C3 | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |

*Nota.* C0 solo aporta T_cand, dado que es la línea base humana. Las columnas de edad
reportan el valor agregado o el del rango de referencia, según se defina al
completar. Fuente: elaboración propia.

---

## Checklist de valores a completar tras la re-ejecución (Cap 7)

La siguiente correspondencia indica de dónde se toma cada valor una vez ejecutado el
experimento. Verificar que el modelo reportado en todo el capítulo sea Claude Sonnet
4.5.

| Bloque | Valores | Archivo fuente |
|---|---|---|
| Tabla 7.1 y prosa de 7.1 | Medianas C0/Cx, IQR, speedup, U, p-valor, veredicto H1 | `tab_resultados_h1.csv` |
| Tabla 7.2 y prosa de 7.2 | F1 macro, AUC-ROC, IC 95%, veredicto H2 | `tab_resultados_h2.csv` |
| Figura 7.1 | Matriz de confusión de la mejor configuración | generar de `eval_cache.json` |
| Tabla 7.3 | Faithfulness, answer relevancy, context precision | `tab_ragas_c2.csv` |
| Tabla 7.4 y prosa de 7.3 | DIR y SPD por género, veredicto H3 | `tab_resultados_h3.csv` |
| Tabla 7.5 | DIR y SPD por rango de edad | `tab_resultados_h3_edad.csv` (generar desglosando `group_age`) |
| Tabla 7.6 | Consolidado de todas las métricas | las tablas anteriores |

*Nota.* La tabla de equidad por edad no existe aún como archivo; al re-correr,
calcular DIR y SPD usando la columna `group_age` del Gold Standard, con el rango
23–35 como referencia, y exportarla como `tab_resultados_h3_edad.csv`.
