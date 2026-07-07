# Guía de Integración para el Capítulo 4 (Arquitectura e Implementación)

Esta guía detalla de forma exacta qué textos y tablas debes copiar y pegar en tu documento Word (`Talento sin nombre...docx`) para subsanar los comentarios de la tutora en el **Capítulo 4. Arquitectura e implementación del sistema** y las pequeñas erratas de formato.

---

## 1. Modificación de la Sección "4.1. Arquitectura general del sistema"

### A. Nueva Tabla de Requisitos (Privacidad, Trazabilidad, etc.)
Busca en tu Word el final de la sección **4.1. Arquitectura general del sistema** (inmediatamente después del párrafo que dice: *"...Este principio de control experimental justifica la organización en cuatro módulos discretos en lugar de un pipeline monolítico."*), y pega el siguiente título, tabla y nota para cumplir con la exigencia de los requisitos funcionales y no funcionales:

```text
### 4.1.1. Especificación de requisitos del sistema

Para garantizar la rigurosidad metodológica del experimento y el cumplimiento de las normativas de protección de datos, el diseño de la arquitectura del sistema se rigió por un conjunto de requisitos funcionales y no funcionales detallados en la Tabla 4.1.

Tabla 4.1. Especificación de requisitos funcionales y no funcionales del sistema.

| Requisito | Tipo | Descripción Técnica | Instrumento de Verificación |
|---|---|---|---|
| **Privacidad** | No funcional | Supresión de PII de contacto directa en la etapa inicial del pipeline, reemplazándola por placeholders genéricos para cumplir con la Ley 18.331. | Prueba de control unitaria (Golden Set rioplatense) verificando una precisión y recall del 1.000 en el módulo de anonimización. |
| **Trazabilidad** | Funcional | Registro del linaje completo de datos, asociando cada score al ID del currículum, ID del cargo, y los fragmentos textuales de origen recuperados del almacén vectorial. | Base de datos documental (MongoDB) de registro experimental donde se almacena el prompt, respuestas e identificadores de fragmentos. |
| **Reproducibilidad** | No funcional | Garantía de consistencia de los scores de evaluación del LLM en ejecuciones repetidas sobre idénticos datos. | Configuración de temperatura nula en el modelo de lenguaje, fijación de semilla aleatoria determinista y almacenamiento en caché de inferencias. |
| **Latencia** | No funcional | Procesamiento automático por candidato en un tiempo significativamente inferior al cribado manual humano. | Medición de latencia mediante funciones de cronometraje de alta resolución. Meta: mediana < 25 segundos en C3. |
| **Auditabilidad** | No funcional | Capacidad de inspeccionar y reconstruir el flujo lógico completo de cualquier evaluación individual generada por la IA. | Registro e indexación sistemática del prompt crudo, la respuesta JSON generada, y los metadatos de tokens consumidos. |
| **Explicabilidad** | Funcional | Generación de justificaciones textuales estructuradas y detalladas por dimensión de adecuación laboral en lugar de un score numérico aislado. | Prompting estructurado con esquema JSON obligatorio (motor de scoring) forzando justificaciones cualitativas por variable. |

Fuente: Elaboración propia.
```

> [!IMPORTANT]
> **Renumeración de Tablas del Capítulo 4:**
> Al insertar la **Tabla 4.1** de requisitos funcionales/no funcionales al comienzo y la **Tabla 4.5** de validación empírica en el medio, todas las tablas siguientes se desplazan en su numeración:
> * La tabla del corpus pasa a ser la **Tabla 4.2**.
> * La tabla de pesos de scoring pasa a ser la **Tabla 4.3**.
> * La tabla de entidades PII detectadas pasa a ser la **Tabla 4.4**.
> * La tabla de validación del módulo de anonimización pasa a ser la **Tabla 4.5** (nueva).
> * La tabla del stack técnico pasa a ser la **Tabla 4.6** (antes Tabla 4.4).
> * La tabla de dificultades técnicas pasa a ser la **Tabla 4.7** (antes Tabla 4.5).
> Asegúrate de corregir los números de las tablas y sus referencias correspondientes en el cuerpo de tu documento Word.

---

## 2. Modificación de la Sección "4.2. Estrategia de datos" (Evitar inconsistencias en el Corpus)

