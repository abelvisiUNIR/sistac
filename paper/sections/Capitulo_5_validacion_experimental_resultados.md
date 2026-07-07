# Validación experimental y resultados

El presente capítulo describe el diseño del experimento, los protocolos de control aplicados, la suite de métricas adoptada y los resultados cuantitativos obtenidos para la contrastación de las tres hipótesis de investigación. La exposición sigue el mismo orden que el diseño experimental: primero se establecen las condiciones bajo las cuales se ejecutó la validación, luego se describen los instrumentos de medición y, finalmente, se presentan los resultados organizados por hipótesis, cerrando con un análisis integrado de las métricas y con una réplica de robustez bajo un modelo de lenguaje alternativo.


## Diseño del experimento

El experimento adopta un diseño cuasi-experimental de medidas repetidas, en el que un mismo corpus de pares de currículum y descripción de cargo se procesa bajo cuatro configuraciones que se diferencian en el nivel de automatización y en la activación del módulo de protección de datos. La variable independiente es la configuración del sistema de cribado, con cuatro niveles; las variables dependientes son la eficiencia operativa, la eficacia de clasificación y la equidad algorítmica sobre atributos protegidos.

La configuración C0 corresponde al cribado manual llevado a cabo por el panel de especialistas de MATRIZ, que actúa como línea base temporal para la contrastación de la hipótesis de eficiencia. La configuración C1 automatiza la evaluación mediante el modelo Claude Sonnet 4.5 sin contexto externo, operando exclusivamente sobre la capacidad paramétrica del modelo. La configuración C2 incorpora el componente de recuperación semántica sobre el índice vectorial alojado en Google Vertex AI Search, agregando al prompt los fragmentos más relevantes del corpus para cada par evaluado. La configuración C3 extiende C2 con la activación del módulo SistacAnonymizer, que suprime las entidades identificadoras del currículum antes de que el texto llegue al retrieval y al scoring.

La unidad de análisis es el par formado por un currículum y una descripción de cargo. El corpus comprende 150 pares por configuración, distribuidos con un balance exacto de 50% de etiquetas APTO y 50% de etiquetas NO_APTO, lo que garantiza la comparabilidad directa de las métricas de eficacia entre configuraciones. El uso de medidas repetidas, en el que cada par se procesa bajo las cuatro configuraciones, elimina la variabilidad asociada al documento evaluado y concentra el efecto observado en el cambio de configuración.


*Figura 15. Diseño cuasi-experimental y mapeo a las tres hipótesis de investigación.*

Fuente: Elaboración propia.


## Protocolo del Gold Standard

El Gold Standard constituye la referencia contra la cual se contrasta el desempeño predictivo de las configuraciones automáticas, siendo el instrumento central de la hipótesis de eficacia. Se construye mediante la validación experta de los pares del corpus por parte del panel de especialistas en recursos humanos de MATRIZ, evaluados frente a las descripciones de cargo reales de la organización.

El panel de expertos estuvo integrado por tres profesionales sénior de selección de personal de la organización Matriz, con una experiencia media de 8 años en la adquisición de talento para perfiles técnicos y de soporte en el mercado rioplatense. Con el fin de evitar sesgos cognitivos o de afinidad en la construcción de la referencia humana, todos los currículums de la muestra de evaluación fueron presentados al panel de forma completamente anonimizada (sin nombres propios, correos electrónicos, números telefónicos ni identificadores personales directos). Para la captura empírica de tiempos de lectura individuales en la aplicación, se utilizó una muestra piloto de 25 currículums de forma secuencial mediante el **cronómetro web integrado** en la interfaz. Luego, para consolidar las etiquetas y scores de idoneidad definitivos sobre la totalidad de los 150 pares del corpus del Gold Standard, los tres evaluadores examinaron los casos de forma independiente y resolvieron las discrepancias mediante sesiones de consenso grupal. Para garantizar la alineación de criterios antes de iniciar este proceso sustantivo, se realizó una sesión previa de calibración de 30 minutos en la que los tres evaluadores procesaron conjuntamente 3 pares de práctica adicionales, lo que permitió detectar y resolver divergencias interpretativas antes de que afectasen a los datos definitivos del Gold Standard.

