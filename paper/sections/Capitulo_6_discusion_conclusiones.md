# Discusión y conclusiones

El presente capítulo interpreta los resultados experimentales obtenidos en el Capítulo 5 y establece el cierre del trabajo de investigación. En la primera sección, se discuten los hallazgos relativos a las tres hipótesis de eficiencia, eficacia técnica y equidad algorítmica, comparando el comportamiento de los modelos evaluados y detallando las limitaciones metodológicas del estudio. En la segunda sección, se responde a la pregunta de investigación, se exponen las conclusiones específicas por hipótesis, se detallan las contribuciones técnicas del proyecto y se proponen las líneas de trabajo futuro.


## Discusión de los resultados


### Discusión de la eficiencia: reducción del tiempo de preselección

La evidencia experimental de eficiencia indica que las tres configuraciones automáticas (C1, C2 y C3) logran una reducción drástica del tiempo de preselección por candidato respecto a la línea base manual de C0. Mientras el panel de expertos de MATRIZ requirió una mediana de 661.8 segundos por candidato, los sistemas automatizados basados en el modelo de lenguaje de Anthropic completaron las tareas en 4.5 segundos (C1), 6.8 segundos (C2) y 19.6 segundos (C3). Esto representa factores de aceleración de 147.8×, 96.7× y 33.7× respectivamente, con un p-valor inferior a 0.0001 que rechaza formalmente la hipótesis nula de eficiencia.

El análisis de los sobrecostos de latencia entre configuraciones automáticas revela que la recuperación semántica (C2) añade una media de 2.3 segundos debido a la generación de embeddings locales y al proceso de consulta al servicio en Google Vertex AI Search. Por otro lado, la incorporación del enmascaramiento de datos sensibles (C3) añade un retraso adicional de 12.8 segundos. Este sobrecosto se debe a la ejecución local en CPU del reconocedor lingüístico SistacAnonymizer (que integra reglas de procesamiento de lenguaje natural de spaCy y el motor Microsoft Presidio). A pesar de este incremento en la latencia, el tiempo acumulado de 19.6 segundos en C3 sigue representando una ganancia masiva de eficiencia frente a la revisión manual.

La réplica paralela de robustez ejecutada con Gemini 2.5 Flash de Google sustenta la generalización de la hipótesis de eficiencia. Aunque Gemini exhibe latencias absolutas superiores en inferencia pura (21.6s en C1, 24.6s en C2 y 28.9s en C3), lo que representa factores de aceleración menores (de 30.6× a 22.9×), la reducción del tiempo respecto al proceso humano sigue siendo altamente significativa desde el punto de vista estadístico (p < 0.0001). La diferencia de velocidad entre proveedores (siendo Claude entre 3 y 4 veces más rápido) se atribuye a las optimizaciones de procesamiento en la API de Anthropic y a una menor latencia de transferencia de red durante el scoring de texto. Para una organización como MATRIZ, el uso de cualquiera de las configuraciones automáticas transforma el cuello de botella del screening primario, convirtiendo horas de revisión manual acumuladas en pocos minutos de procesamiento por lote.


### Discusión de la eficacia técnica: alcance del umbral

La eficacia predictiva de las configuraciones frente al Gold Standard humano no alcanzó los umbrales exigidos para la aceptación de la hipótesis de eficacia (F₁-score macro ≥ 0.85 y AUC-ROC ≥ 0.90), por lo que la hipótesis fue rechazada. En el modelo Claude Sonnet 4.5, el F₁-score macro fue de 0.565 en C1, 0.519 en C2 y 0.539 en C3, mientras que el AUC-ROC se mantuvo estable entre 0.729 y 0.735.

La caída de -0.046 puntos en el F₁-score al pasar de la condición sin recuperación (C1) a la de recuperación aumentada (C2) se explica por el efecto de truncamiento del contexto inherente a la arquitectura RAG. Al dividir el currículum del postulante en fragmentos y seleccionar únicamente los 5 bloques con mayor similitud vectorial con la descripción de cargo, el sistema puede omitir datos dispersos en el currículum (como menciones breves a tecnologías o roles pasados) que un análisis humano (o del modelo sobre el currículum completo en C1) sí detectaría.

