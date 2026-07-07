# Guía de Integración para el Capítulo 6 (Discusión y conclusiones)

Esta guía detalla los cambios puntuales necesarios para subsanar las últimas observaciones de la tutora en la **Sección 6.1 (Discusión)** y la **Sección 6.2 (Conclusiones)** del **Capítulo 6** de tu Word. Las ubicaciones están marcadas con el número de párrafo correspondiente del documento extraído para facilitar un copiado y pegado directo y localizado sin reescribir bloques innecesarios.

---

## 1. Ajustes en la Sección 6.1 (Discusión de los resultados)

### A. Subsección 6.1.2 (Eficacia técnica)
* **Ubicación:** Busca el párrafo **P730** (originalmente el párrafo que empieza por *"Este comportamiento demuestra que el modelo es sumamente estricto..."*) y **reemplázalo** por este texto, el cual utiliza la citación parenthetical ordenada alfabéticamente bajo los estándares de APA 7:

```text
Este comportamiento demuestra que el modelo es sumamente estricto y conservador cuando evalúa la adecuación curricular. El mantenimiento de valores elevados de AUC-ROC (~0.73) confirma que el sistema ordena y jerarquiza a los candidatos de forma adecuada según su nivel de competencia, lo que denota una buena capacidad de ranking (útil para priorizar candidatos). Sin embargo, el F₁-score macro absoluto queda lejos de los benchmarks de referencia previos en inglés (Bevara et al., 2025; Liu, 2025), donde se reportan F₁-scores superiores a 0.85. Esta distancia se atribuye al proceso de localización y traducción del corpus al español rioplatense (que introduce distorsiones semánticas sutiles), a la rigurosidad extrema en la evaluación de idoneidad del panel experto de Matriz, y a la baja sensibilidad (recall) de solo 28.0% provocada por el umbral rígido original de 70 puntos, el cual es excesivo para la escala de scores generada por el LLM. Al recalibrar el umbral al punto óptimo obtenido por Youden (umbrales entre 34 y 48 puntos), el F₁-score asciende de forma muy significativa hasta alcanzar un valor de 0.697 (C1), 0.693 (C2) y 0.691 (C3), evidenciando que la brecha de eficacia responde a la calibración del punto de corte binario fijo y no a una falta de capacidad discriminativa del modelo.
```

### B. Subsección 6.1.3 (Equidad)
* **Ubicación:** Busca el párrafo con viñeta **P735** (originalmente el punto 1 que empieza por *"La persistencia de señales indirectas y concordancias de género..."*) y **reemplázalo** por este texto, que amplía la mitigación por proxies en equidad (concordancia, trayectorias, instituciones y roles):

```text
1. La persistencia de señales indirectas y variables proxies de género: El módulo de anonimización enmascara nombres propios y datos de contacto directos, pero preserva la sintaxis y construcciones gramaticales de origen. En el idioma español, la flexión de género en adjetivos y sustantivos (por ejemplo, redactora, ingeniera, graduado, programadora) sigue indicando de forma implícita el género del postulante, permitiendo al LLM inferir esta variable. A esto se suma el sesgo indirecto introducido por variables proxies que no son de carácter personal pero están altamente correlacionadas con el género, tales como brechas temporales en la trayectoria laboral asociadas históricamente al cuidado familiar, nombres de colegios o instituciones educativas históricamente segregadas por género, y la naturaleza de la experiencia previa en roles ocupacionales con sesgos de distribución demográfica tradicionales en el mercado local (por ejemplo, soporte administrativo frente a desarrollo de infraestructura técnica). El modelo conserva la capacidad de asociar semánticamente estos patrones contextuales indirectos, perpetuando el sesgo en el score final.
```

---

## 2. Ajustes en la Sección 6.2 (Conclusiones y trabajo futuro)

### A. Matriz de objetivos específicos
* **Ubicación:** Ve al título de la sección **6.2. Conclusiones y trabajo futuro** (párrafo **P746**). Sitúate inmediatamente debajo de la subsección **6.2.1. Respuesta a la pregunta de investigación** (después del párrafo **P752** que termina con *«...de forma empírica.»*) e **inserta** el siguiente título y tabla:

```text
6.2.2. Matriz de cumplimiento de objetivos específicos

Para contrastar el grado de éxito de la investigación, la Tabla 28 presenta la matriz de cumplimiento metodológico, enlazando cada uno de los objetivos específicos definidos en el Capítulo 3 con su resultado empírico y su conclusión asociada.

Tabla 28. Matriz de cumplimiento de objetivos específicos de la investigación.

| Objetivo Específico (OE) | Resultado Empírico Obtenido | Grado de Cumplimiento | Evidencia en la Memoria | Conclusión Metodológica Asociada |
| :--- | :--- | :--- | :--- | :--- |
| **OE1 (Corpus):** Construir corpus de calibración (300) y validación (150). | Dataset de 300 casos y muestra de 150 CVs reales traducidos y localizados. | **Total** | Tablas 4.2 (Cap. 4) e Historial de MongoDB. | La estrategia de datos mixta garantizó privacidad en el desarrollo y realismo físico en el experimento. |
| **OE2 (RAG & RAGAS):** Implementar RAG y evaluar calidad contextual. | Pipeline en C2 logrando Faithfulness = 0.82 y Context Precision = 0.87 en RAGAS. | **Total** | Resultados reportados en Tabla 19 (Cap. 5). | El pipeline RAG garantiza que el modelo decida con base en la información real del cargo, mitigando alucinaciones. |
| **OE3 (Módulo PII):** Desarrollar enmascarador de PII (≥ 0.95). | Enmascarador robusto con spaCy y Presidio verificando F1-score = 1.000 en el piloto. | **Total** | Tabla 10 de Validación de PII (Cap. 4). | El enmascaramiento de PII directo es sumamente preciso, logrando la remoción completa de datos identificadores directos. |
| **OE4 (Gold Standard):** Conformar panel y verificar acuerdo (≥ 0.70). | Tres expertos de Matriz consensuaron la muestra con un acuerdo medio de κ = 0.76. | **Total** | Matriz de concordancia inter-evaluador (Cap. 5). | El panel de RRHH estableció una referencia de alta consistencia interna, validando la legitimidad del Gold Standard. |
| **OE5 (Experimento):** Procesar corpus y medir eficiencia y eficacia. | Procesamiento en C1-C3 midiendo latencia, F1-macro y AUC-ROC. | **Total** | Tablas de eficiencia y eficacia (Cap. 5). | H1 se acepta (reducción masiva de tiempos), pero H2 se rechaza debido a que F1 queda por debajo del umbral base rígido de 70. |
| **OE6 (Equidad):** Calcular DIR/SPD por género/edad y contrastar. | Cálculo de DIR/SPD por subgrupos y pruebas estadísticas de Fisher. | **Total** | Tablas de equidad e intervalos de confianza (Cap. 5). | H3 se rechaza; la anonimización de PII directas resulta insuficiente ante la presencia de proxies demográficos. |

Fuente: Elaboración propia.
```

### B. Matización de Conclusiones de H2 y H3
* **Ubicación:** En la subsección **6.2.2. Conclusiones por hipótesis** (que ahora pasa a ser **6.2.3** tras insertar la matriz de objetivos), busca las viñetas **P755** (Eficacia) y **P756** (Equidad) y **reemplázalas** por estos textos matizados:

```text
* Hipótesis de eficacia (H2): Se rechaza. Las configuraciones automáticas basadas en recuperación semántica (C2 y C3) no lograron alcanzar el umbral de aceptación del F₁-score macro ≥ 0.85 frente al Gold Standard experto (registrando un F₁ de 0.519 en C2 y 0.539 en C3). Se concluye que el sistema es un valioso asistente de priorización y ordenamiento (ranking) para agilizar la lectura, pero no es viable como decisor binario autónomo bajo cortes fijos.
* Hipótesis de equidad (H3): Se rechaza. La anonimización de PII directas (C3) no mitigó de forma efectiva el impacto dispar por género respecto a las configuraciones no anonimizadas, reduciendo el DIR por género de 0.602 (C2) a 0.301 (C3), debido a la persistencia de variables proxies de género. Esto subraya que la supresión de datos identificadores de contacto directos es insuficiente para neutralizar el sesgo indirecto semántico.
```

### C. Sección de Recomendaciones Institucionales
* **Ubicación:** Justo **antes** de la sección **Contribuciones del trabajo** (párrafo **P757**), **inserta** esta nueva sección:

```text
6.3. Recomendaciones prácticas e institucionales para la organización Matriz

A partir de las limitaciones observadas y el comportamiento empírico del sistema, se proponen cuatro recomendaciones institucionales para la implementación de modelos de lenguaje en sus procesos de adquisición de talento:
1. **Prohibición de descarte algorítmico autónomo:** El software no debe emplearse como un filtro de exclusión automática (automatic rejection) debido a su bajo desempeño binario en umbrales prefijados.
2. **Uso complementario en ranking asistido:** Se recomienda utilizar los scores numéricos generados únicamente como criterio complementario de ordenamiento para agilizar la lectura secuencial de perfiles por parte de los selectores humanos.
3. **Calibración dinámica de umbrales Youden:** La organización debe evitar el uso de puntos de corte rígidos (como el umbral de 70 puntos) y calibrar empíricamente los umbrales de decisión de forma adaptativa para cada cargo o vacante específica.
4. **Logs y auditorías periódicas de sesgo:** Registrar las puntuaciones y decisiones automatizadas en bases de datos con control de accesos para realizar auditorías semestrales de impacto dispar (DIR) que controlen la deriva algorítmica.
```

### D. Reorganización de títulos (Separación Conclusiones y Trabajo Futuro)
* **Ubicación:** Modifica los siguientes títulos de las subsecciones de conclusiones para adaptarlas a la separación y reindexarlas correctamente:
  * Cambiar el título **6.2.3. Contribuciones del trabajo** por **6.4. Contribuciones del trabajo**.
  * Cambiar el título **6.2.4. Trabajo futuro** por **6.5. Limitaciones del estudio y Trabajo futuro**.
