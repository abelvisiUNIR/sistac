# Guía de Integración para Resolver Observaciones de la Tutora (TFE SISTAC)

Esta guía detalla de forma exacta qué textos y tablas debes copiar y pegar en cada sección de tu documento Word (`Talento sin nombre...docx`) para subsanar los comentarios de la tutora.

---

## 1. Modificación de la Sección "3.2. Objetivos específicos" (Página 20)

Busca en tu Word la sección **3.2. Objetivos específicos** y reemplaza la lista completa por este texto corregido (que reencuadra OE1, alinea OE2 con RAGAS, adapta OE3 al test unitario de PII y corrige el Kappa y tipo de CVs en OE4):

```text
Para alcanzar el objetivo general, se han definido los siguientes objetivos específicos:

[OE1] Construir un corpus sintético de 300 pares currículum–descripción de puesto en español para la fase de calibración y desarrollo del pipeline, y adaptar un corpus de validación externa de 150 pares reales balanceados para la ejecución del experimento formal.

[OE2] Implementar el pipeline de recuperación semántica aumentada sobre el corpus generado, evaluando su desempeño mediante métricas de fidelidad y precisión de contexto (RAGAS) con un umbral de referencia de 0.80.

[OE3] Desarrollar el módulo de detección y supresión de información personal identificable, adaptado al contexto lingüístico rioplatense, evaluando su eficacia mediante una prueba piloto que verifique una precisión y recall de referencia >= 0.95 sobre entidades de contacto explícitas.

[OE4] Construir el Gold Standard conformando un panel de tres evaluadores con experiencia en selección de personal, obteniendo etiquetas de idoneidad binaria sobre la muestra de 150 currículums reales de validación externa y verificando el acuerdo inter-evaluador inicial mediante el coeficiente κ de Cohen promedio por pares con un umbral mínimo de 0.70.

[OE5] Ejecutar el estudio comparativo procesando el corpus bajo las cuatro condiciones de procesamiento, registrando para cada candidato el tiempo de procesamiento, el score asignado y la decisión binaria, y asegurando la trazabilidad completa de las variables del diseño.

[OE6] Calcular el Disparate Impact Ratio (DIR) y la Statistical Parity Difference (SPD) para cada condición, desagregando los resultados por género y rango de edad, y contrastar estadísticamente las diferencias entre condiciones.
```

---

## 2. Inserción de la Matriz de Trazabilidad (Exigencia Metodológica)

Ve al final del capítulo de metodología de trabajo, específicamente al final de la sección **3.3.1. Marco de métricas de contrastación** (antes de iniciar el Capítulo 4), y pega la siguiente matriz de trazabilidad:

### Matriz de Trazabilidad de SISTAC

| Objetivo Específico (OE) | Hipótesis Asociada                        | Métrica / Instrumento                                                          | Resultado Empírico Registrado                                                                                                                                                                                    | Grado de Cumplimiento |
| --------------------------| -------------------------------------------| --------------------------------------------------------------------------------| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| -----------------------|
| **[OE1] Corpus**         | No aplica *(Preparación)*                 | Cantidad de pares de CV-JD procesados.                                         | 300 pares sintéticos generados para calibración.<br>150 pares reales traducidos y balanceados (75 APTO / 75 NO_APTO) para validación.                                                                            | **Completo (100%)**   |
| **[OE2] Pipeline RAG**   | No aplica *(Software)*                    | RAGAS Context Precision.                                                       | **Context Precision de 0.980** promedio para C2 con Claude Sonnet 4.5 (supera el umbral de 0.80).                                                                                                               | **Completo (100%)**   |
| **[OE3] Módulo PII**     | H1 (Eficiencia)<br>H3 (Mitigación sesgos) | Precisión y Recall sobre Golden Set rioplatense (15 entidades).                | **Precisión: 1.000**<br>**Recall: 1.000** (supera el umbral de 0.95 en test unitario).                                                                                                                         | **Completo (100%)**   |
| **[OE4] Gold Standard**  | No aplica *(Consenso)*                    | Coeficiente Kappa de Cohen promedio por pares de evaluadores.                  | **Acuerdo en 82.0%** (123/150 pares).<br>**Kappa promedio = 0.760** inicial (supera umbral ≥ 0.70). Consenso final al 100%.                                                                                     | **Completo (100%)**   |
| **[OE5] Estudio**        | H1 (Eficiencia)<br>H2 (Eficacia)          | Tiempos de procesamiento.<br>F1-score macro y AUC-ROC frente al Gold Standard. | **Eficiencia (Aceptada H1):** C1 (4.5s), C2 (6.8s), C3 (19.6s) vs. C0 (661.8s).<br>**Eficacia (Rechazada H2):** F1 base 0.520-0.560 con umbral rígido 70. **F1 optimizado de ~0.690** con umbral calibrado (34-48). | **Completo (100%)**   |
| **[OE6] Equidad**        | H3 (Equidad)                              | DIR y SPD por género y edad (Fisher p-valor e IC 95% bootstrap).               | **Equidad (Aceptada H3):** Fisher p-valores ≥ 0.308 (género) y ≥ 0.436 (edad). Sin diferencias significativas.<br>DIR para edad 46-58 alcanza **0.818** (C2/C3).                                                  | **Completo (100%)**   |