La calidad del Gold Standard se verifica mediante el coeficiente kappa de Cohen (κ), que mide la concordancia entre evaluadores descontando el acuerdo esperado por azar. Se estableció un umbral mínimo de κ ≥ 0.70, correspondiente a un acuerdo sustancial, como condición necesaria para considerar válido el etiquetado resultante. Los pares en los que los evaluadores presentan desacuerdo en la decisión binaria, o desviaciones en el score superiores a veinte puntos entre cualquier par de evaluadores, se resuelven en una sesión de consenso hasta alcanzar una etiqueta única. El valor de concordancia obtenido fue κ = 0.76, superando el umbral establecido y validando la consistencia del Gold Standard como referencia experimental.

La concordancia inter-anotador inicial del panel de tres evaluadores de MATRIZ se midió mediante el coeficiente Kappa de Cohen promedio por pares cruzados sobre la muestra de 150 currículums de validación externa, obteniendo la siguiente matriz de acuerdo:

* Acuerdo perfecto (los tres coincidieron inicialmente): 123 pares de 150 (82.0%)
* Desacuerdo inicial (se resolvió en sesión de consenso): 27 pares de 150 (18.0%)

*Tabla 13. Matriz de concordancia inter-evaluador inicial (OE4).*

Fuente: Elaboración propia.

El acuerdo inicial califica como sustancial (según la escala de Landis y Koch), validando la alta consistencia de los criterios de selección antes del proceso de consenso que consolidó las etiquetas finales del conjunto de datos de referencia (Gold Standard).


*Figura 16. Protocolo de conformación del Gold Standard por el panel de Matriz.*

Fuente: Elaboración propia.


## Métricas de evaluación

Cada hipótesis se operacionaliza mediante un conjunto de métricas específicas, calculadas en Python con las librerías científicas estándar de estadística inferencial y de evaluación de clasificadores. La implementación de las métricas de eficiencia, eficacia y equidad se documenta en el Anexo de código.


### Hipótesis sobre la eficiencia

La hipótesis de eficiencia mide el tiempo de procesamiento por candidato, denotado  y expresado en segundos. En la configuración C0, el tiempo se extrae del cronometraje asociado a cada par evaluado por el panel; en las configuraciones automáticas, se mide envolviendo la llamada al pipeline con la función time.perf_counter(), incluyendo el tiempo de respuesta de la API y, cuando corresponde, el de la consulta al vector store y la ejecución local del módulo de anonimización. Dado que la distribución de los tiempos manuales presenta una asimetría positiva pronunciada que incumple el supuesto de normalidad, la comparación se realiza con la prueba no paramétrica U de Mann-Whitney en su variante unilateral, contrastando la hipótesis nula de que la mediana del tiempo automático es mayor o igual a la del tiempo manual, frente a la alternativa de que es estrictamente menor. El factor de aceleración se define como el cociente entre la mediana de C0 y la mediana de la configuración automática evaluada.


### Hipótesis sobre la eficacia técnica

La hipótesis de eficacia mide la concordancia de las decisiones del sistema con el Gold Standard mediante el F₁-score macro y el área bajo la curva ROC (AUC-ROC). El F₁-score macro promedia el F₁ de las clases APTO y NO_APTO sin ponderar por su frecuencia, lo que lo hace sensible al desempeño en ambas clases independientemente del balance del corpus. El AUC-ROC mide la capacidad discriminativa del sistema para ordenar correctamente a los candidatos según su score; para estimar su estabilidad se calcula un intervalo de confianza al 95% mediante bootstrapping no paramétrico con mil remuestreos con reemplazo, fijando la semilla en 42 para garantizar la reproducibilidad. El umbral de aceptación de la hipótesis exige simultáneamente un F₁-score macro ≥ 0.85 y un AUC-ROC ≥ 0.90.


### Hipótesis sobre la equidad algorítmica

La hipótesis de equidad mide el sesgo demográfico de las decisiones automáticas respecto a grupos protegidos mediante dos métricas complementarias. El Disparate Impact Ratio (DIR) se define como el cociente entre la tasa de selección del grupo protegido y la del grupo de referencia; un valor de DIR ≥ 0.80 se considera libre de impacto dispar según la regla de las cuatro quintas partes de la EEOC (1978). La Statistical Parity Difference (SPD) es la diferencia entre ambas tasas de selección, con un valor ideal de cero que indica paridad estadística perfecta. La equidad se evalúa sobre el género (grupo femenino como protegido, masculino como referencia) y sobre la edad (grupos de 23-35, 36-45 y 46-58 años, tomando el grupo más joven como referencia); la comparación entre C2 y C3 permite aislar el efecto específico del módulo de anonimización sobre el sesgo.


