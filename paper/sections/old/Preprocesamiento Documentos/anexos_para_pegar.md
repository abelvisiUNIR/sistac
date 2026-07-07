# Anexos para pegar en el documento | 23/06/2026

Contenido listo para insertar al final del TFE. Aporta ~4-5 páginas. Mantener el **Anexo B** existente (tabla módulo→archivo) sin cambios; este material reemplaza/expande el actual "Anexo A. CÓDIGO" y agrega los anexos C y D.

> Pendiente de completar con tus datos: (1) la URL y las credenciales de demo en el Anexo A, y (2) las tres capturas de pantalla en el Anexo C (los pies ya están redactados).

---

## Anexo A. Repositorio y despliegue

El código fuente completo del sistema, junto con los scripts de generación del corpus, indexación, evaluación y análisis estadístico, se encuentra alojado en un repositorio público de control de versiones. El presente anexo recoge la dirección del repositorio, las instrucciones mínimas para reproducir el entorno de forma local y los datos de acceso a la instancia desplegada para su evaluación en vivo.

**Repositorio de código:** https://github.com/abelvisiUNIR/sistac.git

### A.1. Instalación local (reproducción del entorno)

El sistema requiere Python 3.10 o superior. La puesta en marcha desde una copia limpia del repositorio sigue cinco pasos:

1. Clonar el repositorio e ingresar al directorio del proyecto.
2. Crear y activar un entorno virtual de Python (`python -m venv .venv`).
3. Instalar las dependencias del proyecto (`pip install -r scripts/python/requirements.txt`).
4. Instalar el modelo lingüístico en español requerido por el módulo de anonimización (`python -m spacy download es_core_news_lg`).
5. Copiar el archivo `.env.example` a `.env` y completar las credenciales de los servicios de inteligencia artificial (modelo de lenguaje y almacén vectorial).

Una vez configurado el entorno, la suite de pruebas del módulo de anonimización permite verificar que la instalación es funcional. El flujo experimental completo (preparación del corpus, indexación, ejecución de las cuatro configuraciones y generación de tablas y figuras) se documenta en el archivo `README.md` del repositorio.

### A.2. Acceso a la instancia desplegada

Con el fin de que el tribunal pueda evaluar el sistema en funcionamiento sin necesidad de instalarlo, se dispone de una instancia desplegada con datos de demostración:

| Elemento                   | Valor                                       |
| ----------------------------| ---------------------------------------------|
| Dirección de acceso (URL)  | **[COMPLETAR: URL del entorno desplegado]** |
| Usuario de demostración    | **[COMPLETAR: usuario]**                    |
| Contraseña de demostración | **[COMPLETAR: contraseña]**                 |

La instancia de demostración opera sobre datos sintéticos y no contiene información personal real, en cumplimiento de la Ley 18.331 de Protección de Datos Personales de Uruguay. Las credenciales anteriores ofrecen acceso de solo lectura a los flujos de carga de currículum, evaluación y comparación de configuraciones descritos en el Anexo C.

---

## Anexo B. Correspondencia entre módulos y archivos

*(Sin cambios. Conservar la tabla B1 existente.)*

---

## Anexo C. Pantallas de la aplicación

La aplicación cuenta con una interfaz web que permite operar el sistema sin conocimientos técnicos. Este anexo documenta los tres flujos principales mediante capturas comentadas, que ilustran de forma concreta el funcionamiento descrito en el Capítulo 4.

**[INSERTAR CAPTURA 1: carga de currículum y descripción de cargo]**

> **Figura C1. Pantalla de carga.** El usuario sube la descripción del cargo y uno o varios currículums en formato PDF, DOCX o imagen. El sistema extrae el texto, lo normaliza y lo prepara para su evaluación. Fuente: elaboración propia.

**[INSERTAR CAPTURA 2: resultado de la evaluación de un candidato]**

> **Figura C2. Resultado del scoring.** Para cada candidato, la interfaz muestra la puntuación de adecuación en una escala de 0 a 100, la decisión binaria (apto / no apto) y la justificación estructurada generada por el sistema, con el desglose por dimensiones de evaluación. Fuente: elaboración propia.

**[INSERTAR CAPTURA 3: comparación entre configuraciones]**

> **Figura C3. Comparativa de configuraciones.** La vista permite contrastar el resultado de un mismo candidato bajo las distintas formas de evaluación (con y sin recuperación de contexto, con y sin anonimización), evidenciando el efecto diferencial de cada componente. Fuente: elaboración propia.

---

## Anexo D. Estructura del índice vectorial

