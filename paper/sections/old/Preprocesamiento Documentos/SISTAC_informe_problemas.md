# INFORME DE REVISIÓN CRÍTICA — TFE SISTAC

**Fecha:** 23/06/2026
**Documento revisado:** `Optimizacion_del_Proceso_de_Seleccion_de_Talento grupo 4 ESIT.docx` (versión subida en esta sesión; 52 páginas, ~29 558 palabras)
**Capítulos revisados:** Front matter + Cap 0 (Organización) y Capítulos 1 a 6
**Ejes aplicados:** Voz/anti-IA · Notación · Estructura/completitud · Métricas/texto · Bibliografía · Código en prosa

---

## 0. NOTA METODOLÓGICA — LEER PRIMERO

El documento activo **no coincide con la estructura de 6 capítulos numerados (Cap 0–6)** que asumía el prompt de la sesión. La organización real es:

- **Front matter:** Portada · Resumen · Abstract · Índices (contenidos, figuras, tablas) · "Organización del trabajo en grupo" (Cap 0, sin numerar).
- **Cap 1** Introducción · **Cap 2** Estado del arte · **Cap 3** Objetivos y Metodología · **Cap 4** Arquitectura e implementación (que **absorbe** lo que el prompt llamaba "Cap 5: Pipeline RAG, scoring y PII") · **Cap 5** Validación experimental **y resultados** · **Cap 6** Discusión y conclusiones.

Tres diagnósticos previos del prompt están **desactualizados** respecto a este archivo y se corrigen en este informe:

1. **La sección de Referencias NO está vacía** (tiene 9 entradas APA), pero está **gravemente incompleta** (faltan ~24 obras citadas). Ver Eje E.
2. **El vector store ya figura como Google Vertex AI Search** en el cuerpo (sección 4.3.3). "Azure" solo sobrevive en dos pies del índice de figuras.
3. La mayoría de los autores que el prompt listaba como "mencionados sin paréntesis" **hoy ya tienen cita parentética** (Liu, Bevara, Fu, Lavi, Afzal, Staab, Deshpande, Bruera, Skondras, Saldivar, Wilson y Caliskan, An, Ip, Albaroudi…). El problema con ellos ya no es el formato de cita sino la **ausencia de entrada bibliográfica**.

**Buena noticia transversal (Eje D):** los valores numéricos del texto **coinciden con los CSVs**. No se detectó ninguna métrica errónea ni placeholder "X.XX" en el cuerpo de resultados.

---

## TABLA RESUMEN DE MÉTRICAS REALES (de los CSVs)

Los tres juegos de CSVs corresponden a: **`paper/tables/` (raíz) = `anthropic/` = Claude Sonnet 4.5 (evaluador principal)**; **`google/` = Gemini 2.5 Flash (réplica de robustez)**; **`results/experimento_google_fallback/` = mismos valores que `google/`** (indexación local de respaldo). El texto reporta Claude como resultado principal y Gemini en la sección 5.10 de robustez.

### Resultado principal — Claude Sonnet 4.5

| Métrica | C0 | C1 | C2 | C3 |
|---|---|---|---|---|
| T_cand mediana (s) | 661.8 | 4.5 | 6.8 | 19.6 |
| Speedup vs C0 | — | 147.8× | 96.7× | 33.7× |
| F₁ macro | — | 0.565 | 0.519 | 0.539 |
| AUC-ROC | — | 0.732 | 0.735 | 0.729 |
| DIR género | — | 0.326 | 0.602 | 0.301 |
| SPD género | — | -0.122 | -0.078 | -0.137 |

### Réplica de robustez — Gemini 2.5 Flash

| Métrica | C0 | C1 | C2 | C3 |
|---|---|---|---|---|
| T_cand mediana (s) | 661.8 | 21.6 | 24.6 | 28.9 |
| Speedup vs C0 | — | 30.6× | 26.9× | 22.9× |
| F₁ macro | — | 0.567 | 0.494 | 0.587 |
| AUC-ROC | — | 0.665 | 0.629 | 0.695 |
| DIR género | — | — | 1.397 | 0.447 |
| SPD género | — | — | 0.084 | -0.145 |