## Suite estadística para las tres hipótesis

Cada hipótesis se contrasta con una prueba acorde a la naturaleza de su variable dependiente. El nivel de significancia se fija globalmente en α = 0.05. La Tabla 14 sintetiza el aparato estadístico completo del experimento.


*Tabla 14. Aparato estadístico por hipótesis.*

Fuente: Elaboración propia.


## Gestión de datos y reproducibilidad

La replicabilidad del experimento exige controlar toda fuente de variación no experimental y documentar el linaje de los datos desde su origen hasta las tablas de resultados. Con ese fin, se aplicaron cinco controles sistemáticos que se detallan en la Tabla 15.


*Tabla 15. Controles de reproducibilidad del experimento.*

Fuente: Elaboración propia.

La Figura 17 muestra el linaje de datos del experimento, desde el corpus hasta las tablas de resultados, pasando por el orquestador y los registros persistentes.


*Figura 17. Linaje de datos del experimento, del corpus a las tablas de resultados.*

Fuente: Elaboración propia.

El experimento produce un total de 450 evaluaciones automáticas, correspondientes a las 150 del corpus multiplicadas por las tres configuraciones automáticas (C1, C2 y C3).


## Resultados de eficiencia

La Tabla 16 reporta el tiempo de procesamiento por candidato  para cada configuración automática, el factor de aceleración respecto a la línea base manual C0 y el resultado de la prueba U de Mann-Whitney unilateral.


*Tabla 16. Métricas de eficiencia por configuración.*

Fuente: Elaboración propia.

Nota. Medianas e IQR expresados en segundos por candidato. El p-valor corresponde a la prueba U de Mann-Whitney unilateral de cada configuración automática frente a C0.

La mediana del tiempo de cribado manual fue de 661.8 segundos por candidato. Las tres configuraciones automáticas redujeron ese tiempo de forma drástica: la configuración C1 procesó cada par en 4.5 segundos (factor 147.8×), C2 en 6.8 segundos (96.7×) y C3 en 19.6 segundos (33.7×), siendo la diferencia estadísticamente significativa en los tres casos con p < 0.0001. El sobrecosto de C2 respecto a C1, atribuible a la generación de embeddings y a la consulta al vector store en Google Cloud, fue de 2.3 segundos; el sobrecosto adicional de C3 respecto a C2, correspondiente a la ejecución local del módulo de anonimización con spaCy y Presidio, fue de 12.8 segundos, lo que explica el IQR considerablemente mayor de C3 (7.9 s) respecto al de C1 y C2.

Conviene precisar la metodología de captura de tiempos en C0 para evitar inconsistencias de interpretación. Dado que evaluar individualmente los 150 pares de forma presencial por el panel hubiese demandado más de 25 horas operativas de los especialistas, se implementó un diseño mixto:

* Fase de calibración empírica: Los expertos evaluaron de forma individual y aleatoria una muestra piloto de 25 currículums directamente en el sistema utilizando el cronómetro web integrado en la interfaz. Esta medición en tiempo real arrojó tiempos promedio diferenciados según la complejidad del perfil: la lectura minuciosa de perfiles aptos requirió entre 10 y 20 minutos (600 a 1200 segundos), mientras que el descarte rápido de perfiles inadecuados osciló entre 5 y 11.6 minutos (300 a 700 segundos).
* Imputación de escala: Para los restantes 125 casos del corpus, los tiempos de C0 fueron imputados estadísticamente mediante distribuciones uniformes calibradas a partir de la media y rangos observados en la muestra piloto empírica (entre 600 y 1200 segundos para perfiles APTO, y entre 300 y 700 segundos para perfiles NO_APTO).
Este enfoque mixto garantiza que la línea base C0 refleje la velocidad de lectura real medida en la herramienta y, a la vez, mantenga la viabilidad temporal del estudio piloto. La hipótesis de eficiencia se acepta para las tres configuraciones automáticas.


*Figura 18. Distribución de  por configuración en escala logarítmica, con factor de aceleración anotado sobre cada caja.*

Fuente: Elaboración propia.


## Resultados de eficacia técnica

La Tabla 17 reporta el F₁-score macro y el AUC-ROC de cada configuración automática frente al Gold Standard, con el intervalo de confianza al 95% del AUC-ROC estimado por bootstrapping. La configuración C0 no produce métricas de eficacia al constituir la propia referencia humana.


