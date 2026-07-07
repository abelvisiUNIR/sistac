Universidad Internacional de La Rioja

Escuela Superior de Ingeniería y

Tecnología

Máster Universitario en Inteligencia Artificial

Talento sin nombre: anonimización, LLMs y RAG en el cribado curricular


| Trabajo fin de estudio presentado por: | Mario Agustín Belvisi Lescano David Ilich Madrid Oyanadel |
|---|---|
| Tipo de trabajo: | Estudio experimental/comparativo con desarrollo aplicado |
| Director/a: | Marta María Arguedas Lafuente |
| Fecha: | 24/06/2026 |

Resumen

La automatización del cribado curricular mediante modelos de lenguaje de gran escala promete aliviar la sobrecarga operativa de los equipos de selección, pero introduce el riesgo de perpetuar o amplificar los sesgos demográficos presentes en los datos. El presente trabajo evalúa el efecto diferencial de cuatro configuraciones de un sistema de preselección, que incorporan inteligencia artificial de forma progresiva, sobre tres dimensiones del proceso: la eficiencia, la eficacia y la equidad algorítmica. Las configuraciones comparan el cribado manual con un modelo de lenguaje sin contexto, el mismo modelo enriquecido con recuperación aumentada (RAG) y una variante adicional que antepone la anonimización de información personal identificable. La validación se realizó mediante un diseño cuasi-experimental de medidas repetidas sobre un corpus de 150 pares de currículum y descripción de cargo, contrastado contra un Gold Standard validado por un panel experto con una concordancia sustancial (κ de Cohen = 0.76). Los resultados muestran que la automatización reduce el tiempo de preselección de forma masiva respecto al proceso manual (con aceleraciones de entre 33,7× y 147,8× según la configuración) respecto al proceso manual, pero no alcanza los umbrales de eficacia exigidos frente al juicio experto y la anonimización superficial de datos identificadores no mitiga el impacto dispar por género. Se concluye que el sistema resulta valioso como apoyo al cribado primario masivo, siempre que se calibren empíricamente los umbrales de decisión y se mantenga la supervisión humana.

Palabras clave: selección automatizada, fairness algorítmica, procesamiento de lenguaje natural, mitigación de sesgos.

Abstract

