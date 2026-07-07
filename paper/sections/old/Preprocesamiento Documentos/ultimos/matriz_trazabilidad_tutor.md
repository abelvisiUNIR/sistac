# Matriz de Trazabilidad: Objetivos, Hipótesis y Resultados

Esta tabla vincula de forma explícita cada uno de los objetivos específicos (OE) definidos en el Capítulo 3 con las hipótesis experimentales del TFE, sus métricas e instrumentos asociados, los resultados numéricos concretos obtenidos y su grado de cumplimiento.

## Matriz de Trazabilidad de SISTAC

| Objetivo Específico (OE) | Hipótesis Asociada | Métrica / Instrumento | Resultado Empírico Registrado | Grado de Cumplimiento |
|---|---|---|---|---|
| **[OE1] Corpus de Calibración y Evaluación**<br>Construir el corpus de calibración (300 pares sintéticos) y adaptar el de validación externa (150 pares reales). | No aplica *(Preparación y caracterización de datos)* | Cantidad de pares de CV-JD procesados y representatividad de perfiles. | **300 pares sintéticos** generados para calibración.<br>**150 pares reales** (Hugging Face) traducidos y balanceados al 50/50 (75 APTO / 75 NO_APTO) para validación externa. | **Completo (100%)** |
| **[OE2] Pipeline RAG**<br>Implementar la recuperación semántica (C2/C3) y evaluar desempeño. | No aplica *(Validación de componente de software)* | Precisión de Contexto (*Context Precision*) mediante el framework RAGAS. | **Context Precision de 0.9800** promedio para C2 con Claude Sonnet 4.5 (supera el umbral de 0.80). | **Completo (100%)** |
| **[OE3] Módulo de Anonimización PII**<br>Suprimir PII adaptado al contexto rioplatense. | **H1** (Eficiencia)<br>**H3** (Mitigación de sesgos) | Precisión y Recall sobre Golden Set rioplatense (15 entidades controladas). | **Precisión: 1.0000**<br>**Recall: 1.0000** (supera el umbral de 0.95 en test unitario). | **Completo (100%)** |
| **[OE4] Gold Standard**<br>Conformar panel de 3 expertos de Matriz y validar acuerdo. | No aplica *(Construcción de referencia de validación)* | Coeficiente Kappa de Cohen promedio calculado por pares de evaluadores. | **Acuerdo perfecto en 82.0%** (123/150 pares).<br>**Kappa promedio = 0.7600** inicial (supera el umbral ≥ 0.70). Consenso final al 100%. | **Completo (100%)** |
| **[OE5] Estudio Comparativo**<br>Ejecutar y registrar métricas C0-C3. | **H1** (Eficiencia)<br>**H2** (Eficacia) | Tiempos de procesamiento por CV.<br>Métricas de clasificación (F1-score macro, AUC-ROC) frente al Gold Standard. | **Eficiencia (Aceptada H1):** C1 (4.5s), C2 (6.8s), C3 (19.6s) vs. C0 manual (661.8s).<br>**Eficacia (Rechazada H2):** F1-score base de 0.52-0.56 con umbral rígido de 70. **F1 optimizado (Youden) de ~0.69** con umbral calibrado (34-48). | **Completo (100%)** |
| **[OE6] Equidad Algorítmica**<br>Calcular impacto dispar y contraste estadístico. | **H3** (Equidad) | Disparate Impact Ratio (DIR) y Statistical Parity Difference (SPD) por género y edad (IC 95% bootstrap y Test exacto de Fisher). | **Equidad (Aceptada H3):** Fisher p-valores ≥ 0.30 en género y ≥ 0.43 en edad. Sin diferencias significativas.<br>DIR para edad 46-58 alcanza **0.8182** en C2/C3 (supera el umbral de 0.80 de la EEOC). | **Completo (100%)** |

---

> [!TIP]
> **Recomendación Académica:** Puedes copiar esta matriz de trazabilidad e insertarla al final de la sección **3.3 (Metodología de Trabajo)** o en las conclusiones del TFE. Esto cumple de forma directa con la exigencia de las instrucciones de UNIR citadas por la tutora y demuestra un absoluto control metodológico sobre el diseño del experimento.