**RAGAS (C2):** faithfulness 0.910 · answer_relevancy 0.880 · context_precision 0.850. ✔ Coinciden con el texto (§5.7).

**Observación sustantiva (no es un error de transcripción):** en ambos modelos, **H2 no alcanza los umbrales** (F₁ ≥ 0.85, AUC ≥ 0.90) y **H3 empeora de C2 a C3** (la anonimización aleja el DIR del umbral). El documento ya reconoce y discute esto correctamente (§5.7, §5.8, §6.1.2, §6.1.3). No hay que "corregir" las cifras; sí conviene revisar que el marco de hipótesis y las conclusiones sean coherentes con un resultado mayormente negativo (ver Eje C, Cap 5/6).

---

## FIGURAS / TABLAS — ESTADO

- Los gráficos de resultados generados por Python **existen** en disco y se corresponden con las Figuras 18–20 del texto:
  - `fig6_2_distribucion_tiempos.png` → Figura 18 (distribución T_cand) ✔ (existe en `cap6/`, `cap6/anthropic/`, `cap6/google/`)
  - `fig6_3_curva_roc.png` → Figura 19 (curva ROC) ✔
  - `fig6_4_impacto_dispar.png` → Figura 20 (DIR por género) ✔
- **El Índice de figuras está completamente desincronizado del cuerpo** (ver [ESTRUCTURA-F1]). Lista 8 figuras (Figura 3 a 10) con títulos que **no coinciden** con los del cuerpo, que numera del 1 al 21.
- **El Índice de tablas solo lista Tabla 1 y Tabla 5**, y la página de Tabla 1 aparece como placeholder "**X**". El cuerpo referencia hasta Tabla 16.
- Las tablas de datos (Tabla 2 a 16) **no son tablas nativas de Word** (python-docx detecta una sola tabla: la portada). Se insertaron como imágenes desde Excel, lo cual es coherente con el flujo del proyecto, pero obliga a regenerar manualmente los índices.

---

## ⚠️ ALERTA CRÍTICA 1: REFERENCIAS BIBLIOGRÁFICAS INCOMPLETAS

La sección "Referencias bibliográficas" contiene **solo 9 entradas** para un documento que cita **~33 obras**. Faltan ~24 entradas. **Esta es la incidencia más grave del documento de cara a la entrega.**

### Entradas presentes (9) — correctas en formato APA
Abhishek et al. (2025) · EU AI Act / Reglamento 2024/1689 (2024) · Gan et al. (2024) · González-González & Herrera (2025) · Goodman (2025) · Ley 18.331 (2008) · Marr & Ward (2019) · New York City Local Law 144 (2023) · Thomas & Reimann (2023).

### Autores citados en el texto SIN entrada en Referencias (completar antes de entregar)
Mario y David deben crear la entrada APA de cada uno (el `.bib` del repo tiene algunos, pero con campos `TODO` y claves desalineadas):

- Vanetik & Kogan (2023) — §2.1
- Liu (2025) — §2.1, §2.2
- Bevara et al. (2025) — §2.2  *(en `Resume2Vec2025` del .bib falta el autor)*
- Fu et al. (2025) — §2.2  *(LANTERN; en .bib como `Fu2025_lantern`, con TODO)*
- Lavi et al. (2021) — §2.2  *(conSultantBERT; no está en el .bib)*
- Dasaklis et al. (2025) — §2.2, §2.3, §2.7  *(no está en el .bib)*
- Lo et al. (2025) — §2.3, §4.4  *(en .bib como `Lo2025_multiagent_rag`, con TODO)*
- Afzal et al. (2025) — §2.3  *(en .bib como `Afzal2025_rag_ner`, con TODO)*
- Lewis et al. (2020) — fuente de la Figura 2, §2.3  *(en .bib como `Lewis2020`, completo)*
- Staab et al. (2023) — §2.4  *(no está en el .bib)*
- Deshpande et al. (2020) — §2.4  *(no está en el .bib)*
- Bruera et al. (2022) — §2.4  *(en .bib como `Bruera2022_privbayes_cv`)*
- Skondras et al. (2023) — §2.4  *(en .bib como `Skondras2023_synthetic_bert`)*
- Saldivar et al. (2025) — §2.4  *(en .bib como `Saldivar2025_synthetic_cvs`)*
- Raghavan et al. (2020) — §2.5, §2.7
- Wilson & Caliskan (2024) — §2.5, §2.7, §2.8  *(en .bib como `Wilson2024_llm_hiring_bias`)*
- An et al. (2025) — §2.5, §2.7, §2.8  *(no está en el .bib)*
- Ip (2025) — §2.5, §2.8  *(no está en el .bib)*
- Albaroudi et al. (2025) — §2.5, §2.8  *(no está en el .bib)*
- U.S. EEOC (1978) — §2.5, §5.3.3
- Ley N.° 16.045 (1989) — §2.5  *(Uruguay, igualdad de trato en el empleo)*
- Schröer et al. (2021) — §3.3
- Chapman et al. (2000) — §3.3 (fuente de Tabla 2 y Figura 4 de CRISP-DM)
- Bangura et al. (2025) — §2.7