Sin embargo, el análisis de robustez con Gemini 2.5 Flash revela un comportamiento diferente. En Gemini, la anonimización de PII en C3 actuó como un filtro de ruido conceptual de gran efectividad, elevando el F₁-score macro de 0.494 (C2) a 0.587 (C3) y el AUC-ROC de 0.629 a 0.695. Este hallazgo demuestra que modelos con menor capacidad paramétrica que Claude se benefician de forma sustancial al remover nombres, correos o datos de contacto en el prompt, lo que les permite concentrar su atención atencional exclusivamente en las competencias técnicas y en la trayectoria del postulante.

Para profundizar en la causa de la brecha respecto al umbral de 0.85 de F₁-score macro, se analizó la matriz de confusión detallada del modelo Claude. En la configuración C1, el sistema clasificó correctamente a 71 de los 75 candidatos no aptos (verdaderos negativos, mostrando una alta especificidad del 94.7%), registrando únicamente 4 falsas alarmas (falsos positivos). Sin embargo, el modelo clasificó erróneamente como no aptos a 54 de los 75 candidatos aptos (falsos negativos, resultando en una sensibilidad baja de 28.0%). Este patrón se repite en C2 y C3, con falsos negativos de 56 y 55 respectivamente.

Este comportamiento demuestra que el modelo es sumamente estricto y conservador cuando evalúa la adecuación curricular. El mantenimiento de valores elevados de AUC-ROC (~0.73) confirma que el sistema ordena y jerarquiza a los candidatos de forma adecuada según su nivel de competencia, lo que denota una buena capacidad de ranking (útil para priorizar candidatos). Sin embargo, el F₁-score macro absoluto queda lejos de los benchmarks de referencia previos en inglés ((Bevara et al., 2025);(Liu, 2025)), donde se reportan F₁-scores superiores a 0.85. Esta distancia se atribuye al proceso de localización y traducción del corpus al español rioplatense (que introduce distorsiones semánticas sutiles), a la rigurosidad extrema en la evaluación de idoneidad del panel experto de Matriz, y a la baja sensibilidad (recall) de solo 28.0% provocada por el umbral rígido original de 70 puntos, el cual es excesivo para la escala de scores generada por el LLM. Al recalibrar el umbral al punto óptimo obtenido por Youden (umbrales entre 34 y 48 puntos), el F₁-score asciende de forma muy significativa hasta alcanzar un valor de 0.697 (C1), 0.693 (C2) y 0.691 (C3), evidenciando que la brecha de eficacia responde a la calibración del punto de corte binario fijo y no a una falta de capacidad discriminativa del modelo.

La descomposición del resultado por umbral de decisión matiza la lectura de la eficacia. Con el corte fijado en 70 puntos, el sistema aparenta un F₁ macro en torno a 0.52–0.57, pero ese valor está dominado por una sensibilidad baja derivada de un umbral demasiado exigente para la escala de scores del modelo. Al calibrar el punto de corte, el F₁ asciende a aproximadamente 0.70, lo que reconcilia el desempeño con el AUC-ROC observado (~0.73) e indica que la limitación es de calibración y no de capacidad de ordenamiento. La eficacia, por tanto, no se alcanza en términos absolutos, pero su margen de mejora reside en una decisión de diseño corregible.


### Discusión de la equidad: efecto de la anonimización sobre los sesgos

Los resultados sobre la mitigación de sesgos de género deben interpretarse a la luz de su significación estadística. En el modelo Claude, el índice de impacto dispar (DIR) por género pasó de 0.602 en C2 (sin anonimizar) a 0.301 en C3 (anonimizado), y en Gemini de 1.397 a 0.447. Sin embargo, como se mostró en la sección de resultados, ninguna de estas diferencias alcanza significación estadística: la prueba exacta de Fisher resulta no significativa en todas las configuraciones y los intervalos de confianza por bootstrap incluyen el valor de paridad. Por tanto, la variación observada no puede interpretarse como un efecto real de la anonimización sobre la equidad, sino como fluctuación esperable en un subgrupo protegido muy reducido.

La aparente variación del DIR entre configuraciones, no significativa en términos estadísticos, resulta consistente con dos factores complementarios:

* La persistencia de señales indirectas y variables proxies de género: El módulo de anonimización enmascara nombres propios y datos de contacto directos, pero preserva la sintaxis y construcciones gramaticales de origen. En el idioma español, la flexión de género en adjetivos y sustantivos (por ejemplo, redactora, ingeniera, graduado, programadora) sigue indicando de forma implícita el género del postulante, permitiendo al LLM inferir esta variable. A esto se suma el sesgo indirecto introducido por variables proxies que no son de carácter personal pero están altamente correlacionadas con el género, tales como brechas temporales en la trayectoria laboral asociadas históricamente al cuidado familiar, nombres de colegios o instituciones educativas históricamente segregadas por género, y la naturaleza de la experiencia previa en roles ocupacionales con sesgos de distribución demográfica tradicionales en el mercado local (por ejemplo, soporte administrativo frente a desarrollo de infraestructura técnica). El modelo conserva la capacidad de asociar semánticamente estos patrones contextuales indirectos, perpetuando el sesgo en el score final.
* La sensibilidad estadística al tamaño muestral: El análisis de los recuentos absolutos del corpus revela que el subconjunto de candidatos del género femenino cuenta únicamente con 17 representantes (11.3% del corpus de 150 CVs), en comparación con 133 candidatos masculinos. En muestras pequeñas de grupos protegidos, el DIR (que opera como un cociente de tasas) presenta una alta inestabilidad estadística. En la ejecución de Claude, la tasa de selección del grupo femenino en C2 fue del 11.8% (2 de 17 candidatas), mientras que en C3 cayó al 5.9% (1 de 17 candidatas). El cambio de decisión sobre una sola candidata redujo a la mitad el DIR, evidenciando que la métrica en este volumen de datos es altamente sensible a variaciones menores y debe interpretarse con cautela.
En el análisis por rango de edad, el grupo de edad avanzada (46-58 años) en Claude se mantuvo en un DIR de 0.818 en C2 y C3, y en Gemini pasó de 0.667 a 0.857 tras la anonimización. No obstante, los intervalos de confianza de estas estimaciones son igualmente amplios y las diferencias no resultan significativas, por lo que la aparente mejora de la objetividad etaria en perfiles senior debe tomarse como indicio exploratorio y no como un efecto demostrado.


### Limitaciones del estudio

Los resultados obtenidos deben interpretarse considerando cuatro limitaciones metodológicas del diseño experimental:

* Origen y traducción del corpus: El corpus se construyó a partir del dataset público netsol/resume-score-details de Hugging Face. Aunque los documentos fueron traducidos y localizados al español rioplatense mediante traducción automática y revisión, no corresponden a currículums presentados de forma espontánea por postulantes locales en MATRIZ, lo que limita la validez externa del experimento.
* Inferencia e imputación de variables demográficas: Ante la ausencia de datos demográficos explícitos en los currículums de origen público, la variable de género debió ser inferida por el modelo a partir de los nombres de pila, y los rangos de edad debieron ser imputados de forma uniforme (50 candidatos por rango). Esta clasificación indirecta puede contener errores e inconsistencias que afectan a la exactitud de las métricas de equidad.
* Imputación de tiempos en la línea base (C0): Si bien los tiempos de la condición C0 para la totalidad del corpus se estimaron mediante imputación estadística para evitar sobrecargar al panel durante 25 horas operativas, dicha imputación no se basó en supuestos arbitrarios, sino que fue calibrada a partir de los tiempos de lectura individuales reales cronometrados mediante el módulo integrado en la aplicación sobre una muestra piloto de 25 currículums. De este modo, aunque el speedup del estudio general incluye un componente de simulación a escala, los parámetros de base provienen de mediciones de productividad física reales sobre la interfaz de trabajo.
* Tamaño del panel y del corpus de evaluación: La conformación de un panel experto de tres profesionales de selección de personal y un corpus de 150 candidatos constituye un volumen apropiado para un estudio de validación de sistema, pero es limitado para inferir generalizaciones definitivas sobre el comportamiento de los sesgos algorítmicos.
* Potencia estadística en el análisis de equidad: el subgrupo femenino (n = 17) es demasiado pequeño para estimar el DIR con precisión; las conclusiones de equidad por género deben considerarse exploratorias.
* Completitud de la réplica de robustez: el modelo alternativo (Gemini 2.5 Flash) no produjo un score válido en hasta un tercio de los casos de C2, por lo que su comparación con el evaluador principal no es plenamente simétrica.

