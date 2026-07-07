# Correcciones para pegar | 23/06/2026

Cada bloque indica qué texto **buscar** en el documento y por cuál **reemplazarlo**. Decimales con punto, voz impersonal, sin guiones largos, sin siglas H1/H2/H3 en prosa.

> Nota: las limitaciones de "potencia estadística" y "completitud de la réplica" ya están en §6.1.4 — esas no hace falta tocarlas.

---

## A. §6.1.3 — Discusión de la equidad (lo más importante: hoy contradice tu tabla de §5.8)

### A1. Reemplazar el párrafo inicial

**BUSCAR:**
> Los resultados sobre la mitigación de sesgos de género mediante anonimización revelan un comportamiento contraintuitivo. Para el modelo Claude, el índice de impacto dispar (DIR) fue de 0.602 en la condición C2 (sin anonimizar) y se redujo a 0.301 en la condición C3 (anonimizado), alejándose sustancialmente del umbral regulatorio de 0.80 establecido por la EEOC. En el caso de Gemini, se observó un patrón similar de descenso, con un DIR de 1.397 en C2 (que indicaba una selección favorable hacia el grupo femenino) que cayó a 0.447 en C3.

**REEMPLAZAR POR:**
> Los resultados sobre la mitigación de sesgos de género deben interpretarse a la luz de su significación estadística. En el modelo Claude, el índice de impacto dispar (DIR) por género pasó de 0.602 en C2 (sin anonimizar) a 0.301 en C3 (anonimizado), y en Gemini de 1.397 a 0.447. Sin embargo, como se mostró en la sección de resultados, ninguna de estas diferencias alcanza significación estadística: la prueba exacta de Fisher resulta no significativa en todas las configuraciones y los intervalos de confianza por bootstrap incluyen el valor de paridad. Por tanto, la variación observada no puede interpretarse como un efecto real de la anonimización sobre la equidad, sino como fluctuación esperable en un subgrupo protegido muy reducido.

### A2. Reemplazar la frase de transición

**BUSCAR:**
> Este retroceso de la equidad al enmascarar los datos identificativos directos (PII) se atribuye a dos factores complementarios:

**REEMPLAZAR POR:**
> La aparente variación del DIR entre configuraciones, no significativa en términos estadísticos, resulta consistente con dos factores complementarios:

*(Los dos párrafos siguientes —señales indirectas de género y sensibilidad al tamaño muestral— se conservan tal cual.)*

### A3. Reemplazar el párrafo de edad

**BUSCAR:**
> En el análisis del sesgo por edad, el comportamiento del sistema fue diferente. En el modelo Claude, el rango de edad avanzada (46-58 años) se mantuvo estable en un DIR de 0.818 en ambas configuraciones (C2 y C3), superando el umbral de 0.80 y demostrando ausencia de impacto dispar. En el caso de Gemini, la anonimización (C3) mejoró el DIR del grupo de edad avanzada de 0.667 (C2) a 0.857 (C3). Esto sugiere que la supresión de referencias cronológicas e hitos históricos tempranos ayuda al modelo a evaluar la trayectoria con mayor objetividad etaria, neutralizando el impacto dispar en la selección de perfiles senior.

**REEMPLAZAR POR:**
> En el análisis por rango de edad, el grupo de edad avanzada (46-58 años) en Claude se mantuvo en un DIR de 0.818 en C2 y C3, y en Gemini pasó de 0.667 a 0.857 tras la anonimización. No obstante, los intervalos de confianza de estas estimaciones son igualmente amplios y las diferencias no resultan significativas, por lo que la aparente mejora de la objetividad etaria en perfiles senior debe tomarse como indicio exploratorio y no como un efecto demostrado.

---

## B. §6.2.2 — Conclusión de equidad

**BUSCAR (el ítem que empieza así):**
> Hipótesis de equidad: se rechaza. La anonimización superficial de PII directas (C3) no mitigó de forma efectiva el impacto dispar por género respecto a las configuraciones no anonimizadas, reduciendo el DIR de 0.602 (C2) a 0.301 (C3)…

