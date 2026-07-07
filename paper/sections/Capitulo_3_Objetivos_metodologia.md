# Objetivos y Metodología

A partir de las brechas identificadas en el estado del arte, este capítulo define el objetivo general del trabajo, los objetivos específicos que lo operacionalizan y la estrategia metodológica adoptada para su consecución.


## Objetivo general

El objetivo general del presente trabajo es evaluar el efecto diferencial de incorporar recuperación semántica aumentada y anonimización de información personal identificable en un sistema de preselección curricular basado en modelos de lenguaje de gran escala, mediante un estudio piloto controlado sobre un corpus sintético, con el fin de generar evidencia cuantitativa sobre el impacto de cada componente en la eficiencia del proceso, la calidad técnica de las decisiones de preselección y la equidad algorítmica de los resultados, en un contexto operativo representativo del sector de servicios compartidos en Uruguay. Este objetivo responde directamente a la ausencia de evidencia empírica desagregada por componente tecnológico identificada en la literatura, particularmente en el contexto latinoamericano y bajo marcos regulatorios como el uruguayo.


## Objetivos específicos

Para alcanzar el objetivo general, se han definido los siguientes objetivos específicos:

[OE1] Construir un corpus sintético de 300 pares currículum–descripción de puesto en español para la fase de calibración y desarrollo del pipeline, y adaptar un corpus de validación externa de 150 pares reales balanceados para la ejecución del experimento formal.

[OE2] Implementar un pipeline de recuperación semántica aumentada sobre el corpus generado, evaluando su desempeño mediante métricas de fidelidad y precisión de contexto (RAGAS) con un umbral de referencia de 0.80.

[OE3] Desarrollar el módulo de detección y supresión de información personal identificable, adaptado al contexto lingüístico rioplatense, evaluando su eficacia mediante una prueba piloto que verifique una precisión y recall de referencia >= 0.95 sobre entidades de contacto explícitas.

[OE4] Construir el Gold Standard conformando un panel de tres evaluadores con experiencia en selección de personal, obteniendo etiquetas de idoneidad binaria sobre la muestra de 150 currículums reales de validación externa y verificando el acuerdo inter-evaluador inicial mediante el coeficiente κ de Cohen promedio por pares con un umbral mínimo de 0.70.

[OE5] Ejecutar el estudio comparativo procesando el corpus bajo las cuatro condiciones de procesamiento, registrando para cada candidato el tiempo de procesamiento, el score asignado y la decisión binaria, y asegurando la trazabilidad completa de las variables del diseño.

[OE6] Calcular el Disparate Impact Ratio (DIR) y la Statistical Parity Difference (SPD) para cada condición, desagregando los resultados por género y rango de edad, y contrastar estadísticamente las diferencias entre condiciones.


## Metodología de trabajo

El presente trabajo adopta el proceso estándar para minería de datos CRISP-DM (Cross-Industry Standard Process for Data Mining) como marco metodológico, por ser el estándar más extendido en proyectos de ciencia de datos aplicada y porque su fase de comprensión del negocio permite vincular con naturalidad el desarrollo técnico del sistema con los requisitos operativos de la organización colaboradora; su naturaleza cíclica resulta además especialmente adecuada para el ajuste iterativo de sistemas basados en modelos de lenguaje.

El modelo original contempla seis fases; en el presente trabajo se adopta una versión adaptada de cinco, ajustada al horizonte temporal disponible y a las restricciones del diseño piloto con datos sintéticos. La Figura 4 y la Tabla 4 resume cada fase, sus actividades principales y su correspondencia con los objetivos específicos.


*Figura 4. Adaptación de CRISP-DM al presente trabajo.*

Fuente: Elaboración propia.


*Tabla 4. Desglose fases CRISP-DM.*

Fuente: Elaboración propia, adaptado de Chapman et al. (2000).

Las fases 3 y 4 presentan una dependencia secuencial que constituye el principal riesgo de cronograma: la evaluación no puede iniciarse hasta que el corpus esté generado y validado y los módulos del sistema estén operativos. Esta dependencia se gestiona mediante el control de versiones descrito en la organización del trabajo.


*Tabla 5. Matriz de trazabilidad.*

Fuente: Elaboración propia.


### Marco de métricas de contrastación