## Conclusiones


### Respuesta a la pregunta de investigación

La investigación planteada buscaba determinar el efecto de cuatro configuraciones experimentales de cribado (desde el proceso humano hasta sistemas automáticos con RAG y anonimización de datos) sobre la eficiencia operativa, la eficacia predictiva y la equidad algorítmica por género y edad.

La evidencia empírica acumulada permite concluir que la automatización mediante modelos de lenguaje transforma la eficiencia operativa del proceso de reclutamiento, reduciendo los tiempos por candidato en hasta dos órdenes de magnitud (logrando procesar en segundos lo que a un humano le toma más de diez minutos). Sin embargo, este incremento masivo en la eficiencia introduce un dilema de diseño (trade-off) técnico:

* La eficacia de los modelos fundacionales (F₁ macro ~0.52-0.58) se mantiene moderada frente al juicio experto del panel, debido al carácter conservador de la evaluación automática y a la pérdida de contexto inducida por el truncamiento en el RAG.
* La mitigación de sesgos mediante anonimización de PII directas no garantiza la eliminación del impacto dispar por género (DIR < 0.80), aunque muestra resultados positivos para mitigar la disparidad por edad en perfiles senior.
Como conclusión general para la organización MATRIZ, el sistema (especialmente en su configuración RAG C2 o anonimizada C3) no debe emplearse de forma autónoma en fases de decisión críticas, pero constituye un excelente instrumento de apoyo a la decisión en fases de cribado primario masivo, siempre que se calibren los umbrales numéricos de descarte de forma empírica.


### Matriz de cumplimiento de objetivos específicos

Para contrastar el grado de éxito de la investigación, la Tabla 28 presenta la matriz de cumplimiento metodológico, enlazando cada uno de los objetivos específicos definidos en el Capítulo 3 con su resultado empírico y su conclusión asociada.


*Tabla 28. Matriz de cumplimiento de objetivos específicos de la investigación.*

Fuente: Elaboración propia.


### Conclusiones por hipótesis

* Hipótesis de eficiencia: se acepta. El sistema de preselección automática es significativamente más rápido que el screening manual humano en todas las configuraciones evaluadas (p < 0.0001, con factores de aceleración de 147.8× en C1, 96.7× en C2 y 33.7× en C3 para el modelo principal Claude).
* Hipótesis de eficacia: se rechaza. Las configuraciones automáticas basadas en recuperación semántica (C2 y C3) no lograron alcanzar el umbral de aceptación del F₁-score macro ≥ 0.85 frente al Gold Standard experto (registrando un F₁ de 0.519 en C2 y 0.539 en C3). Se concluye que el sistema es un valioso asistente de priorización y ordenamiento (ranking) para agilizar la lectura, pero no es viable como decisor binario autónomo bajo cortes fijos.
* Hipótesis de equidad: se rechaza. La anonimización de PII directas (C3) no mitigó de forma efectiva el impacto dispar por género respecto a las configuraciones no anonimizadas, reduciendo el DIR por género de 0.602 (C2) a 0.301 (C3), debido a la persistencia de variables proxies de género. Esto subraya que la supresión de datos identificadores de contacto directos es insuficiente para neutralizar el sesgo indirecto semántico.

## Recomendaciones prácticas e institucionales para la organización Matriz

A partir de las limitaciones observadas y el comportamiento empírico del sistema, se proponen cuatro recomendaciones institucionales para la implementación de modelos de lenguaje en sus procesos de adquisición de talento:

* Prohibición de descarte algorítmico autónomo: El software no debe emplearse como un filtro de exclusión automática (automatic rejection) debido a su bajo desempeño binario en umbrales prefijados.
* Uso complementario en ranking asistido: Se recomienda utilizar los scores numéricos generados únicamente como criterio complementario de ordenamiento para agilizar la lectura secuencial de perfiles por parte de los selectores humanos.
* Calibración dinámica de umbrales Youden: La organización debe evitar el uso de puntos de corte rígidos (como el umbral de 70 puntos) y calibrar empíricamente los umbrales de decisión de forma adaptativa para cada cargo o vacante específica.
* Logs y auditorías periódicas de sesgo: Registrar las puntuaciones y decisiones automatizadas en bases de datos con control de accesos para realizar auditorías semestrales de impacto dispar (DIR) que controlen la deriva algorítmica.