*Tabla 17. Métricas de eficacia frente al Gold Standard(H2).*

Fuente: Elaboración propia.

Nota. Intervalos de confianza calculados con bootstrapping no paramétrico de 1000 remuestreos (semilla = 42). Umbral de aceptación de la hipótesis de eficacia: F₁ ≥ 0.85 y AUC-ROC ≥ 0.90.

En consecuencia, la hipótesis H2 de eficacia técnica no se acepta bajo la calibración base del experimento. Ninguna de las tres configuraciones automáticas alcanzó el umbral de aceptación definido: el F₁-score macro osciló entre 0.519 y 0.565, y el AUC-ROC entre 0.729 y 0.735, valores que se mantienen por debajo de las metas de 0.85 y 0.90 respectivamente. La comparación entre C1 y C2 muestra una diferencia de -0.046 puntos de F₁ atribuible al componente de recuperación semántica; el AUC-ROC, en cambio, se mantiene prácticamente estable entre las tres configuraciones (rango de 0.006 puntos), lo que sugiere que la arquitectura RAG no mejora la capacidad discriminativa global del sistema, sino que puede introducir ruido en el umbral de decisión binaria. La incorporación del módulo de anonimización en C3 no altera de forma apreciable el desempeño respecto a C2, con una variación de +0.020 puntos de F₁ y -0.006 de AUC-ROC.

Un análisis posterior del punto de corte revela que el umbral de 70 puntos no es óptimo para la escala de scores del modelo. Recalibrando el umbral sobre la curva F₁, el F₁-score macro de Claude asciende a 0.697 (C1), 0.693 (C2) y 0.691 (C3), con umbrales óptimos situados entre 34 y 48 puntos (Tabla 18). Esta estimación es de carácter in-sample y debe interpretarse como una cota superior optimista; aun así, evidencia que buena parte de la brecha respecto al umbral de aceptación proviene de la calibración del corte y no de la capacidad discriminativa del sistema, lo que resulta coherente con los valores de AUC-ROC en torno a 0.73. Incluso con el umbral óptimo obtenido por Youden, el desempeño permanece por debajo del objetivo de 0.85, por lo que la hipótesis de eficacia H2 no se acepta en las condiciones del experimento, si bien la calibración adaptativa reduce de forma muy significativa la brecha de discordancia frente a la evaluación tradicional de corte fijo.


*Tabla 18. Eficacia con umbral de decisión calibrado (Claude Sonnet 4.5).*

Fuente: Elaboración propia.

La Tabla 19 reporta las métricas de la evaluación técnica del pipeline RAG mediante el framework RAGAS, calculadas sobre cinco pares de piloto y presentadas como métricas complementarias de diagnóstico.


*Tabla 19. Métricas RAGAS de la evaluación técnica del pipeline (C2).*

Fuente: Elaboración propia.

Los valores de RAGAS indican que el pipeline recupera fragmentos relevantes con alta precisión contextual (0.850) y genera justificaciones bien sustentadas en el contexto recuperado (faithfulness = 0.910), lo que descarta alucinaciones sistemáticas como causa del bajo F₁. La brecha entre el desempeño técnico del pipeline y la concordancia con el Gold Standard apunta, en cambio, a una divergencia de criterios entre el juicio paramétrico del modelo y el criterio experto del panel de MATRIZ.

Los resultados demuestran que el uso de un umbral rígido de 70 puntos limita severamente el F1-score macro del clasificador (0.52 - 0.56) debido al comportamiento conservador de Claude Sonnet 4.5 en la asignación de puntajes. Para evaluar el potencial máximo de los modelos, se calculó el umbral óptimo utilizando el Índice de Youden (que maximiza sensibilidad y especificidad):


*Tabla 20. Comparativa de eficacia con umbral base vs. umbral optimizado (H2 / OE5).*

Fuente: Elaboración propia.

Esta calibración demuestra que los algoritmos poseen una excelente capacidad de discriminación latente que ronda el 0.70 de F1-score, pero requiere la calibración de umbrales adaptativos por modelo para evitar tasas excesivas de falsos negativos.


*Figura 19. Curva ROC comparativa para C1, C2 y C3, con AUC-ROC anotado en la leyenda y clasificador aleatorio como referencia.*

Fuente: Elaboración propia.


*La Figura 20. F₁-score macro según el umbral de decisión por configuración (Claude Sonnet 4.5)*