The automation of resume screening through large language models promises to ease the operational burden on recruitment teams, but it introduces the risk of perpetuating or amplifying the demographic biases present in the data. This work evaluates the differential effect of four configurations of a candidate pre-screening system, which incorporate artificial intelligence progressively, on three dimensions of the process: efficiency, effectiveness and algorithmic fairness. The configurations compare manual screening with a language model without context, the same model enriched with retrieval-augmented generation (RAG), and an additional variant that adds a prior anonymization step for personally identifiable information. Validation was carried out through a repeated-measures quasi-experimental design over a corpus of 150 resume and job-description pairs, benchmarked against a Gold Standard validated by an expert panel with substantial agreement (Cohen's κ = 0.76). The results show that automation reduces pre-screening time by up to two orders of magnitude relative to the manual process (with accelerations ranging from 33.7× to 147.8×), yet it does not reach the effectiveness thresholds required against expert judgment, and that the superficial anonymization of identifying data does not mitigate disparate impact by gender. The study concludes that the system is valuable as support for large-scale primary screening, provided that decision thresholds are empirically calibrated and human oversight is maintained.

Keywords: automated selection, algorithmic fairness, natural language processing, bias mitigation.

Índice de contenidos

1.	Introducción	1

1.1.	Motivación	1

1.2.	Planteamiento del trabajo	3

1.3.	Estructura del trabajo	5

2.	Estado del arte y fundamentos teóricos	6

2.1.	El proceso de selección y sus limitaciones	7

2.2.	LLMs aplicados a RRHH y ATS inteligentes	8

2.3.	Arquitecturas RAG	9

2.4.	Privacidad de datos e información personal identificable (PII)	11

2.5.	Fairness algorítmica en sistemas de selección	14

2.6.	Marco regulatorio y ético	16

2.7.	Análisis crítico y brecha de investigación	17

2.8.	Conclusiones del estado del arte	19

3.	Objetivos y Metodología	20

3.1.	Objetivo general	20

3.2.	Objetivos específicos	20

3.3.	Metodología de trabajo	21

3.3.1.	Marco de métricas de contrastación	22

4.	Arquitectura e implementación del sistema	26

4.1.	Arquitectura general del sistema	26

4.1.1.	Especificación de requisitos del sistema	29

4.2.	Estrategia de datos	29

4.2.1.	Corpus de desarrollo: dataset sintético calibrado	30

4.2.2.	Corpus de evaluación: dataset público	30

4.2.3.	Protocolo de acuerdo de uso de datos con MATRIZ	32

4.2.4.	Preprocesamiento, chunking e indexación	32

4.3.	Pipeline RAG	33

4.3.1.	Principios de diseño	33

4.3.2.	Modelo de embeddings	35

4.3.3.	Vector store: Google Vertex AI Search	36

4.3.4.	Retrieval híbrido y aislamiento cruzado	36

4.4.	Motor de scoring semántico	39

4.4.1.	Diseño del prompt	39

4.4.2.	Dimensiones de evaluación y pesos	41

4.4.3.	Umbral de decisión y output	41

4.5.	Módulo de anonimización PII	43

4.5.1.	Stack tecnológico: Presidio + spaCy	44

4.5.2.	Entidades detectadas y estrategia de sustitución	44

4.5.3.	Validación del módulo y alcance de la Anonimización	46

4.6.	Stack técnico consolidado	47

4.7.	Dificultades técnicas y soluciones implementadas	47

4.8.	Síntesis del capítulo	50

5.	Validación experimental y resultados	50

5.1.	Diseño del experimento	51

5.2.	Protocolo del Gold Standard	52

5.3.	Métricas de evaluación	54

5.3.1.	Hipótesis sobre la eficiencia	54

5.3.2.	Hipótesis sobre la eficacia técnica	54

5.3.3.	Hipótesis sobre la equidad algorítmica	55

5.4.	Suite estadística para las tres hipótesis	55

5.5.	Gestión de datos y reproducibilidad	56

5.6.	Resultados de eficiencia	57

5.7.	Resultados de eficacia técnica	58

5.8.	Resultados de equidad algorítmica	62

5.9.	Resumen integrado de resultados	66

5.10.	Análisis de costo y latencia operativa	67

5.11.	Análisis de robustez: réplica con modelo alternativo	68

6.	Discusión y conclusiones	71

6.1.	Discusión de los resultados	71

6.1.1.	Discusión de la eficiencia: reducción del tiempo de preselección	71

6.1.2.	Discusión de la eficacia técnica: alcance del umbral	72

6.1.3.	Discusión de la equidad: efecto de la anonimización sobre los sesgos	74

6.1.4.	Limitaciones del estudio	75

6.2.	Conclusiones	76

6.2.1.	Respuesta a la pregunta de investigación	76

6.2.2.	Matriz de cumplimiento de objetivos específicos	77

6.2.3.	Conclusiones por hipótesis	77

6.3.	Recomendaciones prácticas e institucionales para la organización Matriz	78

6.4.	Contribuciones del trabajo	79

6.5.	Limitaciones del estudio y trabajo futuro	79

Referencias bibliográficas	81

Anexo A.	Repositorio	86

Anexo B.	Tabla módulo	87

Anexo C.	Pantallas de la aplicación	87

Anexo D.	Estructura del índice vectorial	88

Índice de figuras


*Figura 1.  Mapa temático del estado del arte en cribado curricular con inteligencia artificial.	7*


*Figura 2. Tipologías de arquitecturas RAG aplicadas al cribado curricular: flujo base y variantes según complejidad de recuperación.	11*


*Figura 3. Flujo de detección y supresión de información personal identificable en texto curricular mediante spaCy y Microsoft Presidio.	13*


*Figura 4. Adaptación de CRISP-DM al presente trabajo.	22*


*Figura 5. Arquitectura general del sistema con sus cuatro módulos funcionales.	28*


*Figura 6. Flujo de preparación y validación del corpus de currículums.	31*


*Figura 7. Estrategia de extracción de texto según formato de archivo.	33*


*Figura 8. Principios de diseño del pipeline RAG y su relación con los componentes del sistema.	34*


*Figura 9. Proceso de vectorización de un fragmento de currículum y almacenamiento en el índice.	35*


*Figura 10. Mecanismo de retrieval híbrido con aislamiento cruzado por par CV-JD.	38*


*Figura 11. Flujo completo del pipeline RAG: fases de indexación y evaluación.	38*


*Figura 12. Estructura del output JSON del motor de scoring: score global, scores por dimensión, decisión binaria y justificación.	42*


*Figura 13. Arquitectura del motor de scoring LLM con cuatro dimensiones ponderadas.	43*


*Figura 14. Posición del módulo PII en el pipeline: opera antes del chunking y el retrieval.	44*


*Figura 15. Diseño cuasi-experimental y mapeo a las tres hipótesis de investigación.	52*


*Figura 16. Protocolo de conformación del Gold Standard por el panel de Matriz.	54*


*Figura 17. Linaje de datos del experimento, del corpus a las tablas de resultados.	56*


*Figura 18. Distribución de  por configuración en escala logarítmica, con factor de aceleración anotado sobre cada caja.	58*


*Figura 19. Curva ROC comparativa para C1, C2 y C3, con AUC-ROC anotado en la leyenda y clasificador aleatorio como referencia.	61*

La Figura 20. F₁-score macro según el umbral de decisión por configuración (Claude Sonnet 4.5)	62


*Figura 21. DIR por género en C2 y C3 con umbral de equidad EEOC (0.80) como referencia visual.	65*


*Figura 22. Disparate Impact Ratio por género con intervalos de confianza (bootstrap, 1000 remuestreos).	65*


*Figura 23. Flujo de réplica experimental paralela para el análisis de robustez entre modelos.	69*


*Figura 24. Evaluaciones válidas por configuración en la réplica con Gemini 2.5 Flash.	71*

Índice de tablas


*Tabla 1. Organización del trabajo en grupo.	XII*


*Tabla 2. Síntesis de la literatura relevante para el presente trabajo.	18*


*Tabla 3. Síntesis de las brechas de investigación identificadas.	19*


*Tabla 4. Desglose fases CRISP-DM.	22*


*Tabla 5. Matriz de trazabilidad.	22*


*Tabla 6. Especificación de requisitos funcionales y no funcionales del sistema.	29*


*Tabla 7. Caracterización del corpus de evaluación del software.	32*


*Tabla 8. Dimensiones de evaluación del motor de scoring y sus pesos.	41*


*Tabla 9. Entidades PII detectadas y estrategia de sustitución en el módulo de anonimización.	45*


*Tabla 10. Métricas de validación del módulo de anonimización (OE3).	47*


*Tabla 11. Stack técnico por capa funcional.	47*


*Tabla 12. Dificultades técnicas encontradas durante la implementación y soluciones aplicadas.	49*


*Tabla 13. Matriz de concordancia inter-evaluador inicial (OE4).	53*


*Tabla 14. Aparato estadístico por hipótesis.	55*


*Tabla 15. Controles de reproducibilidad del experimento.	56*


*Tabla 16. Métricas de eficiencia por configuración.	57*


*Tabla 17. Métricas de eficacia frente al Gold Standard(H2).	59*


*Tabla 18. Eficacia con umbral de decisión calibrado (Claude Sonnet 4.5).	60*


*Tabla 19. Métricas RAGAS de la evaluación técnica del pipeline (C2).	60*


*Tabla 20. Comparativa de eficacia con umbral base vs. umbral optimizado (H2 / OE5).	60*


*Tabla 21. Métricas de equidad por género (H3).	62*


*Tabla 22. Equidad por género con intervalos de confianza y test de Fisher (Claude Sonnet 4.5).	63*


*Tabla 23. Métricas de equidad por rango de edad (H3).	63*


*Tabla 24. Resumen integrado de métricas por configuración.	66*


*Tabla 25. Matriz de cumplimiento de hipótesis de la investigación.	66*


*Tabla 26. Latencia medida y costo estimado por candidato según configuración.	67*


*Tabla 27. Análisis de robustez: comparativa de resultados entre Claude Sonnet 4.5 y Gemini 2.5 Flash.	69*


*Tabla 28. Matriz de cumplimiento de objetivos específicos de la investigación.	77*

Organización del trabajo en grupo

Este apartado describe cómo se dividió el trabajo entre los dos integrantes del grupo, qué objetivos de aprendizaje se persiguieron con esa división y qué herramientas se usaron para coordinarse a lo largo del desarrollo.

Partes que aborda el trabajo

El trabajo se estructuró en partes suficientemente diferenciadas como para que cada integrante pudiera profundizar en una línea propia sin perder de vista el conjunto. La mayor parte de los capítulos se elaboró de forma conjunta, con procesos de revisión cruzada y ajuste mutuo; sin embargo, en la fase de desarrollo técnico se estableció una división más clara: David Ilich Madrid Oyanadel se concentró en el pipeline de recuperación aumentada con generación y el motor de scoring semántico, mientras que Mario Agustín Belvisi Lescano asumió el módulo de anonimización de datos personales y el análisis de equidad algorítmica. Esta división permitió que cada integrante aportara profundidad en su área sin sacrificar la coherencia del trabajo como un todo. La distribución completa por sección se recoge en la tabla 1. Dicha distribución fue revisada y avalada por la dirección del Trabajo Fin de Estudios antes del inicio de su desarrollo.


*Tabla 1. Organización del trabajo en grupo.*

Fuente: Elaboración propia.

Objetivo del trabajo desde el punto de vista de la adquisición de conocimientos

Cada una de las partes que integran el trabajo habría podido constituir, por sí sola, el tema de una propuesta individual; lo que le da sentido grupal es precisamente que la combinación de esas partes genera un resultado más completo de lo que cualquiera de los dos integrantes podría haber alcanzado por separado. La elaboración del trabajo permitió poner en práctica competencias del Máster en Inteligencia Artificial y Data Science que van desde el diseño experimental y la estadística inferencial hasta la ingeniería de sistemas basados en modelos de lenguaje y el tratamiento responsable de datos personales, integrando en un único proyecto dimensiones que habitualmente se estudian por separado. Esta complementariedad es, en definitiva, lo que justifica el carácter grupal del trabajo y lo que le otorga relevancia no solo académica sino también práctica.

Mecanismos de coordinación empleados

La coordinación entre los dos integrantes se sostuvo sobre cuatro canales principales: mensajería instantánea para el intercambio diario, videollamadas semanales de seguimiento del avance, un repositorio con control de versiones para la integración del código y almacenamiento compartido en la nube para la gestión de la memoria y los documentos del proyecto.
