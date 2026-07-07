## Organización del trabajo en grupo

Este apartado describe cómo se dividió el trabajo entre los dos integrantes del grupo, qué objetivos de aprendizaje se persiguieron con esa división y qué herramientas se usaron para coordinarse a lo largo del desarrollo.

### Partes que aborda el trabajo

El trabajo se estructuró en partes suficientemente diferenciadas como para que cada integrante pudiera profundizar en una línea propia sin perder de vista el conjunto. La mayor parte de los capítulos se elaboró de forma conjunta, con procesos de revisión cruzada y ajuste mutuo; sin embargo, en la fase de desarrollo técnico se estableció una división más clara: David Ilich Madrid Oyanadel se concentró en el pipeline de recuperación aumentada con generación y el motor de scoring semántico, mientras que Mario Agustín Belvisi Lescano asumió el módulo de anonimización de datos personales y el análisis de equidad algorítmica. Esta división permitió que cada integrante aportara profundidad en su área sin sacrificar la coherencia del trabajo como un todo. La distribución completa por sección se recoge en la tabla 1.

**Tabla 1.** *Organización del trabajo en grupo.*

| Capítulo / Sección | Responsable principal | Responsable de apoyo | Tareas clave |
|---|---|---|---|
| **CAP. 1: INTRODUCCIÓN** | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Articular la motivación del problema y la estructura general del trabajo |
| 1.1. Motivación | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Describir el contexto de Matriz y la doble dimensión operativa-ética del problema |
| 1.2. Planteamiento del trabajo | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Formular la pregunta de investigación y las tres hipótesis |
| 1.3. Estructura del trabajo | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Describir la organización de los capítulos con coherencia narrativa |
| **CAP. 2: ESTADO DEL ARTE** | David I. Madrid Oyanadel | Mario A. Belvisi Lescano | Consolidar el estado del arte y articular la brecha de investigación |
| 2.1. El proceso de selección y sus limitaciones | David I. Madrid Oyanadel | Mario A. Belvisi Lescano | Revisar sistemas ATS tradicionales y sus limitaciones documentadas |
| 2.2. LLMs aplicados a RRHH y ATS inteligentes | David I. Madrid Oyanadel | Mario A. Belvisi Lescano | Revisar literatura reciente sobre LLMs en procesos de selección |
| 2.3. Arquitecturas RAG | David I. Madrid Oyanadel | — | Desarrollar fundamentos y tipologías de arquitecturas RAG |
| 2.4. Privacidad de datos e información personal identificable (PII) | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Revisar técnicas de anonimización PII aplicadas al contexto curricular |
| 2.5. Fairness algorítmica en sistemas de selección | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Revisar métricas de equidad algorítmica y evidencia de sesgo en ATS |
| 2.6. Marco regulatorio y ético | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Analizar EU AI Act, Local Law 144 y Ley 18.331 Uruguay |
| 2.7. Análisis crítico y brecha de investigación | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Identificar la brecha que justifica la contribución del trabajo |
| 2.8. Conclusiones del estado del arte | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Sintetizar las decisiones de diseño que se derivan de la literatura |
| **CAP. 3: OBJETIVOS Y METODOLOGÍA** | David I. Madrid Oyanadel | Mario A. Belvisi Lescano | Definir objetivos, hipótesis y metodología CRISP-DM adaptada |
| 3.1. Objetivo general | David I. Madrid Oyanadel | Mario A. Belvisi Lescano | Formular el objetivo central del trabajo |
| 3.2. Objetivos específicos | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Desagregar los objetivos operativos con sus comparadores |
| 3.3. Metodología de trabajo | David I. Madrid Oyanadel | Mario A. Belvisi Lescano | Describir la adaptación CRISP-DM y el diseño factorial C0–C3 |
| **CAP. 4: ARQUITECTURA E IMPLEMENTACIÓN** | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Diseñar y documentar la arquitectura técnica del sistema |
| 4.1. Arquitectura general del sistema | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Describir la visión end-to-end del sistema con sus cuatro configuraciones |
| 4.2. Estrategia de datos | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Documentar corpus sintético, dataset público y JDs de Matriz |
| 4.3. Pipeline RAG | David I. Madrid Oyanadel | — | Describir embeddings, vector store Vertex AI y retrieval híbrido |
| 4.4. Motor de scoring semántico | David I. Madrid Oyanadel | Mario A. Belvisi Lescano | Documentar diseño del prompt, dimensiones de evaluación y umbral de decisión |
| 4.5. Módulo de anonimización PII | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Describir stack Presidio + spaCy, entidades detectadas y validación del módulo |
| 4.6. Stack técnico consolidado | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Sintetizar el conjunto de tecnologías empleadas en el sistema |
| 4.7. Dificultades técnicas y soluciones implementadas | David I. Madrid Oyanadel | Mario A. Belvisi Lescano | Documentar decisiones de ingeniería adoptadas durante el desarrollo |
| **CAP. 5: VALIDACIÓN EXPERIMENTAL Y RESULTADOS** | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Diseñar y ejecutar el framework de validación y presentar los resultados |
| 5.1. Diseño del experimento | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Definir el diseño cuasi-experimental con las cuatro condiciones C0–C3 |
| 5.2. Protocolo del Gold Standard | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Construir el Gold Standard híbrido con panel de evaluadores y κ de Cohen |
| 5.3. Métricas de evaluación | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Definir métricas por hipótesis: T_cand (H1), F₁/AUC-ROC (H2), DIR/SPD (H3) |
| 5.4. Suite estadística | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Especificar pruebas inferenciales y bootstrapping no paramétrico |
| 5.5. Gestión de datos y reproducibilidad | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Documentar controles de reproducibilidad y trazabilidad del experimento |
| 5.6–5.8. Resultados por hipótesis (H1, H2, H3) | David I. Madrid Oyanadel | Mario A. Belvisi Lescano | Presentar resultados organizados por hipótesis con tablas y figuras |
| 5.9–5.10. Análisis integrado y robustez | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Sintetizar resultados cruzados y réplica con modelo alternativo |
| **CAP. 6: DISCUSIÓN Y CONCLUSIONES** | David I. Madrid Oyanadel | Mario A. Belvisi Lescano | Interpretar resultados, formular conclusiones y recomendaciones |
| 6.1. Discusión de resultados | David I. Madrid Oyanadel | Mario A. Belvisi Lescano | Interpretar el significado de los resultados frente al estado del arte |
| 6.2. Limitaciones del estudio | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Identificar restricciones metodológicas y de generalización |
| 6.3. Implicaciones éticas y regulatorias | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Analizar consecuencias del sistema frente al EU AI Act y Ley 18.331 |
| 6.4. Conclusiones | David I. Madrid Oyanadel | Mario A. Belvisi Lescano | Sintetizar las contribuciones del trabajo por hipótesis |
| 6.5. Recomendaciones para Matriz | Mario A. Belvisi Lescano | David I. Madrid Oyanadel | Formular recomendaciones estratégicas para la organización colaboradora |
| 6.6. Líneas de trabajo futuro | David I. Madrid Oyanadel | Mario A. Belvisi Lescano | Identificar extensiones y mejoras derivadas de la investigación |

*Fuente: elaboración propia.*

### Objetivo del trabajo desde el punto de vista de la adquisición de conocimientos

Cada una de las partes que integran el trabajo habría podido constituir, por sí sola, el tema de una propuesta individual; lo que le da sentido grupal es precisamente que la combinación de esas partes genera un resultado más completo de lo que cualquiera de los dos integrantes podría haber alcanzado por separado. La elaboración del trabajo permitió poner en práctica competencias del Máster en Inteligencia Artificial y Data Science que van desde el diseño experimental y la estadística inferencial hasta la ingeniería de sistemas basados en modelos de lenguaje y el tratamiento responsable de datos personales, integrando en un único proyecto dimensiones que habitualmente se estudian por separado. Esta complementariedad es, en definitiva, lo que justifica el carácter grupal del trabajo y lo que le otorga relevancia no solo académica sino también práctica.

### Mecanismos de coordinación empleados

La coordinación entre los dos integrantes se sostuvo sobre cuatro canales principales: mensajería instantánea para el intercambio diario, videollamadas semanales de seguimiento del avance, un repositorio con control de versiones para la integración del código y almacenamiento compartido en la nube para la gestión de la memoria y los documentos del proyecto.