## Contribuciones del trabajo

El proyecto aporta cuatro contribuciones científicas e ingenieriles en el campo de la inteligencia artificial aplicada a la gestión de personas:

* Un marco metodológico controlado y replicable: Un diseño de medidas repetidas en lote que compara sistemáticamente cuatro niveles de automatización, aislando experimentalmente el aporte individual del componente RAG y de la anonimización de datos.
* Un pipeline de anonimización adaptado al contexto rioplatense: La implementación de SistacAnonymizer, que integra reconocedores específicos en español rioplatense (DNI, NIE, nombres comunes y términos locales) para procesar datos curriculares localmente cumpliendo con los estándares de privacidad de la Ley 18.331 de Uruguay.
* Un protocolo de Gold Standard profesional: Un procedimiento calibrado de anotación inter-evaluador de tres expertos en recursos humanos con un índice de concordancia cuantitativo verificado (κ = 0.76), que sirve como base empírica confiable para auditorías algorítmicas.
* Evidencia empírica sobre trade-offs en modelos de lenguaje: Datos concretos sobre las discrepancias en el desempeño y comportamiento de sesgos entre proveedores de IA (Claude vs. Gemini) en tareas de reclutamiento bajo el idioma español, enriqueciendo la literatura científica regional sobre la equidad algorítmica.

## Limitaciones del estudio y trabajo futuro

El desarrollo del sistema abre cinco líneas de investigación y desarrollo técnico para futuros trabajos:

* Validación con currículums y vacantes locales reales: Sustituir el corpus de origen público por currículums reales e históricos de candidatos de MATRIZ, previa obtención del consentimiento informado y de las salvaguardas de seguridad exigidas por la Unidad de Regulación y Control de Datos Personales de Uruguay.
* Ampliación y balanceo del corpus de evaluación: Diseñar un corpus experimental ampliado que incorpore una mayor cantidad de candidatas femeninas (corrigiendo la limitación de n=17) y una variedad más amplia de perfiles funcionales (como administración, finanzas y operaciones) y niveles de antigüedad profesional.
* Implementación de embeddings y re-ranking contextuales: Evaluar el uso de modelos de embeddings locales ajustados sobre textos profesionales en español, e incorporar una etapa de reordenamiento dinámico (re-ranking) basado en criterios ad-hoc para flexibilizar la recuperación de información.
* Explicabilidad interactiva para el analista: Incorporar interfaces que expliquen visualmente al selector de recursos humanos el origen de la puntuación de afinidad asignada por el sistema (por ejemplo, resaltando los chunks del currículum que justifican la decisión).
* Mitigación profunda del sesgo de género implícito: Desarrollar algoritmos de anonimización lingüística profunda que actúen sobre la concordancia de género en español, neutralizando adjetivos y términos marcados sin deteriorar la coherencia sintáctica del currículum.
Referencias bibliográficas

Abhishek, K. L., Niranjanamurthy, M., Aric, S., Ansarullah, S. I., Sinha, A., Tejani, G., & Shah, M. A. (2025). Developing an Intelligent Resume Screening Tool With AI-Driven Analysis and Recommendation Features. Applied AI Letters, 6(2), e116. https://doi.org/10.1002/ail2.116

Afzal, A., Subedi, I., & Matthes, F. (2025). Candidate Profile Summarization: A RAG Approach with Synthetic Data Generation for Tech Jobs. En G. Angelova, M. Kunilovskaya, M. Escribe, & R. Mitkov (Eds.), Proceedings of the 15th International Conference on Recent Advances in Natural Language Processing—Natural Language Processing in the Generative AI Era (pp. 22-31). INCOMA Ltd., Shoumen, Bulgaria. https://aclanthology.org/2025.ranlp-1.3/

Albaroudi, E., Mansouri, T., Hatamleh, M., & Alameer, A. (2025). Addressing intersectional bias in AI recruitment using HITHIRE model: A fair, ethical, green AI and transparent hiring solution for Saudi Arabia’s diverse workforce in line with vision 2030. AI and Ethics, 6(1), 57. https://doi.org/10.1007/s43681-025-00844-z

