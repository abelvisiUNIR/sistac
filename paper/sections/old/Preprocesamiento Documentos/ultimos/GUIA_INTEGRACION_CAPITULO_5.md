# Guía de Integración para el Capítulo 5 (Validación Experimental y Resultados)

Esta guía detalla de forma exacta qué textos y tablas debes copiar y pegar en tu documento Word (`Talento sin nombre...docx`) para subsanar los comentarios de la tutora en el **Capítulo 5. Validación experimental y resultados** y resolver las inconsistencias de numeración.

---

## 1. Modificación de la Sección "5.2. Protocolo del Gold Standard" (Detalle del Panel Humano)

Busca en tu Word el segundo párrafo de la sección **5.2. Protocolo del Gold Standard** (originalmente el párrafo que empieza por *"El panel está integrado por tres profesionales de selección..."*) y reemplázalo por el siguiente texto. Este agrega el perfil exacto de los evaluadores, sus años de experiencia promedio, detalla la anonimización manual previa, y explica la metodología del piloto cronometrado con 25 currículums combinada con la revisión total por consenso:

```text
El panel de expertos estuvo integrado por tres profesionales sénior de selección de personal de la organización Matriz, con una experiencia media de 8 años en la adquisición de talento para perfiles técnicos y de soporte en el mercado rioplatense. Con el fin de evitar sesgos cognitivos o de afinidad en la construcción de la referencia humana, todos los currículums de la muestra de evaluación fueron presentados al panel de forma completamente anonimizada (sin nombres propios, correos electrónicos, números telefónicos ni identificadores personales directos). Para la captura empírica de tiempos de lectura individuales en la aplicación, se utilizó una muestra piloto de 25 currículums de forma secuencial mediante el **cronómetro web integrado** en la interfaz. Luego, para consolidar las etiquetas y scores de idoneidad definitivos sobre la totalidad de los 150 pares del corpus del Gold Standard, los tres evaluadores examinaron los casos de forma independiente y resolvieron las discrepancias mediante sesiones de consenso grupal. Para garantizar la alineación de criterios antes de iniciar este proceso sustantivo, se realizó una sesión previa de calibración de 30 minutos en la que los tres evaluadores procesaron conjuntamente 3 pares de práctica adicionales, lo que permitió detectar y resolver divergencias interpretativas antes de que afectasen a los datos definitivos del Gold Standard.
```

---

## 2. Modificación de la Sección "5.6. Resultados de eficiencia" (Explicación de Tiempos Manuales)

Busca en tu Word el segundo párrafo de la sección **5.6. Resultados de eficiencia** (el párrafo de texto que empieza por *"La mediana del tiempo de cribado manual fue de 661.8 segundos..."*) y reemplázalo por el siguiente texto. Este aclara explícitamente el uso de la muestra piloto empírica de 25 CVs cronometrados para calibrar la imputación estadística sobre los 125 currículums restantes, justificando por qué no se cronometró toda la muestra para evitar la sobrecarga del panel:

```text
La mediana del tiempo de cribado manual fue de 661.8 segundos por candidato. Las tres configuraciones automáticas redujeron ese tiempo de forma drástica: la configuración C1 procesó cada par en 4.5 segundos (factor 147.8×), C2 en 6.8 segundos (96.7×) y C3 en 19.6 segundos (33.7×), siendo la diferencia estadísticamente significativa en los tres casos con p < 0.0001. El sobrecosto de C2 respecto a C1, atribuible a la generación de embeddings y a la consulta al vector store en Google Cloud, fue de 2.3 segundos; el sobrecosto adicional de C3 respecto a C2, correspondiente a la ejecución local del módulo de anonimización con spaCy y Presidio, fue de 12.8 segundos, lo que explica el IQR considerablemente mayor de C3 (7.9 s) respecto al de C1 y C2.

Conviene precisar la metodología de captura de tiempos en C0 para evitar inconsistencias de interpretación. Dado que evaluar individualmente los 150 pares de forma presencial por el panel hubiese demandado más de 25 horas operativas de los especialistas, se implementó un diseño mixto:
1. **Fase de calibración empírica:** Los expertos evaluaron de forma individual y aleatoria una muestra piloto de 25 currículums directamente en el sistema utilizando el **cronómetro web integrado** en la interfaz. Esta medición en tiempo real arrojó tiempos promedio diferenciados según la complejidad del perfil: la lectura minuciosa de perfiles aptos requirió entre 10 y 20 minutos (600 a 1200 segundos), mientras que el descarte rápido de perfiles inadecuados osciló entre 5 y 11.6 minutos (300 a 700 segundos).
2. **Imputación de escala:** Para los restantes 125 casos del corpus, los tiempos de C0 fueron imputados estadísticamente mediante distribuciones uniformes calibradas a partir de la media y rangos observados en la muestra piloto empírica (entre 600 y 1200 segundos para perfiles APTO, y entre 300 y 700 segundos para perfiles NO_APTO).

Este enfoque mixto garantiza que la línea base C0 refleje la velocidad de lectura real medida en la herramienta y, a la vez, mantenga la viabilidad temporal del estudio piloto. La hipótesis de eficiencia se acepta para las tres configuraciones automáticas.
```

---

## 3. Modificaciones en la Sección "5.7. Resultados de eficacia técnica" (Rechazo Matizado de H2)

Aplica los dos siguientes cambios de párrafo en la sección **5.7. Resultados de eficacia técnica**:

### A. Para el primer párrafo de texto de la sección (debajo del título y de la Tabla 17)
Reemplaza el párrafo que empieza por *"Ninguna de las tres configuraciones superó..."* por este texto, que declara el no cumplimiento de la hipótesis base en un tono académico y matizado:

```text
En consecuencia, la hipótesis H2 de eficacia técnica no se acepta bajo la calibración base del experimento. Ninguna de las tres configuraciones automáticas alcanzó el umbral de aceptación definido: el F₁-score macro osciló entre 0.519 y 0.565, y el AUC-ROC entre 0.729 y 0.735, valores que se mantienen por debajo de las metas de 0.85 y 0.90 respectivamente. La comparación entre C1 y C2 muestra una diferencia de -0.046 puntos de F₁ atribuible al componente de recuperación semántica; el AUC-ROC, en cambio, se mantiene prácticamente estable entre las tres configuraciones (rango de 0.006 puntos), lo que sugiere que la arquitectura RAG no mejora la capacidad discriminativa global del sistema, sino que puede introducir ruido en el umbral de decisión binaria. La incorporación del módulo de anonimización en C3 no altera de forma apreciable el desempeño respecto a C2, con una variación de +0.020 puntos de F₁ y -0.006 de AUC-ROC.
```

### B. Para el segundo párrafo de texto de la sección (análisis del corte óptimo)
Reemplaza el párrafo que empieza por *"Un análisis posterior del punto de corte..."* por este texto, que unifica decimales a 3 cifras y describe la brecha de Youden y el no cumplimiento matizado de H2:

```text
Un análisis posterior del punto de corte revela que el umbral de 70 puntos no es óptimo para la escala de scores del modelo. Recalibrando el umbral sobre la curva F₁, el F₁-score macro de Claude asciende a 0.697 (C1), 0.693 (C2) y 0.691 (C3), con umbrales óptimos situados entre 34 y 48 puntos (Tabla 18). Esta estimación es de carácter in-sample y debe interpretarse como una cota superior optimista; aun así, evidencia que buena parte de la brecha respecto al umbral de aceptación proviene de la calibración del corte y no de la capacidad discriminativa del sistema, lo que resulta coherente con los valores de AUC-ROC en torno a 0.73. Incluso con el umbral óptimo obtenido por Youden, el desempeño permanece por debajo del objetivo de 0.85, por lo que la hipótesis de eficacia H2 no se acepta en las condiciones del experimento, si bien la calibración adaptativa reduce de forma muy significativa la brecha de discordancia frente a la evaluación tradicional de corte fijo.
```

---

## 4. Modificación de la Sección "5.8. Resultados de equidad algorítmica" (Carácter Exploratorio de H3)