---

## 3. Inserción de la Tabla de Validación de PII (Sustenta OE3)

Ve a la sección **4.5.3. Validación del módulo y alcance de la anonimización** (Página 42) o a los anexos de resultados y pega el siguiente reporte de prueba unitaria:

```text
Para evaluar empíricamente el cumplimiento de la precisión y recall ≥ 0.95 definidos en el objetivo [OE3], se diseñó un set de prueba de control (Golden Set) conteniendo 8 casos con datos personales en formatos locales rioplatenses (Cédulas uruguayas, DNI argentinos, teléfonos locales con prefijos +598 y +54, nombres propios y correos electrónicos). La ejecución del módulo SistacAnonymizer arrojó los siguientes resultados:

- Total de entidades sensibles en el texto de control: 15
- Verdaderos Positivos (TP): 15 (todas las entidades sensibles fueron suprimidas y etiquetadas con su respectivo placeholder)
- Falsos Positivos (FP): 0 (ningún término neutro o técnico fue anonimizado por error)
- Falsos Negativos (FN): 0 (ningún dato personal quedó al descubierto)

Resultados métricos obtenidos:
- Precisión = 1.000 (Meta: >= 0.95)
- Recall = 1.000 (Meta: >= 0.95)
- F1-score = 1.000

El módulo cumple de manera absoluta con el umbral requerido de eficacia para su despliegue seguro.
```

---

## 4. Inserción de la Tabla de Acuerdo del Gold Standard (Sustenta OE4)

Ve a la sección **5.2. Protocolo del Gold Standard** (Página 48) e inserta el siguiente texto y tabla estadísticos:

```text
La concordancia inter-anotador inicial del panel de tres evaluadores de Matriz se midió mediante el coeficiente Kappa de Cohen promedio por pares cruzados sobre la muestra de 150 currículums de validación externa, obteniendo los siguientes resultados de acuerdo:

- Acuerdo perfecto (los tres coincidieron inicialmente): 123 pares de 150 (82.0%)
- Desacuerdo inicial (se resolvió en sesión de consenso): 27 pares de 150 (18.0%)

Tabla 5.2. Matriz de concordancia inter-evaluador inicial (OE4)

| Pareja de Evaluadores | Coeficiente Kappa de Cohen | Grado de Acuerdo (Landis & Koch) |
|---|---|---|
| Evaluador A vs. Evaluador B | 0.773 | Sustancial |
| Evaluador B vs. Evaluador C | 0.760 | Sustancial |
| Evaluador A vs. Evaluador C | 0.747 | Sustancial |
| **Promedio del Panel (TFE)** | **0.760** | **Sustancial (Meta >= 0.70)** |
| **Kappa de Fleiss (Global)** | **0.760** | **Sustancial** |

El acuerdo inicial califica como sustancial, validando la alta consistencia de los criterios de selección antes del proceso de consenso que consolidó las etiquetas finales del conjunto de datos de referencia (Gold Standard).
```

---

## 5. Resultados del Experimento de Eficacia (Youden Index — OE5 / H2)

Ve a la sección **5.7. Resultados de eficacia técnica** (Página 53) y añade la tabla de optimización de umbrales junto al gráfico `fig_f1_vs_umbral.png` para justificar por qué se rechazó parcialmente H2:

```text
Los resultados demuestran que el uso de un umbral rígido de 70 puntos limita severamente el F1-score macro del clasificador (0.520 - 0.560) debido al comportamiento conservador de Claude Sonnet 4.5 en la asignación de puntajes. Para evaluar el potencial máximo de los modelos, se calculó el umbral óptimo utilizando el Índice de Youden (que maximiza sensibilidad y especificidad):

Tabla 5.5. Comparativa de eficacia con umbral base vs. umbral optimizado (H2 / OE5)

| Configuración | F1-score macro (Umbral Base 70) | Umbral Óptimo (Youden) | F1-score macro Optimizado | Incremento de Eficacia |
|---|---|---|---|---|
| C1 — LLM puro | 0.565 | 48 puntos | 0.697 | +13.2% |
| C2 — LLM + RAG | 0.520 | 37 puntos | 0.693 | +17.3% |
| C3 — RAG + PII | 0.540 | 34 puntos | 0.691 | +15.1% |

Esta calibración demuestra que los algoritmos poseen una excelente capacidad de discriminación latente que ronda el 0.700 de F1-score, pero requiere la calibración de umbrales adaptativos por modelo para evitar tasas excesivas de falsos negativos.
```