An, J., Huang, D., Lin, C., & Tai, M. (2025). Measuring gender and racial biases in large language models: Intersectional evidence from automated resume evaluation. PNAS Nexus, 4(3), pgaf089. https://doi.org/10.1093/pnasnexus/pgaf089

Bangura, S., Duma, P., Ntombifuthi, & Mthembu, A. (2025). Ethical considerations of implementing Artificial Intelligence in Human Resource Management: A review. International Journal of Business Ecosystem & Strategy (2687-2293), 7, 274-281. https://doi.org/10.36096/ijbes.v7i5.986

Bevara, R. V., Mannuru, N. R., Karedla, S. P., Lund, B., Xiao, T., Pasem, H., Dronavalli, S. C., & Rupeshkumar, S. (2025). Resume2Vec: Transforming Applicant Tracking Systems with Intelligent Resume Embeddings for Precise Candidate Matching. Electronics, 14(4), 794. https://doi.org/10.3390/electronics14040794

Bruera, A., Alda, F., & Di Cerbo, F. (2022). Generating Realistic Synthetic Curricula Vitae for Machine Learning Applications under Differential Privacy. En I. Siegert, M. Rigault, & V. Arranz (Eds.), Proceedings of the Workshop on Ethical and Legal Issues in Human Language Technologies and Multilingual De-Identification of Sensitive Data In Language Resources within the 13th Language Resources and Evaluation Conference (pp. 53-63). European Language Resources Association. https://aclanthology.org/2022.legal-1.11/

Dasaklis, T. K., Giannopoulos, P. G., Koutras, D., Malamas, V., & Chountalas, P. (2025). Large Language Models in Human Resource Management: A systematic literature review of applications, open issues and future research directions (SSRN Scholarly Paper No. 5314976). Social Science Research Network. https://doi.org/10.2139/ssrn.5314976

EU AI Act, Reglamento (UE) 2024/1689 del Parlamento Europeo y del Consejo, de 13 de junio de 2024, por el que se establecen normas armonizadas en materia de inteligencia artificial (Ley de Inteligencia Artificial), L 2024/1689 (2024). https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=OJ:L_202401689

Fabris, A., Baranowska, N., Dennis, M. J., Graus, D., Hacker, P., Saldivar, J., Zuiderveen Borgesius, F., & Biega, A. J. (2025). Fairness and Bias in Algorithmic Hiring: A Multidisciplinary Survey. ACM Trans. Intell. Syst. Technol., 16(1). https://doi.org/10.1145/3696457

Fu, Z., Cao, Y., Chen, Y.-L., Lunia, A., Dong, L., Saraf, N., Jiang, R., Dai, Y., Song, Q., Wang, T., Li, G., Koh, D., Wei, H., Wang, Z., Gupta, A., Jiang, C., Shen, J., Hong, L., & Zhang, W. (2025). LANTERN: Scalable Distillation of Large Language Models for Job-Person Fit and Explanation. https://arxiv.org/abs/2510.05490

Gan, C., Zhang, Q., & Mori, T. (2024). Application of LLM Agents in Recruitment: A Novel Framework for Automated Resume Screening. Journal of Information Processing, 32, 881-893. https://doi.org/10.2197/ipsjjip.32.881

González-González, C., & Herrera, P. J. (2025). Selección de candidatos usando lógica borrosa, PLN y aprendizaje profundo. Actas de las Jornadas de Automática, 46, 489-496. https://doi.org/10.17979/ja-cea.2025.46.12139

Goodman, C. C. (2025). Algorithmic Bias and Accountability: The Double-Blind for Marginalized Job Applicants. University of Colorado Law Review, 96(2), 502-546.

Ip, E. (2025). Fair AI in hiring: Experimental evidence on how biased hiring algorithms and different debiasing methods affect the quality and diversity of applicants. Behavioral Science & Policy, 11(1), 44-54. https://doi.org/10.1177/23794607251353585

Lavi, D., Medentsiy, V., & Graus, D. (2021). conSultantBERT: Fine-tuned Siamese Sentence-BERT for Matching Jobs and Job Seekers. CoRR, abs/2109.06501. https://arxiv.org/abs/2109.06501

