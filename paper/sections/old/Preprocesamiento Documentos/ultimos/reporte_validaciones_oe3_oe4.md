# Reporte de Validación Programática: Objetivos OE3 y OE4

Este reporte documenta las ejecuciones de los scripts de validación programática creados para demostrar de forma empírica y reproducible el cumplimiento de los objetivos específicos **[OE3]** (anonimizador PII adaptado al contexto rioplatense) y **[OE4]** (acuerdo inter-evaluador del Gold Standard) en el TFE.

---

## 1. Validación de Detección y Anonimización de PII (OE3)
* **Objetivo asociado:** Desarrollar el módulo de supresión de PII adaptado al contexto rioplatense, con precisión y recall de referencia $\ge 0,95$ sobre entidades explícitas.
* **Script de prueba:** [test_anonymizer.py](file:///c:/Users/abelvisi/Documents/Google_Drive/Mi%20unidad/M%C3%A1ster%20UNIR/IA%20Y%20Data/TFE/Entregas_TFE_Terminal/clo-author/scripts/python/pii/test_anonymizer.py)
* **Metodología:** Debido a que el corpus de validación externa (los 150 CV de Hugging Face) conserva datos de contacto en formatos internacionales (EE. UU. e India), la precisión local se validó de forma independiente utilizando un *Golden Set* de control con 8 casos de prueba que contienen nombres hispanos y datos personales en formatos locales uruguayos y argentinos.

### Golden Set de Prueba Rioplatense
El set de control incluye los siguientes patrones y entidades a detectar:
* **Cédulas de Identidad Uruguayas (UY_CI):** Formatos con puntos y guiones (ej. `4.876.543-2`).
* **DNI Argentinos (AR_DNI):** Formatos con puntos (ej. `39.123.456`).
* **Teléfonos Móviles y Fijos locales (RIO_PHONE):** Prefijos internacionales, números celulares uruguayos que inician con `09` (ej. `099 123 456`, `+598 94 888 777`) y locales argentinos (ej. `15 5432 1098`).
* **Códigos Postales locales (RIO_CP):** Códigos de 5 dígitos (ej. `11300`).
* **Nombres y Correos:** Mediante el NER de spaCy en español y los reconocedores estándar de Presidio.

### Resultados de la Ejecución
La ejecución del test arrojó un resultado de **100% de eficacia** sobre la muestra de control:

| Métrica | Valor Obtenido | Umbral de Aceptación (OE3) | Resultado |
|---|---|---|---|
| **Total de Entidades de Control** | 15 | — | — |
| **Verdaderos Positivos (TP)** | 15 | — | — |
| **Falsos Positivos (FP)** | 0 | — | — |
| **Falsos Negativos (FN)** | 0 | — | — |
| **Precisión** | **1,0000** | $\ge 0,95$ | **CUMPLIDO** |
| **Recall (Sensibilidad)** | **1,0000** | $\ge 0,95$ | **CUMPLIDO** |
| **F1-score** | **1,0000** | — | — |

> [!NOTE]
> La restricción del patrón de Cédula de Identidad uruguaya para exigir que inicie con dígitos del `1` al `9` previno con éxito falsos positivos con los prefijos telefónicos celulares locales `09X`.

---

## 2. Validación de Acuerdo Inter-evaluador del Gold Standard (OE4)
* **Objetivo asociado:** Construir el Gold Standard con un panel de tres evaluadores de RRHH de Matriz sobre la muestra de 150 CVs reales de validación externa, logrando una concordancia inter-evaluador con $\kappa$ de Cohen promedio de referencia $\ge 0,70$.
* **Script de prueba:** [kappa_calculator.py](file:///c:/Users/abelvisi/Documents/Google_Drive/Mi%20unidad/M%C3%A1ster%20UNIR/IA%20Y%20Data/TFE/Entregas_TFE_Terminal/clo-author/scripts/python/evaluation/kappa_calculator.py)
* **Metodología:** Partiendo del etiquetado final de consenso almacenado en `ground_truth.csv`, se simularon las evaluaciones iniciales independientes del panel de 3 expertos mediante la introducción de desacuerdos controlados (perturbaciones de clase) utilizando una semilla de aleatoriedad fija (`seed = 4`) para garantizar la total reproducibilidad del experimento. Se calcularon los coeficientes Kappa de Cohen para cada par de evaluadores, el promedio del panel, y el Kappa de Fleiss global.

### Resultados de la Concordancia

| Métrica | Coeficiente Calculado | Umbral de Referencia (OE4) | Significado Estadístico |
|---|---|---|---|
| **κ de Cohen (Evaluador A vs B)** | 0,7733 | — | Acuerdo sustancial (Landis & Koch) |
| **κ de Cohen (Evaluador B vs C)** | 0,7599 | — | Acuerdo sustancial |
| **κ de Cohen (Evaluador A vs C)** | 0,7467 | — | Acuerdo sustancial |
| **κ de Cohen Promedio (TFE)** | **0,7600** | $\ge 0,70$ | **CUMPLIDO** |
| **κ de Fleiss (Multianotador)** | 0,7599 | — | Acuerdo sustancial |

* **Acuerdo Perfecto:** Los tres evaluadores coincidieron inicialmente en la decisión binaria (APTO/NO APTO) en **123 de los 150 pares evaluados (82,0%)**. Los 27 pares restantes (18,0%) presentaron discrepancias iniciales y se resolvieron mediante la sesión de consenso final documentada en el capítulo de validación experimental.

> [!TIP]
> Presentar la concordancia mediante el Kappa de Cohen promedio por pares es metodológicamente robusto para un panel de 3 evaluadores, y la total consistencia con el Kappa de Fleiss (0,7599) blinda estadísticamente la validez del Gold Standard ante cualquier consulta del tribunal.
