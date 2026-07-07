# Ampliaciones de cuerpo | 23/06/2026

Dos bloques para sumar páginas de cuerpo con contenido sustantivo. Voz impersonal, punto decimal, sin guiones largos. Indican dónde insertarse.

---

## AMPLIACIÓN 1 — Profundización del diseño del prompt (Capítulo 4)

> Ubicación: ampliar la subsección **4.4 Motor de scoring semántico → Diseño del prompt**, a continuación de la descripción actual del prompt y antes de las dimensiones de evaluación.

El diseño del prompt persigue tres objetivos simultáneos que condicionan su estructura: garantizar la comparabilidad entre configuraciones, producir una salida verificable y aislar el efecto de la recuperación semántica. La comparabilidad se asegura manteniendo un mismo prompt de sistema en todas las configuraciones automatizadas, de modo que el único elemento que varía entre ellas sea la información que recibe el modelo (el currículum completo frente a los fragmentos recuperados) y no la instrucción que gobierna su comportamiento. Este control es la base de la validez interna del experimento: cualquier diferencia de desempeño entre configuraciones puede atribuirse al componente que se activa o desactiva, y no a una variación en la formulación de la tarea.

La salida verificable se logra obligando al modelo a responder exclusivamente con un objeto estructurado en formato JSON, sin texto libre adicional. Esta restricción cumple una función metodológica que excede la mera conveniencia técnica: convierte la respuesta del modelo en un dato estructurado, directamente convertible en las métricas de clasificación sin pasos de interpretación manual que introducirían subjetividad o error. La instrucción se refuerza con una temperatura de muestreo igual a cero, que elimina la aleatoriedad de la generación y garantiza que dos evaluaciones del mismo par currículum-cargo produzcan idéntico resultado, condición indispensable para la reproducibilidad de las métricas. Dado que el modelo ocasionalmente envuelve la respuesta en delimitadores de bloque o agrega texto explicativo, el sistema incorpora una rutina de saneamiento que recupera el objeto estructurado ante fallos de formato, lo que reduce la tasa de error de lectura por debajo del dos por ciento.

El aislamiento del efecto de la recuperación se materializa en la diferencia entre los dos diseños de prompt para el usuario. En la configuración sin recuperación, el modelo recibe el currículum completo y evalúa con base en toda la información disponible, apoyándose en su capacidad de síntesis. En las configuraciones con recuperación, el currículum completo se sustituye por los cinco fragmentos más relevantes y la instrucción cambia de forma deliberada: se ordena al modelo evaluar únicamente con base en la evidencia presente en esos fragmentos, sin inferir información ausente. Cuando un criterio no puede valorarse por falta de evidencia, se asigna un valor neutro intermedio en lugar de penalizar o premiar al candidato, decisión que evita que la ausencia de un fragmento se confunda con una deficiencia del perfil. Esta restricción al contexto recuperado es la que permite atribuir las diferencias de eficacia entre configuraciones al mecanismo de recuperación y no a la información adicional que el modelo pudiera aportar desde su conocimiento paramétrico.

La trazabilidad de la decisión se refuerza con un campo de salida específico de las configuraciones con recuperación, que registra qué dimensiones del perfil no pudieron evaluarse por ausencia de evidencia en los fragmentos. Este registro convierte una limitación potencial de la arquitectura, la pérdida de información por el truncamiento del contexto, en un dato auditable que documenta los límites de cada evaluación y habilita su revisión posterior por parte de un analista humano.

---

## AMPLIACIÓN 2 — Análisis de costo y latencia operativa (Capítulo 5)

> Ubicación: nueva subsección al final del Capítulo 5, después de **5.9 Resumen integrado de resultados** (o como **5.9.x**), antes del análisis de robustez.

Más allá de la significación estadística de la reducción de tiempos, la viabilidad de adoptar el sistema en una organización depende de su costo operativo por candidato y de la latencia efectiva de cada evaluación. Esta subsección traduce los resultados de eficiencia a magnitudes operativas directas: el tiempo de procesamiento medido y el costo económico estimado de cada configuración automática.

La latencia se midió de forma directa sobre cada evaluación. Con el modelo principal, la mediana del tiempo de procesamiento por candidato fue de 4.5 segundos sin recuperación, 6.8 segundos con recuperación y 19.6 segundos con recuperación y anonimización. El incremento que aporta la recuperación semántica es modesto (del orden de 2.3 segundos, atribuible a la generación del vector de consulta y a la búsqueda en el almacén vectorial), mientras que el mayor incremento corresponde a la anonimización (del orden de 12.8 segundos), que se ejecuta localmente sobre la unidad de procesamiento y depende del análisis lingüístico del texto. Aun en la configuración más costosa, el tiempo por candidato se mantiene en el orden de los segundos, frente a una mediana de 661.8 segundos de la revisión manual.

El costo económico se estima a partir de los precios públicos de las interfaces de programación de los modelos (vigentes a junio de 2026: tres y quince dólares por millón de tokens de entrada y de salida para el modelo principal; treinta centavos y dos dólares con cincuenta por millón para el modelo de la réplica) y del tamaño aproximado de los prompts: una entrada del orden de mil quinientos tokens en la configuración sin recuperación y de tres mil doscientos tokens en las configuraciones con recuperación (por la incorporación de los cinco fragmentos), y una salida acotada por el límite de mil veinticuatro tokens, estimada en torno a cuatrocientos tokens por respuesta. La Tabla X resume la estimación.

**Tabla X. Latencia medida y costo estimado por candidato según configuración.**

| Configuración  | Latencia mediana (s) | Costo estimado/candidato (modelo principal) | Costo estimado/candidato (modelo réplica) |
| ----------------| ----------------------| ---------------------------------------------| -------------------------------------------|
| C1 (LLM puro)  | 4.5                  | ≈ 0.011 USD                                 | ≈ 0.0015 USD                              |
| C2 (LLM + RAG) | 6.8                  | ≈ 0.016 USD                                 | ≈ 0.002 USD                               |
| C3 (RAG + PII) | 19.6                 | ≈ 0.016 USD                                 | ≈ 0.002 USD                               |

*Nota. El costo es una estimación basada en el tamaño aproximado de los prompts y en las tarifas públicas vigentes a junio de 2026; el sistema no registra el conteo exacto de tokens por evaluación. La anonimización se ejecuta de forma local y no añade costo de interfaz; el almacén vectorial factura por consulta con un costo marginal frente al del modelo de lenguaje. Fuente: elaboración propia.*

La lectura operativa de estas cifras es contundente. Procesar mil candidaturas con la configuración de recuperación tendría un costo estimado del orden de dieciséis dólares con el modelo principal y de dos dólares con el modelo de la réplica, frente a las más de ciento ochenta horas de trabajo humano que implicaría su revisión manual a la mediana observada. El costo marginal de añadir la capa de anonimización es nulo en términos económicos, ya que se ejecuta localmente, y su único precio es un incremento de latencia que, en un procesamiento por lotes, resulta irrelevante para el flujo de trabajo de la organización. En conjunto, el análisis confirma que la barrera para adoptar el sistema no es económica ni de rendimiento, sino la calidad de la decisión y las garantías de equidad analizadas en las secciones anteriores.