> Adicional: el texto menciona "el benchmark **JobFair** de Holistic AI" (§2.5) con datos concretos; si se conserva, requiere su propia entrada (en el .bib aparece como `JobFair2024_gpt_bias`, con autores `TODO`).

---

## ⚠️ ALERTA CRÍTICA 2: RESUMEN Y ABSTRACT SIN CUERPO DE TEXTO

[FALTANTE CRÍTICO] Las secciones **Resumen** y **Abstract** contienen **únicamente el título y la línea de palabras clave / keywords**; **no hay texto de resumen** en ninguna de las dos. La plantilla UNIR exige un resumen de 150–300 palabras y su traducción al inglés. Deben redactarse antes de la entrega.

---

## ⚠️ ALERTA CRÍTICA 3: PORTADA INCOMPLETA PARA UN TFE GRUPAL

[ESTRUCTURA] La tabla de portada presenta el trabajo a nombre de **"Mario Agustín Belvisi Lescano"** únicamente. Siendo un TFE grupal de **dos** autores, **David Ilich Madrid Oyanadel no figura en la portada**. Verificar y añadir ambos autores.

---

## CAP 0 — Organización del trabajo en grupo

- [ESTRUCTURA — menor] La "Tabla 1. Organización del trabajo en grupo" aparece en el índice de tablas con número de página **"X"** (placeholder). Verificar que la tabla de responsabilidades exista en el cuerpo con sus cuatro columnas y regenerar el índice.
- [VOZ — leve] Estructura y registro adecuados, sin tics de IA marcados. El apartado es proporcionado y describe división de trabajo, objetivos de aprendizaje y coordinación. No requiere reescritura.
- ✔ La división por líneas (David: RAG/scoring; Mario: PII/equidad) es coherente con el resto del documento.

---

## CAP 1 — Introducción

- ✔ [ESTRUCTURA] **No** menciona "SISTAC" (verificado: 0 apariciones en Cap 1). Usa "el sistema propuesto", "el presente trabajo". Correcto.
- ✔ [ESTRUCTURA] **No** usa etiquetas H1/H2/H3 en la prosa de este capítulo; las hipótesis se enuncian en lenguaje natural (§1.2, párr. "se espera que… se plantea que… se sostiene que…"). Correcto.
- ✔ [EMBUDO] El patrón contexto→problema→enfoque se respeta en §1.1 (Motivación) y §1.2.
- [ANTI-IA — em-dash] Párrafo de "Motivación" sobre sesgos cognitivos: *"Los sesgos cognitivos del evaluador —entre ellos el affinity bias, el halo effect y el primacy effect (Thomas & Reimann, 2023) — contaminan…"*. Reemplazar los guiones largos por paréntesis o coma: *"(entre ellos el affinity bias, el halo effect y el primacy effect; Thomas & Reimann, 2023)"*.
- [BIBLIOGRAFÍA] Las citas de este capítulo (Goodman 2025; Abhishek et al. 2025; Marr & Ward 2019; Thomas & Reimann 2023; González-González & Herrera 2025; Gan et al. 2024; EU AI Act 2024; Local Law 144 2023; Ley 18.331 2008) **sí tienen entrada** en Referencias. Capítulo limpio en este eje.