La contrastación empírica de las tres hipótesis exige definir con precisión, en esta etapa metodológica, los estimadores y pruebas estadísticas que se aplicarán sobre los datos experimentales; su especificación anticipada evita que la elección de métricas quede condicionada por los resultados observados, garantizando así la validez interna del diseño. Las fórmulas que se presentan a continuación operacionalizan cada hipótesis y constituyen el vínculo formal entre los objetivos específicos del trabajo y los estadísticos que se reportarán en el capítulo de validación experimental.

Métricas de eficiencia

La variable central de la hipótesis de eficiencia es el tiempo de procesamiento por candidato (), cuya distribución empírica presenta asimetría positiva pronunciada que invalida el uso de la media como estimador de tendencia central. Se adopta en su lugar la mediana, calculada sobre el vector ordenado de tiempos :

La dispersión de los tiempos se cuantifica mediante el rango intercuartílico (IQR), estimador robusto ante valores atípicos:

donde y  corresponden al percentil 25 y al percentil 75 de la muestra, respectivamente. El factor de aceleración de cada configuración automática  respecto a la línea base manual  se obtiene como cociente de medianas:

​La significación estadística de la reducción se contrasta mediante la prueba no paramétrica U de Mann-Whitney en su variante unilateral, cuyas hipótesis quedan planteadas como sigue:

donde θ denota la mediana poblacional del tiempo por candidato. Se rechaza  cuando el p-valor resultante es inferior al nivel de significancia fijado globalmente en α = 0.05.

Métricas de eficacia técnica

La eficacia de clasificación se mide sobre la matriz de confusión que define verdaderos positivos (VP), falsos positivos (FP), verdaderos negativos (VN) y falsos negativos (FN). A partir de ella se derivan la precisión y la sensibilidad (recall):

El F₁-score integra ambas en su media armónica; para la evaluación de la hipótesis se emplea el F₁-score macro, que promedia sin ponderar el F₁ de cada clase, lo que lo hace sensible al desempeño en candidatos APTO y NO_APTO por igual con independencia del balance del corpus:

La capacidad discriminativa global del sistema se evalúa mediante el área bajo la curva ROC (AUC-ROC), que mide la probabilidad de que el sistema asigne un score más alto a un candidato APTO que a uno NO_APTO elegidos al azar:

Para estimar la estabilidad del AUC-ROC sin supuestos paramétricos se aplica bootstrapping no paramétrico con B = 1000 remuestreos con reemplazo; el intervalo de confianza al 95 % se obtiene por el método percentil:

donde  es el percentil p-ésimo de la distribución empírica de los estadísticos AUC* recalculados en los remuestreos. La hipótesis de eficacia se acepta únicamente si se satisfacen de forma simultánea los umbrales  ≥ 0.85 y AUC-ROC ≥ 0.90. La validez del Gold Standard que actúa como referencia se verifica mediante el coeficiente κ de Cohen, que descuenta el acuerdo inter-evaluador atribuible al azar:

donde  es la fracción de acuerdo observado y  la probabilidad de acuerdo esperado por azar entre los evaluadores del panel. Se establece κ ≥ 0.70 como umbral mínimo de acuerdo sustancial para validar el etiquetado resultante.

Métricas de equidad algorítmica

La equidad de las decisiones automatizadas se evalúa sobre la tasa de selección de cada grupo demográfico g, definida como la proporción de candidatos del grupo que reciben la etiqueta APTO:

El Disparate Impact Ratio (DIR) expresa el cociente entre la tasa del grupo protegido p (femenino; rango etario bajo evaluación) y la del grupo de referencia r (masculino; grupo más joven):

Un valor DIR ≥ 0.80 se considera libre de impacto dispar adverso según la regla de las cuatro quintas partes de la EEOC (1978), adoptada como umbral regulatorio en el presente trabajo. La Statistical Parity Difference (SPD) complementa el DIR como medida de diferencia absoluta entre tasas:

Un valor SPD = 0 indica paridad estadística perfecta; valores negativos señalan sesgo adverso hacia el grupo protegido y valores positivos indican sesgo en su favor. El rango de aceptación de referencia es [−0.10, 0.10]. La comparación entre C2 y C3 bajo estas dos métricas permite aislar el efecto diferencial del módulo de anonimización de PII sobre el sesgo algorítmico, que es el objeto específico de la hipótesis de equidad