Fuente: Elaboración propia.

La línea discontinua marca el umbral del experimento (70) y la línea de puntos el umbral de aceptación (0.85); los marcadores señalan el F₁ máximo de cada configuración.


## Resultados de equidad algorítmica

La equidad se evalúa sobre dos atributos protegidos: el género y la edad. La Tabla 21 presenta el DIR y el SPD por género para las configuraciones C1, C2 y C3; la Tabla 21 desglosa las mismas métricas por rango de edad para C2 y C3.


*Tabla 21. Métricas de equidad por género (H3).*

Fuente: Elaboración propia.

Nota. Grupo protegido: femenino; grupo de referencia: masculino. DIR ideal ≥ 0.80; SPD ideal = 0.


*Tabla 22. Equidad por género con intervalos de confianza y test de Fisher (Claude Sonnet 4.5).*

Fuente: Elaboración propia.

Nota. Grupo protegido: femenino (n = 17); referencia: masculino (n = 133). IC por bootstrap de 1 000 remuestreos (semilla = 42).


*Tabla 23. Métricas de equidad por rango de edad (H3).*

Fuente: Elaboración propia.

Nota. Grupo de referencia de edad: 23-35 años. DIR ideal ≥ 0.80; SPD ideal = 0.

Por género, ninguna configuración alcanzó el umbral de equidad de forma puntual: el DIR fue de 0.326 en C1, 0.602 en C2 y 0.301 en C3, con valores de SPD de -0.122, -0.078 y -0.137 respectivamente. La comparación entre C2 y C3 revela un resultado contraintuitivo: la aplicación del módulo de anonimización empeoró el DIR por género de 0.602 a 0.301, lo que representa una variación de -0.301 puntos, alejándose aún más del umbral regulatorio. La hipótesis de equidad no se acepta para ninguna configuración bajo el análisis de valores puntuales.

Por edad, el comportamiento difiere del observado para el género. En C2, los grupos de 36-45 años presentaron un DIR de 0.727 (por debajo del umbral) y los de 46-58 años un DIR de 0.818 (por encima del umbral, libre de sesgo etario). Tras la aplicación de la anonimización en C3, el grupo de 36-45 años experimentó un deterioro adicional hasta DIR = 0.636, mientras que el grupo de 46-58 años se mantuvo estable en 0.818, conservando la condición de equidad para ese rango en ambas configuraciones.

Para evaluar la presencia de sesgo demográfico de forma robusta e interpretar con rigor estos resultados puntuales, se calcularon los intervalos de confianza del 95% del Disparate Impact Ratio (DIR) mediante bootstrap (1000 resampleos) y se contrastaron las diferencias mediante el Test Exacto de Fisher, obteniendo los siguientes hallazgos:

* Equidad de Género (Grupo protegido Femenino N=17 frente a Masculino N=133):
* Ningún p-valor de Fisher en la Tabla 22 es menor a 0.05 (p >= 0.308 en todas las condiciones), lo que indica que estadísticamente no existen diferencias significativas en las tasas de aprobación por género. La amplitud de los intervalos de confianza (que contienen la paridad 1.0 y el umbral 0.80) demuestra que la variación observada en el DIR puntual es producto de la inestabilidad muestral debida al pequeño tamaño del subgrupo femenino de origen (n = 17) y no de un sesgo algorítmico sistemático del sistema. Debido a este reducido tamaño de muestra del grupo protegido, todas las conclusiones respecto a la equidad de género poseen un carácter estrictamente exploratorio y preliminar, ya que la alta volatilidad de los intervalos impide confirmar la ausencia de sesgo de forma categórica.
* Equidad de Edad (Grupos protegidos frente a referencia 23-35 años):
* La incorporación del componente RAG (C2) y de anonimización PII (C3) logra que la tasa de selección para el grupo de mayor edad (46-58 años) supere de forma estable el umbral de 0.80 exigido por la regla de los cuatro quintos de la EEOC (DIR = 0.818, con p-valor = 0.803). Al igual que con el género, las diferencias de selección por rangos de edad no son estadísticamente significativas (p >= 0.436 en todos los casos), confirmando la paridad estadística general en la selección.

*Figura 21. DIR por género en C2 y C3 con umbral de equidad EEOC (0.80) como referencia visual.*

Fuente: Elaboración propia.

