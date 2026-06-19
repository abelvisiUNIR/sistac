# Detalles de Precisión Técnica en el Código de SISTAC

Este documento recopila de forma exacta la información técnica del código fuente del sistema SISTAC para su inclusión precisa en el TFE.

---

## 1. Motor de scoring — [scorer.py](file:///C:/Users/abelvisi/Documents/Google_Drive/Mi%20unidad/M%C3%A1ster%20UNIR/IA%20Y%20Data/TFE/Entregas_TFE_Terminal/clo-author/scripts/python/scoring/scorer.py)

### Pesos y Dimensiones
Los pesos exactos para las cuatro dimensiones evaluadas se encuentran definidos en la función [_parse_llm_response](file:///C:/Users/abelvisi/Documents/Google_Drive/Mi%20unidad/M%C3%A1ster%20UNIR/IA%20Y%20Data/TFE/Entregas_TFE_Terminal/clo-author/scripts/python/scoring/scorer.py#L171):

*   **Competencias técnicas (`competencias_tecnicas`):** $40\%$ (`0.40`)
*   **Experiencia relevante (`experiencia`):** $30\%$ (`0.30`)
*   **Formación académica (`formacion`):** $20\%$ (`0.20`)
*   **Habilidades blandas (`soft_skills`):** $10\%$ (`0.10`)

### Lógica de Cálculo del Score
El score final se obtiene realizando un promedio ponderado de los scores individuales (asignados por el LLM a cada dimensión) y aplicando un redondeo estándar al entero más cercano (`round(weighted_score)`). Si el JSON resultante del LLM no contiene las dimensiones desglosadas, se toma por defecto el score global devuelto por el LLM.

El umbral para clasificar a un candidato como **APTO** o **NO_APTO** es `SCORE_THRESHOLD = 70` (definido en [config.py](file:///C:/Users/abelvisi/Documents/Google_Drive/Mi%20unidad/M%C3%A1ster%20UNIR/IA%20Y%20Data/TFE/Entregas_TFE_Terminal/clo-author/scripts/python/config.py#L130)).

### Prompts Completos

#### System Prompt
```text
Eres un evaluador experto en selección de talento con 15 años
de experiencia en recursos humanos. Tu tarea es evaluar de forma objetiva y
estructurada la compatibilidad entre un currículum vitae (CV) y una descripción
de cargo (JD). Responde ÚNICAMENTE con JSON válido, sin texto adicional ni
bloques de código.
```

#### User Prompt (Con RAG — Configuraciones C2/C3)
```text
Evalúa la compatibilidad entre el siguiente CV y la descripción de cargo.

=== DESCRIPCIÓN DEL CARGO ===
{jd_text}

=== FRAGMENTOS RECUPERADOS DEL CV (evidencia disponible) ===
{context}

=== INSTRUCCIONES ===
Evalúa exclusivamente con base en la evidencia presente en los fragmentos.
No inferas información que no esté explícita. Si un criterio no puede evaluarse
por falta de información en los fragmentos, asigna 50 (neutral).

Responde con este JSON exacto:
{
  "score": <entero 0-100>,
  "dimensions": {
    "competencias_tecnicas": <entero 0-100>,
    "experiencia": <entero 0-100>,
    "formacion": <entero 0-100>,
    "soft_skills": <entero 0-100>
  },
  "justification": "<máximo 150 palabras, basada solo en evidencia de los fragmentos>",
  "evidence_gaps": "<aspectos no evaluables por falta de información, o 'ninguno'>"
}
```

#### User Prompt (Sin RAG — Configuración C1)
```text
Evalúa la compatibilidad entre el siguiente CV y la descripción de cargo.

=== DESCRIPCIÓN DEL CARGO ===
{jd_text}

=== CURRÍCULUM VITAE COMPLETO ===
{cv_text}

=== INSTRUCCIONES ===
Evalúa con base en toda la información del CV. Si un criterio no está explícito,
asigna 50 (neutral). Sé objetivo y basate en evidencia concreta.

Responde con este JSON exacto:
{
  "score": <entero 0-100>,
  "dimensions": {
    "competencias_tecnicas": <entero 0-100>,
    "experiencia": <entero 0-100>,
    "formacion": <entero 0-100>,
    "soft_skills": <entero 0-100>
  },
  "justification": "<máximo 150 palabras, basada en evidencia del CV>",
  "evidence_gaps": "<aspectos no evaluables por falta de información, o 'ninguno'>"
}
```

---

## 2. Módulo PII — [anonymizer.py](file:///C:/Users/abelvisi/Documents/Google_Drive/Mi%20unidad/M%C3%A1ster%20UNIR/IA%20Y%20Data/TFE/Entregas_TFE_Terminal/clo-author/scripts/python/pii/anonymizer.py) y [recognizers.py](file:///C:/Users/abelvisi/Documents/Google_Drive/Mi%20unidad/M%C3%A1ster%20UNIR/IA%20Y%20Data/TFE/Entregas_TFE_Terminal/clo-author/scripts/python/pii/recognizers.py)

### Entidades Redactadas y Placeholders
*   `PERSON` $\rightarrow$ `<PERSONA>`
*   `EMAIL_ADDRESS` $\rightarrow$ `<EMAIL>`
*   `PHONE_NUMBER` y `ES_PHONE` $\rightarrow$ `<TELEFONO>`
*   `ES_DNI` $\rightarrow$ `<DNI>`
*   `ES_NIE` $\rightarrow$ `<NIE>`
*   `ES_CP` $\rightarrow$ `<CP>`

### Reconocedores Personalizados (SISTAC_RECOGNIZERS)
El sistema utiliza Microsoft Presidio y la biblioteca `spaCy` (`es_core_news_lg`), incorporando los siguientes reconocedores personalizados basados en expresiones regulares exclusivamente para el **contexto español**:
1.  **[EsDniRecognizer](file:///C:/Users/abelvisi/Documents/Google_Drive/Mi%20unidad/M%C3%A1ster%20UNIR/IA%20Y%20Data/TFE/Entregas_TFE_Terminal/clo-author/scripts/python/pii/recognizers.py#L20):** Detecta el Documento Nacional de Identidad. Patrón principal: `\b\d{8}[A-HJ-NP-TV-Z]\b` (se omiten letras inválidas como I, O, U).
2.  **[EsNieRecognizer](file:///C:/Users/abelvisi/Documents/Google_Drive/Mi%20unidad/M%C3%A1ster%20UNIR/IA%20Y%20Data/TFE/Entregas_TFE_Terminal/clo-author/scripts/python/pii/recognizers.py#L61):** Número de Identidad de Extranjero. Patrón: `\b[XYZ]\d{7}[A-HJ-NP-TV-Z]\b`.
3.  **[EsPhoneRecognizer](file:///C:/Users/abelvisi/Documents/Google_Drive/Mi%20unidad/M%C3%A1ster%20UNIR/IA%20Y%20Data/TFE/Entregas_TFE_Terminal/clo-author/scripts/python/pii/recognizers.py#L93):** Teléfonos españoles móviles y fijos. Soporta prefijos `+34` o `0034` y patrones locales de 9 dígitos separados opcionalmente por espacios, guiones o puntos.
4.  **[EsCpRecognizer](file:///C:/Users/abelvisi/Documents/Google_Drive/Mi%20unidad/M%C3%A1ster%20UNIR/IA%20Y%20Data/TFE/Entregas_TFE_Terminal/clo-author/scripts/python/pii/recognizers.py#L134):** Códigos postales de 5 dígitos que inician entre $0$ y $5$ (`\b[0-5]\d{4}\b`). Requiere contexto explícito para evitar falsos positivos con años.

> [!NOTE]
> **No existen reconocedores adaptados al ámbito rioplatense** en el código actual (como el formato de C.I. de Uruguay o DNI/código postal de Argentina). La lógica de anonimización de identificadores documentales está orientada únicamente al ámbito de España.

---

## 3. Google Vertex AI Search — [pipeline.py](file:///C:/Users/abelvisi/Documents/Google_Drive/Mi%20unidad/M%C3%A1ster%20UNIR/IA%20Y%20Data/TFE/Entregas_TFE_Terminal/clo-author/scripts/python/rag/pipeline.py)

### Variables de Configuración en GCP
Los parámetros que consume la API de Google Vertex AI Search se definen dinámicamente o por fallbacks en [config.py](file:///C:/Users/abelvisi/Documents/Google_Drive/Mi%20unidad/M%C3%A1ster%20UNIR/IA%20Y%20Data/TFE/Entregas_TFE_Terminal/clo-author/scripts/python/config.py):
*   **Proyecto GCP:** `GCP_PROJECT_ID` (obtenido del entorno).
*   **Región/Localización:** `GCP_LOCATION` (valor por defecto: `"global"`).
*   **Data Store ID:** `GCP_DATA_STORE_ID` (valor por defecto: `"sistac-cvs-datastore"`).
*   **Search App ID:** `GCP_SEARCH_APP_ID` (por defecto `"sistac-search-app"` o `"sistac-search-app-external"` según el ambiente de datos activo).

### Aislamiento Cruzado (Cross-Isolation)
La búsqueda en Vertex AI utiliza un filtro estricto para evitar que la recuperación de información contamine el contexto con fragmentos de otros candidatos o de otras descripciones de cargo (línea 464):

```python
filter_str = f'cv_id: ANY("{cv_id}") AND jd_id: ANY("{jd_id}")'
```

Este filtro booleano compuesto (`cv_id AND jd_id`) garantiza un aislamiento absoluto de los contextos en las fases del RAG para las configuraciones C2 y C3.