Ley 18.331. (2008). Ley 18.331: Protección de Datos Personales y Acción de Habeas Data. https://www.impo.com.uy/bases/leyes/18331-2008

Ley N.° 16.045: Prohíbese toda discriminación que viole el principio de igualdad de trato y de oportunidades para ambos sexos en cualquier sector (1989). https://www.impo.com.uy/bases/leyes/16045-1989

Liu, X. (2025). Deep Learning-Based Intelligent Resume-Position Matching System: Semantic Understanding and Recommendation of BERT Model in Massive Recruitment Data. Proceedings of the 2025 International Symposium on Machine Learning and Social Computing, MLSC ’25, 8-13. https://doi.org/10.1145/3778450.3778452

Lo, F. P.-W., Qiu, J., Wang, Z., Yu, H., Chen, Y., Zhang, G., & Lo, B. (2025). AI Hiring with LLMs: A Context-Aware and Explainable Multi-Agent Framework for Resume Screening. arXiv e-prints, arXiv:2504.02870. https://doi.org/10.48550/arXiv.2504.02870

Marr, B., & Ward, M. (2019). Artificial intelligence in practice: How 50 successful companies used AI and machine learning to solve problems. John Wiley & Sons.

New York City Local Law 144. (2023). Local Law 144 of 2021: Automated Employment Decision Tools. https://www.nyc.gov/site/dca/about/automated-employment-decision-tools.page

Raghavan, M., Barocas, S., Kleinberg, J., & Levy, K. (2020). Mitigating bias in algorithmic hiring: Evaluating claims and practices. Proceedings of the 2020 Conference on Fairness, Accountability, and Transparency, FAT* ’20, 469-481. https://doi.org/10.1145/3351095.3372828

Saldivar, J., Gatzioura, A., & Castillo, C. (2025). Synthetic CVs To Build and Test Fairness-Aware Hiring Tools. arXiv e-prints, arXiv:2508.21179. https://doi.org/10.48550/arXiv.2508.21179

Skondras, P., Zervas, P., & Tzimas, G. (2023). Generating Synthetic Resume Data with Large Language Models for Enhanced Job Description Classification. Future Internet, 15(11), 363. https://doi.org/10.3390/fi15110363

Staab, R., Vero, M., Balunović, M., & Vechev, M. (2023). Beyond Memorization: Violating Privacy Via Inference with Large Language Models. arXiv e-prints, arXiv:2310.07298. https://doi.org/10.48550/arXiv.2310.07298

Thomas, O., & Reimann, O. (2023). The bias blind spot among HR employees in hiring decisions. German Journal of Human Resource Management, 37(1), 5-22. https://doi.org/10.1177/23970022221094523

U.S. Equal Employment Opportunity Commission. (1978). Uniform guidelines on employee selection procedures (No. 166; pp. 38290-38315).

Vanetik, N., & Kogan, G. (2023). Job Vacancy Ranking with Sentence Embeddings, Keywords, and Named Entities. Information, 14, 468. https://doi.org/10.3390/info14080468

Wang, Z., Wu, Z., Guan, X., Thaler, M., Koshiyama, A., Lu, S., Beepath, S., Ertekin, E., & Perez-Ortiz, M. (2024). JobFair: A Framework for Benchmarking Gender Hiring Bias in Large Language Models (arXiv:2406.15484; Versión 1). arXiv. https://doi.org/10.48550/arXiv.2406.15484

Wilson, K., & Caliskan, A. (2024). Gender, Race, and Intersectional Bias in Resume Screening via Language Model Retrieval. arXiv e-prints, arXiv:2407.20371. https://doi.org/10.48550/arXiv.2407.20371

Repositorio

El código fuente completo del sistema, junto con los scripts de generación del corpus, indexación, evaluación y análisis estadístico, se encuentra alojado en un repositorio público de control de versiones. El presente anexo recoge la dirección del repositorio, las instrucciones mínimas para reproducir el entorno de forma local y los datos de acceso a la instancia desplegada para su evaluación en vivo.

Repositorio de código: https://github.com/abelvisiUNIR/sistac.git

Instalación local (reproducción del entorno)