---

## CAP 2 — Estado del arte y fundamentos teóricos

- ✔ [ESTRUCTURA] No menciona "SISTAC" ni etiquetas H1/H2/H3 en prosa. La sección de cierre (§2.7 y §2.8) conecta la literatura con las decisiones de diseño y la brecha. Correcto.
- [BIBLIOGRAFÍA — crítico] Es el capítulo con **más citas sin entrada en Referencias**: Vanetik & Kogan (2023), Liu (2025), Bevara et al. (2025), Fu et al. (2025), Lavi et al. (2021), Dasaklis et al. (2025), Lo et al. (2025), Afzal et al. (2025), Lewis et al. (2020), Staab et al. (2023), Deshpande et al. (2020), Bruera et al. (2022), Skondras et al. (2023), Saldivar et al. (2025), Raghavan et al. (2020), Wilson & Caliskan (2024), An et al. (2025), Ip (2025), Albaroudi et al. (2025), U.S. EEOC (1978), Ley N.° 16.045 (1989), Bangura et al. (2025). Ver lista consolidada en la Alerta Crítica 1.
- [BIBLIOGRAFÍA — verificación específica] **Lewis et al. (2020)** aparece ahora correctamente en el pie de la Figura 2 (*"Fuente: elaboración propia a partir de Lewis et al. (2020) y Dasaklis et al. (2025)"*). Falta su entrada en Referencias (el `.bib` ya la tiene completa).
- [NOTACIÓN — separador decimal] El capítulo usa **coma decimal** (F₁ = 0,716; 0,757; 0,910; nDCG 15,85 %) mientras que los capítulos 5 y 6 usan **punto decimal** (0.565, 0.519). Unificar a un único criterio en todo el documento (la convención en español es la coma; si se mantiene el punto por compatibilidad con las tablas de resultados, aplicarlo también aquí).
- [ANTI-IA — enumeración paralela] §2.1: tres párrafos consecutivos abren con la misma plantilla *"En la dimensión operativa… / En la dimensión técnica… / En la dimensión ética…"*. Variar los conectores y encadenar con subordinación para romper la simetría.
- [VOZ — aceptable] Cada párrafo tiene ≥ 3 oraciones; densidad de cita adecuada. Salvo la enumeración anterior, la textura es buena.

---

## CAP 3 — Objetivos y Metodología

- ✔ [ESTRUCTURA] No hay sección de "hipótesis formales" separada de nivel doctoral; las hipótesis viven en Cap 1/Cap 5. Los objetivos específicos usan etiquetas [OE1]–[OE6], lo cual es correcto y no entra en conflicto con la restricción de H1/H2/H3.
- [NOTACIÓN — separador decimal] Igual que Cap 2: recall@10 "0,80" y precisión/recall "≥ 0,95" con coma, frente al punto de Cap 5–6. Unificar.
- [ESTRUCTURA — numeración duplicada de tablas] Existe **dos veces "Tabla 2"**: "Tabla 2. Síntesis de la literatura" (Cap 2, §2.7) y "Tabla 2. Adaptación de CRISP-DM" (Cap 3, §3.3). Renumerar para que cada tabla tenga un número único.
- [ESTRUCTURA — redundancia figura/tabla] El mismo contenido CRISP-DM aparece como "Tabla 2. Adaptación de CRISP-DM" y como "Figura 4. Adaptación de CRISP-DM". Decidir si va como tabla o como figura, no ambas con el mismo título.
- [VOZ — aceptable] Capítulo breve y funcional, sin tics marcados.

---

## CAP 4 — Arquitectura e implementación del sistema

> Este capítulo concentra el grueso de las incidencias del **Eje F (código en prosa)**.

### [CÓDIGO EN PROSA] — convertir a descripción funcional

Casos detectados (nombre de archivo/clase/constante embebido en prosa corrida; la regla es: describir la función y, si el identificador es imprescindible, dejarlo entre paréntesis o en cursiva, nunca como sujeto ni en bloque de código dentro del párrafo):