**REEMPLAZAR POR:**
> Hipótesis de equidad: no concluyente. La anonimización de PII directas no produjo una mejora estadísticamente significativa del impacto dispar por género respecto a las configuraciones no anonimizadas (prueba de Fisher no significativa; intervalos de confianza que incluyen la paridad). El tamaño del subgrupo protegido (n = 17) impide sostener tanto una mejora como un empeoramiento de la equidad, por lo que el contraste queda abierto y se traslada al trabajo futuro mediante el balanceo del corpus.

---

## C. §5.3 — Código en prosa (Métricas)

**BUSCAR:**
> Cada hipótesis se operacionaliza mediante un conjunto de métricas específicas, calculadas en Python con las bibliotecas `scipy.stats` y `scikit-learn`, implementadas en los módulos `efficiency_metrics.py`, `efficacy_metrics.py` y `fairness_metrics.py`.

**REEMPLAZAR POR:**
> Cada hipótesis se operacionaliza mediante un conjunto de métricas específicas, calculadas en Python con las librerías científicas estándar de estadística inferencial y de evaluación de clasificadores. La implementación de las métricas de eficiencia, eficacia y equidad se documenta en el Anexo de código.

---

## D. Correcciones menores

### D1. Etiqueta H3 en limitaciones (§6.1.4)
**BUSCAR:** `…puede contener errores e inconsistencias sintácticas que afectan a la exactitud de las métricas H3.`
**REEMPLAZAR POR:** `…puede contener errores e inconsistencias que afectan a la exactitud de las métricas de equidad.`

### D2. Nota de la Tabla 11 (eficacia)
**BUSCAR:** `Umbral de aceptación de H2:`
**REEMPLAZAR POR:** `Umbral de aceptación de la hipótesis de eficacia:`

### D3. Coma decimal en el Resumen
**BUSCAR:** `κ de Cohen = 0,76`
**REEMPLAZAR POR:** `κ de Cohen = 0.76`

### D4. Título nuevo (portada, encabezado, nombre de archivo, repositorio)
Título canónico definitivo:

> **Talento sin nombre: anonimización, LLMs y RAG en el cribado curricular**

**BUSCAR (título actual en portada):** `Preselección curricular con LLMs y Recuperación Aumentada un estudio sobre eficiencia, eficacia y equidad algorítmica`
**REEMPLAZAR POR:** `Talento sin nombre: anonimización, LLMs y RAG en el cribado curricular`

Replicar el mismo título en: portada, encabezado/pie si repite el título, nombre del archivo `.docx` y README del repositorio. Verificar que el Resumen y el Abstract no mencionen el título anterior.

### D5. Pie de la Figura 20 (hoy es una frase, no un pie)
**BUSCAR:** `La Figura 20 muestra F₁-score macro según el umbral de decisión por configuración (Claude Sonnet 4.5)`
**REEMPLAZAR POR:** `Figura 20. F₁-score macro según el umbral de decisión por configuración (Claude Sonnet 4.5).`
*(Verificar además que la imagen `fig_f1_vs_umbral.png` esté insertada sobre ese pie.)*

### D6. Punto tras el número en dos rótulos
**BUSCAR:** `Tabla 12 Eficacia con umbral de decisión calibrado` → **REEMPLAZAR:** `Tabla 12. Eficacia con umbral de decisión calibrado`
**BUSCAR:** `Figura 22 Disparate Impact Ratio por género con intervalos de confianza` → **REEMPLAZAR:** `Figura 22. Disparate Impact Ratio por género con intervalos de confianza`

### D7. "Tabla 2" duplicada (requiere renumerar en Word)
Existen dos: *Tabla 2. Síntesis de la literatura…* (Cap 2) y *Tabla 2. Adaptación de CRISP-DM…* (Cap 3). Renumerar una de ellas y todas las posteriores en secuencia; luego actualizar el índice de tablas (clic derecho → Actualizar campos).

### D8. (Opcional) Nombre de clase en prosa (§6.1.3)
**BUSCAR:** `El módulo SistacAnonymizer enmascara nombres propios`
**REEMPLAZAR POR:** `El módulo de anonimización enmascara nombres propios`

---

## Cierre
Tras pegar A, B y C, actualizar los índices (campos de Word). Con eso, la discusión y las conclusiones quedan alineadas con la tabla de §5.8, que es la única incoherencia de fondo que quedaba.