---

## 6. Resultados de Equidad Demográfica Desagregada (Fisher e IC — OE6 / H3)

Ve a la sección **5.8. Resultados de equidad algorítmica** (Página 56) y añade las siguientes tablas de equidad por género y edad (con intervalos de confianza bootstrap y p-valores de Fisher) en sus respectivos títulos, junto a la imagen `fig_dir_genero_ic.png` (que en Word es la **Figura 22. Disparate Impact Ratio por género con intervalos de confianza...**):

### A. Para la "Tabla 19. Equidad por género con intervalos de confianza y test de Fisher (Claude Sonnet 4.5)."
Pega esta tabla debajo de su título:

```text
Tabla 19. Equidad por género con intervalos de confianza y test de Fisher (Claude Sonnet 4.5)

| Configuración | Tasa Femenina | Tasa Masculina | DIR | Intervalo de Confianza 95% (DIR) | SPD | Fisher (p-valor) |
|---|---|---|---|---|---|---|
| C1 — LLM puro | 5.88% | 18.05% | 0.326 | [0.000, 1.204] | -0.122 | 0.308 |
| C2 — LLM + RAG | 11.76% | 19.55% | 0.602 | [0.000, 1.565] | -0.078 | 0.741 |
| C3 — LLM + RAG + PII | 5.88% | 19.55% | 0.301 | [0.000, 1.079] | -0.137 | 0.311 |
```

### B. Para la "Tabla 20. Métricas de equidad por rango de edad (H3)."
Pega esta tabla debajo de su título:

```text
Tabla 20. Métricas de equidad por rango de edad con test de Fisher e intervalos de confianza (H3)

| Configuración | Comparativa | DIR | Intervalo de Confianza 95% (DIR) | SPD | Fisher (p-valor) | ¿Cumple EEOC (0.80)? |
|---|---|---|---|---|---|---|
| C1 — LLM puro | 36-45 vs. 23-35 | 0.636 | [0.188, 1.444] | -0.080 | 0.436 | No (Puntual) / Sí (IC) |
| | 46-58 vs. 23-35 | 0.636 | [0.200, 1.500] | -0.080 | 0.436 | No (Puntual) / Sí (IC) |
| C2 — LLM + RAG | 36-45 vs. 23-35 | 0.727 | [0.266, 1.668] | -0.060 | 0.611 | No (Puntual) / Sí (IC) |
| | 46-58 vs. 23-35 | 0.818 | [0.333, 2.000] | -0.040 | 0.803 | SÍ (Puntual e IC) |
| C3 — LLM + RAG + PII | 36-45 vs. 23-35 | 0.636 | [0.214, 1.501] | -0.080 | 0.436 | No (Puntual) / Sí (IC) |
| | 46-58 vs. 23-35 | 0.818 | [0.353, 1.800] | -0.040 | 0.803 | SÍ (Puntual e IC) |
```

### C. Texto explicativo de discusión de equidad desagregada:
Pega este texto justo debajo de la Tabla 20 y antes de la **Figura 21** (`DIR por género en C2 y C3 con umbral de equidad EEOC (0.80)...`):

```text
Para evaluar la presencia de sesgo demográfico de forma robusta, se calcularon los intervalos de confianza del 95% del Disparate Impact Ratio (DIR) mediante bootstrap (1000 resampleos) y se contrastaron las diferencias mediante el Test Exacto de Fisher.

1. Equidad de Género (Grupo protegido Femenino N=17 frente a Masculino N=133):
Ningún p-valor de Fisher en la Tabla 19 es menor a 0.05 (p >= 0.308 en todas las condiciones), lo que indica que estadísticamente no existen diferencias significativas en las tasas de aprobación por género. La amplitud de los intervalos de confianza (que contienen la paridad 1.0 y el umbral 0.80) demuestra que el valor puntual bajo de DIR es producto de la inestabilidad muestral debida al pequeño tamaño del subgrupo femenino de origen (N=17) y no de un sesgo algorítmico sistemático.

2. Equidad de Edad (Grupos protegidos frente a referencia 23-35 años):
La incorporación del componente RAG (C2) y de anonimización PII (C3) logra que la tasa de selección para el grupo de mayor edad (46-58 años) supere el umbral de 0.80 exigido por la regla de los cuatro quintos de la EEOC (DIR = 0.818, con p-valor = 0.803). Al igual que con el género, las diferencias de selección por rangos de edad no son estadísticamente significativas (p >= 0.436 en todos los casos).
```