- §4.2.4: *"implementadas en el archivo `data/doc_extractor.py`"* → *"implementadas en el módulo de extracción de texto"*.
- §4.2.2: *"procesado mediante un script en Python (`data/prepare_external_validation.py`)"* → describir el procedimiento; el nombre del script, si se conserva, entre paréntesis o en nota al pie.
- §4.3.1 (Principios de diseño): *"utilizan la semilla `RANDOM_SEED = 42`"* → *"utilizan una semilla fija de valor 42 para garantizar la reproducibilidad"*.
- §4.4 (Motor de scoring): *"La implementación se encuentra en `scoring/scorer.py`"* → eliminar o llevar a nota; describir funcionalmente.
- §4.4: *"El umbral… se fija en setenta puntos (`SCORE_THRESHOLD = 70`), definido en `config.py`"* → *"El umbral de clasificación binaria se fija en 70 puntos"* (la constante y el archivo, a nota al pie si son imprescindibles).
- §4.5 (PII): *"La implementación se encuentra en `pii/anonymizer.py` mediante la clase `SistacAnonymizer`"* → *"El módulo de anonimización (denominado SistacAnonymizer) gestiona…"*; nombre del archivo a nota.
- §4.5: tipos de entidad `PERSON`, `ORG`, `LOC`, `DATE` como literales → describir ("entidades de persona, organización, ubicación y fecha").
- §4.3.3: variables de entorno `GCP_PROJECT_ID`, `GCP_LOCATION`, `GCP_DATA_STORE_ID`, `GCP_SEARCH_APP_ID`, `VECTORSTORE_PROVIDER`, valores `global`, `sistac-cvs-datastore`, etc. → este nivel de detalle de configuración pertenece al Anexo de código, no al cuerpo. Resumir funcionalmente.
- §5.3 (métricas): *"implementadas en los módulos `efficiency_metrics.py`, `efficacy_metrics.py` y `fairness_metrics.py`"* y *"`scipy.stats` y `scikit-learn`"* → describir; nombres de archivo al Anexo.
- §4.6 (dificultades): `paraphrase-multilingual-MiniLM-L12-v2`, `eval_cache.json` → describir.

**Nombres de modelo/dataset que SÍ pueden conservarse** (identifican unívocamente el componente), pero en cursiva o comillas, no en bloque de código: *paraphrase-multilingual-mpnet-base-v2*, *es_core_news_lg*, *RecursiveCharacterTextSplitter*, *netsol/resume-score-details*.

### [CÓDIGO EN PROSA — pie de figura]
- El **título de la Figura 4 en el índice** dice *"Estrategia de extracción de texto según formato de archivo **(doc_extractor.py)**"*. Quitar el nombre de archivo del título. (El pie en el cuerpo, §4.2.4, ya está corregido: *"Figura 7. Estrategia de extracción de texto según formato de archivo"*, sin el archivo — pero ver el problema de numeración abajo.)

### [ESTRUCTURA-F1] Índice de figuras desincronizado y referencias a Azure
- El **Índice de figuras es obsoleto**: lista 8 figuras (Figura 3–10) cuyos títulos no coinciden con los del cuerpo (que numera Figura 1–21). Hay que **regenerar el índice** (actualizar campos en Word) tras fijar la numeración.
- [NOTACIÓN — Azure] Persisten **dos referencias a "Azure AI Search"** en el índice de figuras: *"Figura 5. … índice vectorial en Azure AI Search"* y *"Figura 6. … indexación y evaluación en Azure AI Search"*. El cuerpo (§4.3.3) ya describe correctamente **Google Vertex AI Search** y presenta Azure como la alternativa **descartada**. Corregir esos dos títulos a Vertex AI Search.

### [ESTRUCTURA] Numeración de figuras inconsistente y un pie duplicado
- El cuerpo reusa numeración: Cap 2 usa "Figura 1, 2, 3"; Cap 3 "Figura 4"; Cap 4 arranca en "Figura 5" y llega hasta "Figura 14"; Cap 5 sigue 15–21. Pero el índice (auto) arranca en "Figura 3 = Arquitectura general". La numeración del cuerpo y la del índice no son el mismo sistema. Reconciliar.
- **Pie duplicado:** "Figura 12" (§4.4, umbral/output del scoring) repite literalmente el título de la Figura 11: *"Figura 12. Flujo completo del pipeline RAG: fases de indexación y evaluación."* Debe llevar un título propio (p. ej., estructura del output del modelo).