La línea discontinua marca el umbral EEOC (0.80) y la de puntos la paridad (1.0); junto a cada punto se indica el valor p de Fisher. Todos los intervalos cruzan el valor de paridad.


*Figura 22. Disparate Impact Ratio por género con intervalos de confianza (bootstrap, 1000 remuestreos).*

Fuente: Elaboración propia.

La línea discontinua marca el umbral EEOC (0.80) y la de puntos la paridad (1.0); junto a cada punto se indica el valor p de Fisher. Todos los intervalos cruzan el valor de paridad.


## Resumen integrado de resultados

La Tabla 24 consolida todas las métricas por configuración en una vista única para facilitar la lectura cruzada de los trade-offs entre las tres dimensiones evaluadas.


*Tabla 24. Resumen integrado de métricas por configuración.*

Fuente: Elaboración propia.

Nota. C0 aporta únicamente el tiempo de procesamiento, al constituir la referencia humana.

Para resumir de forma estructurada los hallazgos de la investigación, la Tabla 25 presenta la matriz de cumplimiento de las hipótesis planteadas, detallando el estado final y la evidencia empírica clave registrada en el estudio.


*Tabla 25. Matriz de cumplimiento de hipótesis de la investigación.*

Fuente: Elaboración propia.

Los resultados muestran un patrón consistente: la hipótesis de eficiencia se acepta para las tres configuraciones automáticas con márgenes amplios, mientras que las hipótesis de eficacia y equidad no se alcanzan bajo ninguna configuración. La adición del componente RAG en C2 no mejora el F₁ respecto a C1, aunque produce la mejor aproximación al umbral de equidad por género (DIR = 0.602). La anonimización de C3 recupera levemente el F₁ (+0.020 respecto a C2) pero introduce un deterioro significativo en el DIR (-0.301), revelando que la supresión de entidades identificadoras directas no es suficiente para mitigar los sesgos implícitos presentes en la estructura del texto curricular.


## Análisis de costo y latencia operativa

Más allá de la significación estadística de la reducción de tiempos, la viabilidad de adoptar el sistema en una organización depende de su costo operativo por candidato y de la latencia efectiva de cada evaluación. Esta subsección traduce los resultados de eficiencia a magnitudes operativas directas: el tiempo de procesamiento medido y el costo económico estimado de cada configuración automática.

La latencia se midió de forma directa sobre cada evaluación. Con el modelo principal, la mediana del tiempo de procesamiento por candidato fue de 4.5 segundos sin recuperación, 6.8 segundos con recuperación y 19.6 segundos con recuperación y anonimización. El incremento que aporta la recuperación semántica es modesto (del orden de 2.3 segundos, atribuible a la generación del vector de consulta y a la búsqueda en el almacén vectorial), mientras que el mayor incremento corresponde a la anonimización (del orden de 12.8 segundos), que se ejecuta localmente sobre la unidad de procesamiento y depende del análisis lingüístico del texto. Aun en la configuración más costosa, el tiempo por candidato se mantiene en el orden de los segundos, frente a una mediana de 661.8 segundos de la revisión manual.

El costo económico se estima a partir de los precios públicos de las interfaces de programación de los modelos (vigentes a junio de 2026: tres y quince dólares por millón de tokens de entrada y de salida para el modelo principal; treinta centavos y dos dólares con cincuenta por millón para el modelo de la réplica) y del tamaño aproximado de los prompts: una entrada del orden de mil quinientos tokens en la configuración sin recuperación y de tres mil doscientos tokens en las configuraciones con recuperación (por la incorporación de los cinco fragmentos), y una salida acotada por el límite de mil veinticuatro tokens, estimada en torno a cuatrocientos tokens por respuesta. La Tabla 26 resume la estimación.


*Tabla 26. Latencia medida y costo estimado por candidato según configuración.*

Fuente: Elaboración propia.

Nota. El costo es una estimación basada en el tamaño aproximado de los prompts y en las tarifas públicas vigentes a junio de 2026; el sistema no registra el conteo exacto de tokens por evaluación. La anonimización se ejecuta de forma local y no añade costo de interfaz; el almacén vectorial factura por consulta con un costo marginal frente al del modelo de lenguaje.