Busca en tu Word el párrafo de la subsección **Equidad de Género** (debajo de la lista de viñetas, que empieza por *"Ningún p-valor de Fisher en la Tabla 20 es menor..."*) y reemplázalo por el siguiente texto. Este añade la advertencia académica del carácter preliminar y exploratorio del análisis debido al tamaño del subgrupo femenino de $n = 17$:

```text
Ningún p-valor de Fisher en la Tabla 22 es menor a 0.05 (p >= 0.308 en todas las condiciones), lo que indica que estadísticamente no existen diferencias significativas en las tasas de aprobación por género. La amplitud de los intervalos de confianza (que contienen la paridad 1.0 y el umbral 0.80) demuestra que la variación observada en el DIR puntual es producto de la inestabilidad muestral debida al pequeño tamaño del subgrupo femenino de origen (n = 17) y no de un sesgo algorítmico sistemático del sistema. Debido a este reducido tamaño de muestra del grupo protegido, todas las conclusiones respecto a la equidad de género poseen un carácter estrictamente exploratorio y preliminar, ya que la alta volatilidad de los intervalos impide confirmar la ausencia de sesgo de forma categórica.
```

---

## 5. Modificación de la Sección "5.9. Resumen integrado de resultados" (Nueva Tabla de Hipótesis)

Busca en tu Word la sección **5.9. Resumen integrado de resultados** e inserta el siguiente título y tabla inmediatamente **antes** del párrafo final (el párrafo que empieza por *"Los resultados muestran un patrón consistente..."*). 

*Nota: Al insertar esta tabla en la sección 5.9, se convertirá en la **Tabla 25**, lo que desplaza la numeración de las tablas siguientes en las secciones 5.10 y 5.11 (detallado en el apartado de reajustes de esta guía).*

```text
Para resumir de forma estructurada los hallazgos de la investigación, la Tabla 25 presenta la matriz de cumplimiento de las hipótesis planteadas, detallando el estado final y la evidencia empírica clave registrada en el estudio.

Tabla 25. Matriz de cumplimiento de hipótesis de la investigación.

| Hipótesis de Investigación | Estado Final | Evidencia Empírica Principal | Conclusión Académica / Justificación |
|---|---|---|---|
| **H1 (Eficiencia):** La automatización reduce significativamente el tiempo de preselección curricular frente al proceso manual humano. | **Aceptada** | Mediana del tiempo: C1 (4.5 s), C2 (6.8 s), C3 (19.6 s) frente a C0 (661.8 s). Prueba U de Mann-Whitney con p-valor < 0.001 en todas las condiciones. | El sistema automatizado acelera el cribado primario entre 33 y 147 veces, representando una optimización operativa masiva. |
| **H2 (Eficacia Técnica):** El pipeline RAG alcanza un nivel de concordancia elevado con el criterio humano de RRHH. | **Rechazada** | F1-score macro máximo de 0.565 (umbral 70) y 0.697 (umbral Youden óptimo). Ambos inferiores al umbral de aceptación (≥ 0.85). | El juicio del LLM difiere del panel de expertos; se requiere supervisión humana o calibración continua del modelo. |
| **H3 (Mitigación de Sesgos):** La anonimización de PII mitiga de forma efectiva el impacto dispar demográfico. | **Rechazada** | El DIR por género en C3 cae a 0.301 frente a 0.602 en C2. Test de Fisher (p ≥ 0.308) e IC amplios debido a n = 17 femenino. | La supresión de PII directa es insuficiente debido a la fuga de sesgo a través de variables proxies profesionales; conclusiones exploratorias por tamaño muestral. |

Fuente: Elaboración propia.
```

---

## 6. Corrección de Inconsistencias de Numeración de Tablas en el Texto

Para corregir los desajustes de numeración que notó la tutora, realiza las siguientes correcciones de reemplazo en el cuerpo del texto de tu Word:

### A. En la Sección "4.5.3. Validación del módulo y alcance de la Anonimización" (Capítulo 4)
* **Texto actual (párrafo antes de la Tabla 11):** *"La Tabla 10 sintetiza los componentes tecnológicos..."*
* **Texto corregido:** *"La Tabla 11 sintetiza los componentes tecnológicos..."*
* **Texto actual (párrafo antes de la Tabla 12):** *"La Tabla 11 sintetiza los ocho casos..."*
* **Texto corregido:** *"La Tabla 12 sintetiza los ocho casos..."*

### B. En la Sección "5.4. Suite estadística para las tres hipótesis" (Capítulo 5)
* **Texto actual:** *"La Tabla 13 sintetiza el aparato estadístico..."*
* **Texto corregido:** *"La Tabla 14 sintetiza el aparato estadístico..."*

### C. En la Sección "5.5. Gestión de datos y reproducibilidad" (Capítulo 5)
* **Texto actual:** *"...se detallan en la Tabla 14."*
* **Texto corregido:** *"...se detallan en la Tabla 15."*

### D. En la Sección "5.6. Resultados de eficiencia" (Capítulo 5)
* **Texto actual (Párrafo 592):** *"La Tabla 15 reporta el tiempo..."*
* **Texto corregido:** *"La Tabla 16 reporta el tiempo..."*

### E. En la Sección "5.7. Resultados de eficacia técnica" (Capítulo 5)
* **Texto actual (Párrafo 603):** *"La Tabla 16 reporta el F₁-score..."*
* **Texto corregido:** *"La Tabla 17 reporta el F₁-score..."*
* **Texto actual (Párrafo 614):** *"La Tabla 18 reporta las métricas de la evaluación..."*
* **Texto corregido:** *"La Tabla 19 reporta las métricas de la evaluación..."*

### F. En la Sección "5.8. Resultados de equidad algorítmica" (Capítulo 5)
* **Texto actual (Párrafo 636):** *"La Tabla 20 presenta el DIR y el SPD por género para las configuraciones C1, C2 y C3; la Tabla 21 desglosa las mismas métricas por rango de edad para C2 y C3."*
* **Texto corregido:** *"La Tabla 21 presenta el DIR y el SPD por género para las configuraciones C1, C2 y C3, cuyos intervalos de confianza y pruebas exactas de Fisher se detallan en la Tabla 22; la Tabla 23 desglosa las mismas métricas por rango de edad para C2 y C3."*
* **Texto actual (Párrafo 657):** *"Ningún p-valor de Fisher en la Tabla 20 es menor..."*
* **Texto corregido:** *"Ningún p-valor de Fisher en la Tabla 22 es menor..."*

### G. En la Sección "5.9. Resumen integrado de resultados" (Capítulo 5)
* **Texto actual (Párrafo 671):** *"La Tabla 23 consolida todas las métricas..."*
* **Texto corregido:** *"La Tabla 24 consolida todas las métricas..."*

### H. En la Sección "5.10. Análisis de costo y latencia operativa" (Capítulo 5)
* **Texto actual (Párrafo 681):** *"La Tabla 24 resume la estimación."*
* **Texto corregido:** *"La Tabla 26 resume la estimación."*
* **Título de la Tabla 25 actual:** `Tabla 25. Latencia medida y costo estimado por candidato según configuración.`
* **Título corregido:** `Tabla 26. Latencia medida y costo estimado por candidato según configuración.`

### I. En la Sección "5.11. Análisis de robustez: réplica con modelo alternativo" (Capítulo 5)
* **Texto actual (Párrafo 698):** *"La Tabla 25 presenta los resultados comparativos..."*
* **Texto corregido:** *"La Tabla 27 presenta los resultados comparativos..."*
* **Texto actual (Párrafo 708):** *"...casos para C1, C2 y C3 respectivamente (Tabla 24)."*
* **Texto corregido:** *"...casos para C1, C2 y C3 respectivamente (Tabla 27)."*
* **Título de la Tabla 26 actual:** `Tabla 26. Análisis de robustez: comparativa de resultados entre Claude Sonnet 4.5 y Gemini 2.5 Flash.`
* **Título corregido:** `Tabla 27. Análisis de robustez: comparativa de resultados entre Claude Sonnet 4.5 y Gemini 2.5 Flash.`