### Aciertos del capítulo
- ✔ El párrafo introductorio (§4, párr. inicial) es "qué y por qué" sin funnel narrativo. Correcto para capítulo de contribución.
- ✔ El stack describe **Vertex AI Search** (no Azure) en el cuerpo, con justificación de costo, indexación asíncrona e integración con Gemini.
- ✔ El uso de "SISTAC" aquí **está permitido** (Tabla 6, SistacAnonymizer, Tabla 7).
- [ANTI-IA — enumeración paralela, menor] §4.3.1: *"El primero es la modularidad… El segundo es la reproducibilidad… El tercero es la escalabilidad… El cuarto es la privacidad por diseño…"*. Aceptable para principios de diseño, pero podría encadenarse con mayor variación si se desea pulir.

---

## CAP 5 — Validación experimental y resultados

- ✔ [MÉTRICAS] **Todos los valores del texto coinciden con los CSVs** (Claude principal y Gemini robustez). Verificado uno a uno: T_cand 661.8/4.5/6.8/19.6; speedups 147.8×/96.7×/33.7×; F₁ 0.565/0.519/0.539; AUC 0.732/0.735/0.729; DIR género 0.326/0.602/0.301; SPD -0.122/-0.078/-0.137; RAGAS 0.910/0.880/0.850; réplica Gemini completa. **Sin [MÉTRICA ERRÓNEA] ni [PLACEHOLDER].**
- ✔ [NOTACIÓN] κ = 0.76 citado correctamente (§5.2), con umbral κ ≥ 0.70. F₁, AUC-ROC, DIR, SPD, T_cand, C0–C3 con notación consistente.
- [VALOR SIN FUENTE EN CSV — menor] Los **DIR por rango de edad** (§5.8 y §6.1.3: C2 0.727/0.818, C3 0.636/0.818; Gemini 0.667→0.857) y los recuentos del subgrupo femenino (n=17; 2/17 y 1/17) **no aparecen en los CSVs revisados** (`tab_resultados_h3.csv` solo trae el DIR/SPD de género agregado para C2 y C3). Probablemente se calculan al vuelo, pero conviene **persistir un CSV de equidad por edad** y de recuentos para trazabilidad y reproducibilidad (coherente con INV-W2/INV-11).
- [ESTRUCTURA — etiquetas H1/H2/H3 en prosa] El capítulo usa de forma **intensiva** las etiquetas literales "H1", "H2", "H3" en títulos y cuerpo (p. ej. §5.3.1 "Hipótesis 1" está bien, pero las tablas y notas dicen "(H1)", "(H2)", "(H3)"). El prompt pide no usar "H1/H2/H3" en prosa de ningún capítulo. Es una decisión de estilo del equipo: si se mantiene la convención, al menos unificarla; si se quiere cumplir la restricción, sustituir por "la hipótesis de eficiencia/eficacia/equidad".
- [ESTRUCTURA — fusión Cap 5+6 del prompt] Este capítulo integra correctamente diseño experimental, Gold Standard, métricas, suite estadística y resultados. La sección de robustez (§5.10) con Gemini está bien situada y rotulada.
- [VOZ] §5.1: *"La configuración C0 corresponde… C1 automatiza… C2 incorpora… C3 extiende…"* es una enumeración paralela, pero en la descripción de condiciones experimentales resulta funcional y clara; no requiere reescritura.

---

## CAP 6 — Discusión y conclusiones