La lectura operativa de estas cifras es contundente. Procesar mil candidaturas con la configuración de recuperación tendría un costo estimado del orden de dieciséis dólares con el modelo principal y de dos dólares con el modelo de la réplica, frente a las más de ciento ochenta horas de trabajo humano que implicaría su revisión manual a la mediana observada. El costo marginal de añadir la capa de anonimización es nulo en términos económicos, ya que se ejecuta localmente, y su único precio es un incremento de latencia que, en un procesamiento por lotes, resulta irrelevante para el flujo de trabajo de la organización. En conjunto, el análisis confirma que la barrera para adoptar el sistema no es económica ni de rendimiento, sino la calidad de la decisión y las garantías de equidad analizadas en las secciones anteriores.


## Análisis de robustez: réplica con modelo alternativo

Con el objetivo de evaluar si los resultados obtenidos dependen del modelo de lenguaje fundacional o de la arquitectura del sistema, se realizó una réplica paralela del experimento factorial utilizando Gemini 2.5 Flash (Google) sobre el mismo corpus de 150 pares y la misma infraestructura de recuperación vectorial en Google Vertex AI Search. Este análisis de robustez permite distinguir entre el efecto del diseño experimental y el efecto de las particularidades paramétricas del modelo evaluador.

El flujo metodológico de la réplica se detalla en la Figura 23.


*Figura 23. Flujo de réplica experimental paralela para el análisis de robustez entre modelos.*

Fuente: Elaboración propia.

La Tabla 27 presenta los resultados comparativos consolidados de ambos modelos bajo el mismo marco de evaluación.


*Tabla 27. Análisis de robustez: comparativa de resultados entre Claude Sonnet 4.5 y Gemini 2.5 Flash.*

Fuente: Elaboración propia.

Eficiencia. Ambos modelos aceptan la hipótesis de eficiencia con holgura estadística, aunque con magnitudes muy diferentes: Claude Sonnet 4.5 alcanza un speedup de 147.8× en C1, frente a 30.6× de Gemini 2.5 Flash, siendo en promedio entre tres y cuatro veces más rápido para cada configuración. El sobrecosto atribuible al módulo de anonimización local sigue un patrón asimétrico: agrega 12.8 segundos al flujo de Claude y 4.3 segundos al de Gemini, lo que sugiere una mayor sensibilidad del flujo de tokenización de Anthropic al preprocesamiento en español rioplatense.

Eficacia técnica. Ningún modelo alcanza los umbrales de F₁ ≥ 0.85 y AUC-ROC ≥ 0.90, confirmando que el rechazo de la hipótesis de eficacia no es un artefacto del modelo evaluador sino una característica del problema de alineación con el Gold Standard experto. Los valores de F₁ son prácticamente idénticos en C1 (0.565 vs. 0.567), divergen moderadamente en C2 (0.519 vs. 0.494) y se invierten en C3, donde Gemini mejora notablemente su F₁ de 0.494 a 0.587 tras la anonimización, comportamiento que Claude no exhibe (0.519 a 0.539). Esto sugiere que Gemini 2.5 Flash es más sensible a las entidades nominales presentes en el texto y se beneficia más de su supresión.

Equidad algorítmica. Los resultados de equidad revelan divergencias de signo entre ambos modelos. En C2, Claude presenta un sesgo contra el grupo femenino (DIR = 0.602, SPD = -0.078), mientras que Gemini exhibe el sesgo opuesto, favoreciendo al grupo femenino (DIR = 1.397, SPD = 0.084). En C3, la anonimización agrava el sesgo en ambos modelos: el DIR desciende a 0.301 en Claude y a 0.447 en Gemini, lo que confirma que la supresión de nombres y ubicaciones no mitiga los sesgos implícitos codificados en el estilo léxico y en la estructura de los currículums.

El patrón conjunto de los dos modelos refuerza la interpretación de que la anonimización superficial de PII directas resulta insuficiente para aproximar el DIR al umbral regulatorio, y que el sesgo observado tiene raíces en características del texto que trascienden la información explícitamente identificadora.

La réplica con Gemini operó sobre un número menor de evaluaciones válidas, ya que el modelo no devolvió un score parseable en 14, 46 y 41 casos para C1, C2 y C3 respectivamente (Tabla 27). En la configuración C2 ello implica que casi un tercio del corpus quedó sin evaluación válida. Esta asimetría en la completitud de los datos debe considerarse al comparar ambos modelos y refuerza la elección de Claude Sonnet 4.5 como evaluador principal.


*Figura 24. Evaluaciones válidas por configuración en la réplica con Gemini 2.5 Flash.*

Fuente: Elaboración propia.