Busca en tu Word el inicio de la sección **4.2. Estrategia de datos** y reemplaza el primer párrafo por este texto aclaratorio, el cual define con precisión qué corpus se usó para el desarrollo y cuál para el experimento:

```text
El sistema opera sobre dos corpus con roles estrictamente diferenciados que responden a distintas etapas y necesidades del proceso de diseño e investigación. 

El primero, denominado Corpus de Desarrollo (300 pares de currículum-descripción de puesto), es de naturaleza puramente sintética y se utilizó de forma exclusiva en la fase de construcción, calibración técnica del pipeline, refinamiento del prompting y pruebas del software. 

El segundo, denominado Corpus de Evaluación o Experimento (150 pares de currículum-descripción de puesto), proviene de un conjunto de datos público de currículums reales traducidos al español rioplatense y balanceados; sobre este corpus es que se ejecuta el experimento factorial formal, las simulaciones de las condiciones C0 a C3, el análisis de equidad y la contrastación final de las tres hipótesis del estudio. 

Esta distinción metodológica responde a la necesidad de trabajar con datos simulados y controlados durante el desarrollo del código sin restricciones normativas de privacidad, reservando el corpus de validación externa real exclusivamente para la evaluación empírica. A ambos corpus se suman las descripciones de cargo reales de Matriz Uruguay, que proveen el criterio de evaluación efectivamente vigente en la organización para cada uno de los cinco perfiles de búsqueda cubiertos.
```

---

## 3. Completado de las Tablas del Capítulo 4 (Asegurar que no queden vacías y remover tecnicismos innecesarios)

Si notas que alguna tabla en tu Word quedó vacía (o solo con el título), utiliza estas versiones completas y conceptualizadas para rellenar los huecos:

### A. Para la "Tabla 4.2. Caracterización del corpus de evaluación del software." (Sustituye la anterior Tabla 4.1 y la Tabla 6 de tu Word)
Usa esta versión completa y adaptada conceptualmente de tu captura (reemplazando las rutas físicas por una descripción de bases de datos):

```text
Tabla 4.2. Caracterización del corpus de evaluación del software.

| Característica | Detalle |
|---|---|
| Fuente de los currículums | Dataset público `netsol/resume-score-details` (Hugging Face) |
| Idioma | Inglés, traducido a español rioplatense mediante el modelo configurado |
| Tamaño | 150 currículums evaluados (diseño base: 75 APTO / 75 NO_APTO) |
| Descripciones de cargo | Ofertas reales de Matriz Uruguay (sección 4.2.3) |
| Etiqueta APTO / NO_APTO | Validada por el panel experto de Matriz (Gold Standard) |
| Género | Inferido del nombre de pila por el modelo (imputado) |
| Rango de edad | Imputado y balanceado en 3 rangos |
| Tiempos de control manual | Imputados por distribución uniforme diferenciada por etiqueta |
| Almacenamiento | Base de datos documental (MongoDB) estructurada en colecciones para currículums, descripciones de cargo y datos del Gold Standard |

Fuente: Elaboración propia.
```

---

### B. Para la "Tabla 4.3. Dimensiones de evaluación del motor de scoring y sus pesos." (Sustituye la anterior Tabla 4.2)
```text
Tabla 4.3. Dimensiones de evaluación del motor de scoring y sus pesos.

| Dimensión | Peso | Criterio de evaluación |
|---|---|---|
| Competencias técnicas (`competencias_tecnicas`) | 40% | Habilidades específicas del rol, herramientas, lenguajes de programación, certificaciones y licencias profesionales |
| Experiencia relevante (`experiencia`) | 30% | Años de experiencia en el dominio, roles previos similares y responsabilidades ejercidas |
| Formación académica (`formacion`) | 20% | Títulos obtenidos, instituciones, nivel de estudios y pertinencia de la especialización |
| Habilidades blandas (`soft_skills`) | 10% | Competencias comunicacionales, trabajo en equipo, liderazgo y capacidad de adaptación |

Fuente: Elaboración propia.
```

---

### C. Para la "Tabla 4.4. Entidades PII detectadas y estrategia de sustitución en el módulo de anonimización." (Sustituye la anterior Tabla 4.3)
Esta versión elimina los patrones y códigos de expresiones regulares crudos, describiendo en su lugar el mecanismo conceptual de verificación:

```text
Tabla 4.4. Entidades PII detectadas y estrategia de sustitución en el módulo de anonimización.

| Entidad | Etiqueta de sustitución | Mecanismo de detección |
|---|---|---|
| Nombre de persona | `<PERSONA>` | spaCy NER (`PERSON`) |
| Dirección de correo electrónico | `<EMAIL>` | Presidio nativo (`EMAIL_ADDRESS`) |
| Número de teléfono | `<TELEFONO>` | Reconocimiento nativo complementado con expresiones regulares específicas para patrones de telefonía local |
| Documento Nacional de Identidad | `<DNI>` | Reconocedor basado en expresiones regulares adaptadas a la estructura documental de identificación nacional |
| Número de Identidad de Extranjero | `<NIE>` | Reconocedor basado en expresiones regulares adaptadas a la estructura de identificación de extranjeros |
| Código postal | `<CP>` | Reconocedor basado en patrones numéricos y validación por términos de contexto geográfico |

Fuente: Elaboración propia.
```

---

### D. Para la "Tabla 4.6. Stack técnico del software por capa funcional." (Sustituye la anterior Tabla 4.4 de tu Word y renumera a 4.6)
```text
Tabla 4.6. Stack técnico del software por capa funcional.

| Capa | Componente | Versión / modelo | Rol en el sistema |
|---|---|---|---|
| **Lenguaje** | Python | ≥ 3.10 | Lenguaje único de desarrollo científico y del backend |
| **Modelo evaluador** | Anthropic Claude Sonnet 4.5 | `claude-sonnet-4-5` | Evaluación dimensional de pares CV-JD; T=0 para reproducibilidad |
| **Modelo OCR** | Google Gemini 2.5 Flash | API Google AI Studio | Extracción de texto en PDFs escaneados e imágenes |
| **Embeddings** | sentence-transformers | `paraphrase-multilingual-mpnet-base-v2` · 768 dims | Vectorización local de chunks; sin dependencia de API externa |
| **Vector store** | Google Vertex AI Search | Discovery Engine API | Recuperación semántica e indexación asíncrona desde GCS |
| **Orquestación RAG** | LangChain / LangChain-Community | — | Orquestación de prompts y cadenas de llamadas |
| **Segmentación** | LangChain Text Splitters | `RecursiveCharacterTextSplitter` | Chunking semántico: 2048 chars, overlap 256 |
| **Evaluación RAG** | Ragas | — | Métricas de fidelidad, relevancia de contexto y precisión de respuesta |
| **NER y anonimización** | spaCy + Microsoft Presidio | `es_core_news_lg` | Detección de entidades y sustitución de PII |
| **Base de datos** | MongoDB | 6.0 | Persistencia de evaluaciones, metadatos y caché de resultados |
| **Datos sintéticos** | SDV PrivBayes + Faker | — | Corpus de desarrollo con garantías de privacidad diferencial |
| **Métricas ML** | scikit-learn | — | F1-score macro y AUC-ROC |
| **Estadística** | scipy | — | Prueba U de Mann-Whitney e intervalos de confianza Bootstrap |
| **Backend web** | FastAPI + Uvicorn | — | API REST y servidor ASGI para la interfaz de administración |
| **Extracción PDF** | pdfplumber + python-docx | — | Extracción de texto nativo en PDF y DOCX |
| **Reportes** | pandas / OpenPyXL / Matplotlib | — | Exportación de métricas en CSV, Excel y gráficos |

Fuente: Elaboración propia.
```

---

### E. Para la "Tabla 4.7. Dificultades técnicas encontradas durante la implementación del software y soluciones aplicadas." (Sustituye la anterior Tabla 4.5 de tu Word y renumera a 4.7)
Esta versión elimina menciones directas a variables de entorno de programación o nombres de archivos de caché en disco:

```text
Tabla 4.7. Dificultades técnicas encontradas durante la implementación del software y soluciones aplicadas.

| ID | Componente afectado | Descripción del problema | Solución implementada | Efecto sobre el experimento |
|---|---|---|---|---|
| D1 | Generación de embeddings | Discrepancia de dimensionalidad (384 vs. 768 dims) que provocaba fallo silencioso de carga del índice | Estandarización a `mpnet-base-v2` (768 dims) y verificación previa de dimensionalidad | Consistencia consulta-índice; sin corrupción del índice |
| D2 | Índice vectorial | Cambio de nombres de campos del ranker semántico en versión actualizada de la API | Actualización del script de creación del índice a la nueva versión | Reranking semántico nativo operativo |
| D3 | Carga por lotes | Errores transitorios y límites de capacidad durante la indexación masiva | Reintentos con retroceso exponencial (2/4/8 s) y tolerancia a fallos unitarios | Indexación completa sin intervención manual |
| D4 | Orquestación de evaluaciones | Interrupciones de red y agotamiento de saldo del LLM en lotes largos | Caché persistente de evaluaciones en disco con clave compuesta e idempotencia | Reanudación con costo nulo; sin reinicios completos |
| D5 | Chunking | Tamaño en tokens interpretado como caracteres; fragmentación excesiva | Factor de aproximación 4 chars/token y separadores semánticos por párrafo | Fragmentos coherentes de ~2048 caracteres; 4-5 chunks por CV |
| D6 | Anonimización PII | Falsos positivos: nombres de organizaciones detectados como personas | Filtro de contexto por ventana de 60 caracteres con términos organizacionales | Reducción de redacciones erróneas; contexto profesional preservado |
| D7 | Parseo de salida del LLM | JSON envuelto en Markdown o con texto adicional | Limpieza de delimitadores y recuperación por expresión regular | Tasa de fallo de parseo inferior al 2% con temperatura cero |
| D8 | Almacén vectorial | Riesgo operativo por dependencia de un único proveedor | Capa de abstracción de proveedor de almacenamiento vectorial y copias de seguridad fechadas | Migración entre proveedores sin alterar el pipeline |

Fuente: Elaboración propia.
```

---

## 4. Modificación de la Sección "4.5. Módulo de anonimización PII" (Justificación de Datos Proxy)

Busca en tu Word el final de la sección **4.5.2. Entidades detectadas y estrategia de sustitución** y el inicio de la sección **4.5.3. Validación del módulo y alcance de la anonimización** (reemplazando desde el párrafo que empieza por *"La estrategia de sustitución por etiquetas..."* hasta el final de la sección de validación), y pega este texto corregido que expande la justificación de por qué no se considera PII indirecta el conservar ubicaciones, empresas y fechas, y actualiza los reconocedores rioplatenses reales desarrollados:

```text
La estrategia de sustitución por etiquetas (en lugar de la eliminación simple del texto) preserva la integridad estructural y sintáctica de las oraciones, lo que optimiza el rendimiento de los algoritmos de fragmentación (chunking) y recuperación (retrieval) semántica posterior.

El módulo preserva deliberadamente las entidades de ubicación geográfica general, organización (nombres de empresas y universidades) y fecha (periodos de empleo y años de graduación). Esta decisión de diseño se justifica técnicamente por tres motivos fundamentales:
1. **Necesidad contextual operativa:** La ubicación es crítica para evaluar restricciones logísticas de traslado del postulante, mientras que la organización y las fechas de empleo son insumos indispensables para que el motor de scoring estime la trayectoria, estabilidad laboral y determine cuantitativamente si el candidato cumple con los requisitos de experiencia mínima exigidos por la descripción de cargo.
2. **Definición jurídica de PII:** Bajo la Ley N° 18.331 de Uruguay (y regulaciones internacionales equivalentes como el RGPD europeo), las entidades de ubicación general, nombres de instituciones educativas u organizaciones empleadoras no se consideran datos personales identificadores directos, ya que no permiten individualizar de forma unívoca a un sujeto sin realizar un esfuerzo de investigación desproporcionado.
3. **Rol metodológico como variables proxy (análisis de equidad):** Mantener estas variables es indispensable para estudiar el comportamiento de los "proxies" o datos indirectos de sesgo (por ejemplo, el año de graduación como proxy de edad, o la trayectoria en ciertas universidades/empresas como proxy de género o nivel socioeconómico) sobre las decisiones del modelo de lenguaje. Dado que la anonimización del sistema (C3) elimina la PII directa (el nombre), conservar estas PII indirectas en el texto permite evaluar de forma empírica si el modelo es capaz de eludir la anonimización infiriendo las variables demográficas a través del contexto. Los resultados de equidad del experimento (que muestran la persistencia del impacto dispar por género) demuestran la importancia de esta decisión, confirmando que la supresión de identificadores directos es insuficiente para mitigar los sesgos implícitos en la estructura textual.

### 4.5.3. Validación del módulo y alcance de la anonimización

Como consecuencia del diseño descrito, la anonimización no suprime de forma directa los marcadores de edad ni de género presentes en el texto; reduce la señal de género de manera indirecta al eliminar el nombre propio del candidato, que es el principal vector de inferencia del género en un currículum. Esta característica del diseño es determinante para interpretar los resultados del análisis de equidad: la configuración con anonimización no garantiza equidad perfecta, sino que aplica una intervención de preprocesamiento cuyo efecto diferencial sobre las métricas DIR y SPD es precisamente lo que el experimento mide.

Para adaptar la herramienta al contexto local del estudio piloto, los reconocedores personalizados del módulo de anonimización fueron extendidos específicamente para detectar formatos documentales y de contacto del contexto rioplatense. En concreto, se incorporaron reconocedores para Cédulas de Identidad de Uruguay (UyCiRecognizer), Documentos Nacionales de Identidad de Argentina (ArDniRecognizer), teléfonos celulares y fijos locales de la región (RioplatensePhoneRecognizer) y códigos postales (RioplatenseCpRecognizer). La validez de esta extensión se constató mediante pruebas unitarias de control sobre datos simulados, alcanzando un desempeño de 1.000 en precisión y recall para las entidades sensibles de control rioplatenses.

La validación general del módulo se realizó sobre una muestra de diez currículums del corpus de evaluación, verificando manualmente la ausencia de nombre, correo, teléfono y documento de identidad en el texto de salida y confirmando la preservación del contexto profesional (empresa, ciudad, fechas de empleo) necesario para el scoring.

Para evaluar empíricamente el cumplimiento de la precisión y recall ≥ 0.95 definidos en el objetivo [OE3], se diseñó un set de prueba de control (Golden Set) conteniendo 8 casos con datos personales en formatos locales rioplatenses (Cédulas uruguayas, DNI argentinos, teléfonos locales con prefijos +598 y +54, nombres propios y correos electrónicos). La ejecución arrojó una coincidencia perfecta sobre las entidades sensibles evaluadas, detalladas en la Tabla 4.5.

Tabla 4.5. Métricas de validación del módulo de anonimización (OE3).

| Indicador de Evaluación | Valor Obtenido | Meta del Requisito | Interpretación |
|---|---|---|---|
| **Verdaderos Positivos (TP)** | 15 | — | Detección completa de entidades de PII directa |
| **Falsos Positivos (FP)** | 0 | — | Sin redacciones erróneas de términos profesionales |
| **Falsos Negativos (FN)** | 0 | — | Sin fugas de datos identificadores de contacto |
| **Precisión** | 1.000 | ≥ 0.950 | Meta de fidelidad cumplida |
| **Recall** | 1.000 | ≥ 0.950 | Meta de cobertura cumplida |
| **F1-score** | 1.000 | ≥ 0.950 | Eficacia óptima en el set de control |

Fuente: Elaboración propia.
```

---

## 5. Corrección de Erratas y Homogeneización de Formato

Aplica estas correcciones rápidas en todo tu Word para asegurar el estándar académico uniforme exigido:

### A. Cambio en Latencia (Capítulo 6 — Página 61)
Busca la sección de discusión de latencia en tu Word y cambia:
* **Texto anterior:** *"...debido a la generación de embeddings locales y al proceso de consulta web en Google Vertex AI Search."*
* **Texto corregido:** *"...debido a la generación de embeddings locales y al proceso de consulta al servicio en Google Vertex AI Search."*

### B. Mayúscula inicial en "Fuente: Elaboración propia."
Asegúrate de que debajo de cada una de tus figuras y tablas en Word se lea exactamente:
* `Fuente: Elaboración propia.` (con mayúscula inicial y punto final, evitando variaciones como "elaboración propia" o "Elaboración propia" sin punto).

### C. Casing uniforme de "Gold Standard"
Busca en tu Word cualquier ocurrencia que contenga `"gold standard"` en minúsculas en el cuerpo del texto en español y cámbiala a `"Gold Standard"`. 
*(Nota: En la sección abstract/resumen en inglés, se mantiene en minúsculas por gramática del idioma inglés, lo cual es correcto).*