El Capítulo 4 describe la arquitectura de recuperación aumentada del sistema; este anexo la concreta mostrando el esquema real del índice vectorial sobre el que opera la búsqueda. Cada fragmento de currículum se almacena como un registro con metadatos de identificación, el texto del fragmento, el vector denso que lo representa y los parámetros de búsqueda. Esta estructura es la que hace posible el aislamiento cruzado por par currículum-cargo (la búsqueda se restringe al par evaluado mediante los campos `cv_id` y `jd_id`) y la recuperación híbrida que combina similitud semántica y coincidencia léxica.

El campo `embedding` contiene el vector de 768 dimensiones generado por el modelo de embeddings multilingüe, indexado mediante el algoritmo HNSW con similitud por coseno para una búsqueda aproximada eficiente. El campo `chunk_text` habilita la búsqueda léxica en español, y el indicador `anonymized` permite distinguir los fragmentos procesados por el módulo de anonimización (configuración con supresión de datos personales) de los originales. Los campos `cv_id` y `jd_id` actúan como filtros que garantizan que ningún fragmento de otro candidato o de otro cargo contamine el contexto recuperado.

### D.1. Esquema del índice (definición)

```json
{
  "name": "sistac-cvs",
  "fields": [
    { "name": "id",          "type": "Edm.String",  "key": true,  "filterable": true },
    { "name": "cv_id",       "type": "Edm.String",  "filterable": true },
    { "name": "jd_id",       "type": "Edm.String",  "filterable": true },
    { "name": "chunk_text",  "type": "Edm.String",  "searchable": true, "analyzer": "es.lucene" },
    { "name": "cv_text",     "type": "Edm.String",  "retrievable": true },
    { "name": "jd_text",     "type": "Edm.String",  "retrievable": true },
    { "name": "anonymized",  "type": "Edm.Boolean", "filterable": true },
    { "name": "chunk_index", "type": "Edm.Int32",   "retrievable": true },
    {
      "name": "embedding",
      "type": "Collection(Edm.Single)",
      "searchable": true,
      "dimensions": 768,
      "vectorSearchProfile": "sistac-vector-profile"
    }
  ],
  "vectorSearch": {
    "algorithms": [
      { "name": "sistac-hnsw", "kind": "hnsw",
        "hnswParameters": { "m": 4, "efConstruction": 400, "efSearch": 500, "metric": "cosine" } }
    ],
    "profiles": [ { "name": "sistac-vector-profile", "algorithm": "sistac-hnsw" } ]
  },
  "semantic": {
    "defaultConfiguration": "default",
    "configurations": [
      { "name": "default",
        "prioritizedFields": {
          "prioritizedContentFields": [ { "fieldName": "chunk_text" } ],
          "prioritizedKeywordsFields": [ { "fieldName": "cv_id" }, { "fieldName": "jd_id" } ]
        } }
    ]
  }
}
```

### D.2. Significado de cada campo

| Campo         | Tipo                      | Función                                                                                   |
| ---------------| ---------------------------| -------------------------------------------------------------------------------------------|
| `id`          | Texto (clave)             | Identificador único de cada fragmento indexado.                                           |
| `cv_id`       | Texto (filtrable)         | Identificador del currículum al que pertenece el fragmento; base del aislamiento cruzado. |
| `jd_id`       | Texto (filtrable)         | Identificador de la descripción de cargo asociada.                                        |
| `chunk_text`  | Texto (buscable, español) | Texto del fragmento; soporta la búsqueda léxica con analizador en español.                |
| `cv_text`     | Texto (recuperable)       | Texto completo del currículum, disponible para trazabilidad.                              |
| `jd_text`     | Texto (recuperable)       | Texto de la descripción de cargo.                                                         |
| `anonymized`  | Booleano (filtrable)      | Indica si el fragmento fue procesado por el módulo de anonimización.                      |
| `chunk_index` | Entero                    | Posición del fragmento dentro del documento original.                                     |
| `embedding`   | Vector de 768 dimensiones | Representación semántica densa del fragmento; sustento de la búsqueda vectorial.          |

> Nota. La búsqueda combina la señal vectorial (campo `embedding`, algoritmo HNSW con similitud por coseno) y la léxica (campo `chunk_text`), y el filtro compuesto sobre `cv_id` y `jd_id` restringe la recuperación al par currículum-cargo bajo evaluación. Esta definición corresponde a la capa de indexación del sistema; en el despliegue sobre el proveedor de nube activo, los mismos campos operan como metadatos de filtrado y recuperación híbrida.