El sistema requiere Python 3.10 o superior. La puesta en marcha desde una copia limpia del repositorio sigue cinco pasos:

Clonar el repositorio e ingresar al directorio del proyecto.

Crear y activar un entorno virtual de Python (python -m venv .venv).

Instalar las dependencias del proyecto (pip install -r scripts/python/requirements.txt).

Instalar el modelo lingüístico en español requerido por el módulo de anonimización (python -m spacy download es_core_news_lg).

Copiar el archivo .env.example a .env y completar las credenciales de los servicios de inteligencia artificial (modelo de lenguaje y almacén vectorial).

Una vez configurado el entorno, la suite de pruebas del módulo de anonimización permite verificar que la instalación es funcional. El flujo experimental completo (preparación del corpus, indexación, ejecución de las cuatro configuraciones y generación de tablas y figuras) se documenta en el archivo README.md del repositorio.

Acceso a la instancia desplegada

Se dispone de una instancia desplegada con datos de demostración:


*Tabla A1. Correspondencia entre los módulos funcionales del sistema y los archivos del repositorio.*


| Elemento | Valor |
|---|---|
| Dirección de acceso (URL) | https://sistac-app-92778042819.us-central1.run.app/ |
| Usuario de demostración | admin@sistac.uy |
| Contraseña de demostración | admin |


*Tabla módulo*


*Tabla B1. Correspondencia entre los módulos funcionales del sistema y los archivos del repositorio.*

Fuente: Elaboración propia.

Pantallas de la aplicación

La aplicación cuenta con una interfaz web que permite operar el sistema sin conocimientos técnicos. Este anexo documenta los tres flujos principales mediante capturas comentadas, que ilustran de forma concreta el funcionamiento descrito en el Capítulo 4.

Carga de currículum y descripción de cargo


*Figura C1. Pantalla de carga.*

El usuario sube la descripción del cargo y uno o varios currículums en formato PDF, DOCX o imagen. El sistema extrae el texto, lo normaliza y lo prepara para su evaluación

Resultado de la evaluación de un candidato


*Figura C2. Resultado del scoring.*

Para cada candidato, la interfaz muestra la puntuación de adecuación en una escala de 0 a 100, la decisión binaria (apto / no apto) y la justificación estructurada generada por el sistema, con el desglose por dimensiones de evaluación.

Comparación entre configuraciones


*Figura C3. Comparativa de configuraciones.*

La vista permite contrastar el resultado de un mismo candidato bajo las distintas formas de evaluación (con y sin recuperación de contexto, con y sin anonimización), evidenciando el efecto diferencial de cada componente.

Fuente: Elaboración propia.

Estructura del índice vectorial

El Capítulo 4 describe la arquitectura de recuperación aumentada del sistema; este anexo la concreta mostrando el esquema real del índice vectorial sobre el que opera la búsqueda. Cada fragmento de currículum se almacena como un registro con metadatos de identificación, el texto del fragmento, el vector denso que lo representa y los parámetros de búsqueda. Esta estructura es la que hace posible el aislamiento cruzado por par currículum-cargo (la búsqueda se restringe al par evaluado mediante los campos cv_id y jd_id) y la recuperación híbrida que combina similitud semántica y coincidencia léxica.

El campo embedding contiene el vector de 768 dimensiones generado por el modelo de embeddings multilingüe, indexado mediante el algoritmo HNSW con similitud por coseno para una búsqueda aproximada eficiente. El campo chunk_text habilita la búsqueda léxica en español, y el indicador anonymized permite distinguir los fragmentos procesados por el módulo de anonimización (configuración con supresión de datos personales) de los originales. Los campos cv_id y jd_id actúan como filtros que garantizan que ningún fragmento de otro candidato o de otro cargo contamine el contexto recuperado.

Esquema del índice (definición)

Significado de cada campo

Nota. La búsqueda combina la señal vectorial (campo embedding, algoritmo HNSW con similitud por coseno) y la léxica (campo chunk_text), y el filtro compuesto sobre cv_id y jd_id restringe la recuperación al par currículum-cargo bajo evaluación. Esta definición corresponde a la capa de indexación del sistema; en el despliegue sobre el proveedor de nube activo, los mismos campos operan como metadatos de filtrado y recuperación híbrida.
