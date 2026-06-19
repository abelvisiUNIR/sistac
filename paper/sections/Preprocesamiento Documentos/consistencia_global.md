# Consistencia global del documento SISTAC

Este archivo lista los ajustes necesarios para que todo el TFE quede coherente con
el marco experimental confirmado. Se aplican sobre `paper/SISTAC_TFE.docx` y, cuando
corresponde, sobre los scripts que generan contenido del documento.

## Marco canónico (verdad única del experimento)

| Elemento | Valor canónico |
|---|---|
| Modelo evaluador (C1, C2, C3) | Claude Sonnet 4.5 |
| Corpus de currículums | Dataset público `netsol/resume-score-details` (Hugging Face), traducido al español rioplatense |
| Descripciones de cargo (JD) | Ofertas reales de Matriz Uruguay (5 perfiles, sección 5.2.3) |
| Gold Standard (APTO / NO_APTO) | Validación por el panel experto de RRHH de Matriz sobre los CV de Hugging Face; concordancia con κ de Cohen ≥ 0.70 |
| Género | Inferido del nombre por el modelo (imputado) |
| Edad y tiempos C0 | Imputados (3 rangos de edad; distribución uniforme para C0) |
| Módulo PII (C3) | Redacta PERSONA, EMAIL, TELÉFONO, DNI, NIE, CP; preserva ubicación, organización y fecha |
| Parámetros estables | chunk 512 tokens (~2048 car.), overlap 64, top-k 5, embeddings mpnet 768 dims, umbral 70, temperatura 0 |
| Tamaño del corpus y resultados | [PENDIENTE: completar tras la re-ejecución] |

## Reemplazos globales (buscar y reemplazar en todo el .docx)

| Buscar | Reemplazar por |
|---|---|
| "Claude Haiku 4.5" (como modelo evaluador del experimento) | "Claude Sonnet 4.5" |
| "Claude 3.5 Sonnet" / "Claude Sonnet" (referido al evaluador) | "Claude Sonnet 4.5" |
| "corpus sintético" / "300 CVs sintéticos" (como corpus del experimento) | "corpus de currículums de Hugging Face validado por Matriz" |
| "Gold Standard híbrido" / "etiquetado algorítmico" (como GS del experimento) | "Gold Standard validado por el panel experto de Matriz" |
| "κ de Fleiss" / "kappa de Fleiss" | "κ de Cohen" |
| "60 CVs de test" / "240 CVs de entrenamiento" / "300 CVs" | "[PENDIENTE: N del corpus]" |

## Ajustes por capítulo

### Capítulo 5 (ya escrito, 5.1 a 5.9)

| Sección | Dice actualmente | Debe decir |
|---|---|---|
| 5.2.1 (título y cuerpo) | "Fuente del corpus: Kaggle Resume Dataset… 300 CVs sintéticos calibrados" | Reencuadrar: el corpus sintético calibrado sobre Kaggle fue un artefacto de desarrollo y calibración del pipeline; el corpus de evaluación del experimento es el de Hugging Face descrito en 5.2.7 |
| 5.2.2 | "Gold Standard híbrido: etiquetado algorítmico + validación experta, κ de Cohen, 300 CVs" | Reencuadrar: el Gold Standard del experimento es la validación experta de Matriz sobre los CV de Hugging Face (detalle en Cap. 6); conservar κ de Cohen ≥ 0.70 como concordancia inter-evaluador |
| 5.2.5 | "240 CVs de entrenamiento y 5 JDs ≈ 30.000 chunks" | Sustituir N por "[PENDIENTE: N del corpus]"; mantener el método de chunking |
| 5.2.6 | "300 CVs sintéticos… 240 train / 60 test" | Reencuadrar la división train/test sobre el corpus de Hugging Face; N en "[PENDIENTE]" |
| 5.5.1 | "claude-sonnet-4-5-20241022, temperatura 0" | Correcto; unificar la cadena de modelo como "Claude Sonnet 4.5" en el texto corrido |
| 5.7.2 | Redacta también edad, género y dirección | Reemplazar por la corrección entregada en `cap5_adiciones_corpus_externo_y_dificultades.md` |
| 5.8.3 | "el corpus sintético garantiza balance perfecto 50/50" | "el corpus de evaluación mantiene balance 50/50 (75 APTO / 75 NO_APTO); el género es inferido" |
| 5.9.4 y cierre de 5.9 | "Claude Sonnet… ~8/12/15 s por CV… 60 CVs de test" | Tiempos por CV en "[PENDIENTE]"; N del corpus en "[PENDIENTE]"; conservar la lógica comparativa C0–C3 |
| 5.2.7 (nueva) | — | Insertar la sección entregada (corpus de Hugging Face + validación de Matriz) |
| 5.10 (nueva) | — | Insertar la sección de dificultades técnicas entregada |

### Capítulo 6 (a partir del borrador `framework_validacion_experimental.md`)

Reescrito en el archivo `cap6_validacion_experimental.md`. Cambios respecto al
borrador: el Gold Standard pasa de "panel de 3 expertos con anotación ciega total y
κ de Fleiss sobre 300 CVs sintéticos" a "validación experta de Matriz sobre los CV
de Hugging Face evaluados contra las JD reales de Matriz, con κ de Cohen". El modelo
evaluador es Claude Sonnet 4.5. Las métricas de H3 se estructuran por género y por
edad.

### Capítulo 7 (resultados)

Todas las cifras en `[PENDIENTE]`. Fuente de los valores tras la re-ejecución:
`paper/tables/tab_resultados_h1.csv`, `tab_resultados_h2.csv`, `tab_resultados_h3.csv`
y `eval_cache.json`. Verificar que el modelo reportado sea Claude Sonnet 4.5.

### Capítulo 8 (discusión) y 9 (conclusiones)

Coherentes con el marco canónico. Las limitaciones (Cap. 8) deben mencionar: corpus
de currículums de origen público y traducido, género inferido y edad imputada,
tiempos de C0 imputados, y Gold Standard construido por panel experto de Matriz en
modalidad piloto.

## Scripts y documentos de repositorio (consistencia técnica, opcional)

| Archivo | Ajuste sugerido |
|---|---|
| `scripts/python/figures/insert_cap5_docx.py` | Actualizar el `CONTENT` de 5.2.1, 5.2.2, 5.2.6, 5.7.2 y 5.9 según los ajustes de arriba, para que al regenerar el Cap 5 el .docx quede consistente |
| `paper/sections/analisis_resultados_tfe.md` | Cambiar "Claude Haiku 4.5" por "Claude Sonnet 4.5"; tratar las cifras como provisionales |
| `README.md` (lista de entidades PII) | Alinear con el código: nombre, email, teléfono, DNI, NIE, CP (sin edad/género/dirección) |
| `guide/rag-pipeline.qmd` (entidades PII) | Igual que README: corregir que NO se enmascaran ubicación ni organización |
| `CLAUDE.md` (estado del corpus) | Reflejar que el corpus de evaluación es el de Hugging Face validado por Matriz |

*Nota.* Elaboración propia. Este archivo es la referencia maestra de consistencia;
ante cualquier duda entre el .docx y el código, prevalece el marco canónico de la
primera tabla.