- ✔ [ESTRUCTURA — completitud] **Existe** capítulo de Discusión, Limitaciones, Conclusiones por hipótesis, Contribuciones y Trabajo futuro. **No aplica el [FALTANTE CRÍTICO] de conclusiones** que anticipaba el prompt: están presentes y bien desarrolladas.
- ✔ La discusión interpreta correctamente los resultados negativos de H2 y H3 (carácter conservador del modelo, truncamiento del contexto en RAG, persistencia de señales de género por la flexión del español, inestabilidad del DIR con n=17). Análisis honesto y sólido.
- [ESTRUCTURA — etiquetas H1/H2/H3] Igual que Cap 5: los títulos §6.1.1–6.1.3 y las conclusiones §6.2.2 usan "H1/H2/H3" literalmente. Misma recomendación.
- [ANTI-IA — em-dash] Los tres subtítulos/aperturas de §5.10 y la discusión usan guion largo: *"H1 — Eficiencia"*, *"H2 — Eficacia técnica"*, *"H3 — Equidad algorítmica"*. Sustituir por dos puntos: *"Eficiencia (H1):"* o *"H1, eficiencia:"*.
- [ESTRUCTURA — "Estructura del trabajo" desactualizada] La sección §1.3 (en Cap 1) describe los capítulos con nombres que **ya no coinciden** con el documento final: llama al Cap 3 *"Estrategia de investigación"* (su título real es "Objetivos y Metodología") y ubica *"el módulo de anonimización de PII"* y *"el marco de métricas de equidad"* dentro del **Capítulo 5**, cuando en el documento final el módulo PII está descrito en el **Capítulo 4**. Actualizar §1.3 para que el mapa de capítulos refleje la organización real.
- [VOZ — aceptable] La textura de Cap 6 es buena; redacción argumentativa, poco templada. No requiere reescritura por voz.
- ✔ El uso de "SISTAC" aquí está permitido (§6.2.1, §6.2.4).

---

## RESUMEN EJECUTIVO

| Cap | Anti-IA | Notación | Estructura | Métricas | Bibliografía | Código en prosa | ¿Requiere .md corregido? |
|---|---|---|---|---|---|---|---|
| Front matter | — | — | **Crítico** (Resumen/Abstract vacíos; portada 1 autor) | — | — | — | No (faltan textos por redactar) |
| 0 Organización | OK | — | Menor (página "X" Tabla 1) | — | — | — | No |
| 1 Introducción | Leve (1 em-dash) | OK | OK | — | OK | — | Opcional |
| 2 Estado del arte | Leve (enum. paralela) | Coma vs punto | OK | — | **Crítico** (~22 citas sin entrada) | — | Sí (voz menor) |
| 3 Objetivos/Metod. | OK | Coma vs punto | Menor (Tabla 2 duplicada) | — | OK | — | No |
| 4 Arquitectura | Leve | **Azure en índice** | Índice figuras desfasado; pie Fig.12 dup. | — | OK | **Crítico** (muchos casos) | Sí |
| 5 Validación/Result. | OK | H1/H2/H3 prosa | OK | ✔ Coinciden | OK | Leve (nombres de módulo) | No |
| 6 Discusión/Concl. | Leve (em-dash) | H1/H2/H3 prosa | §1.3 desactualizada | ✔ Coinciden | OK | — | Opcional |

### Prioridades de cara a la entrega (15 jul 2026)
1. **Completar las ~24 referencias faltantes** (bloqueante; viola INV-W4).
2. **Redactar Resumen y Abstract** (150–300 palabras + traducción).
3. **Añadir a David en la portada.**
4. **Limpiar código en prosa del Cap 4** y mover detalle de configuración al Anexo.
5. **Corregir "Azure" → "Vertex AI Search"** en los dos títulos del índice de figuras y **regenerar índices** (figuras y tablas) con numeración única.
6. Renumerar tablas/figuras duplicadas (dos "Tabla 2"; pie repetido en "Figura 12").
7. Unificar separador decimal (coma vs punto) en todo el documento.
8. (Recomendado) Persistir CSV de equidad por edad y recuentos por subgrupo.

### Sobre los capítulos corregidos (.md)
Según lo acordado ("informe primero"), este entregable es solo el diagnóstico. Los capítulos que justifican un `cap_N_corregido.md` por problemas de **voz/textura** son el **Cap 2** (enumeración paralela §2.1, em-dashes, decimal) y el **Cap 4** (reescritura de los pasajes con código en prosa). El resto se resuelve con ediciones puntuales descritas arriba, sin reescritura completa. Avisá si querés que genere esos dos `.md`.
