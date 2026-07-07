# PUNTOS DE MEJORA — TFE SISTAC
Fecha: 23/06/2026 · Complementa a `SISTAC_informe_problemas.md` (que cubre errores y faltantes). Aquí van mejoras **de fondo** que elevarían la calidad de la defensa, ordenadas por impacto.

---

## A. Mejoras de fondo (impacto alto)

### 1. Reencuadrar H2: el problema es el umbral de corte, no el modelo
El AUC-ROC ronda 0.73 (capacidad discriminativa moderada-buena) pero el F₁ cae a ~0.52-0.56. Esa brecha, combinada con la matriz de confusión (especificidad 94.7 %, sensibilidad 28 %), es la firma típica de un **umbral mal calibrado**, no de un modelo incapaz. Recomendación concreta: añadir un análisis secundario que reporte el **F₁ con umbral óptimo** (índice de Youden sobre la curva ROC, o calibración del punto de corte sobre un set de validación). Si con el umbral calibrado el F₁ sube de forma material, el mensaje cambia de "el sistema no sirve" a "el sistema discrimina bien pero requiere calibrar el corte a la escala del LLM", que es una conclusión mucho más fuerte y defendible. El documento ya intuye esto en §6.1.2; conviene **cuantificarlo**, no solo enunciarlo.

### 2. Los umbrales 0.85 / 0.90 provienen de tareas distintas
Los benchmarks de la literatura (F₁ 0.910 de BERT dual-tower, 87,73 % de Gan et al.) corresponden a clasificación de oraciones o matching sobre decenas de miles de pares, no a clasificación binaria APTO/NO_APTO contra un Gold Standard de panel experto con κ = 0.76. Sugerencia: en §5.3.2 presentar 0.85/0.90 como **objetivos de referencia tomados de la literatura** y advertir explícitamente que no son directamente comparables con esta tarea ni con este Gold Standard. Esto blinda la tesis frente a la crítica de "umbral arbitrario" en la defensa.

### 3. H3 descansa sobre n = 17 mujeres: máxima fragilidad
Es la mayor debilidad de validez del trabajo. Con 17 candidatas, el DIR es casi anecdótico (el propio texto reconoce que el cambio de **una** decisión lo reduce a la mitad). Dos caminos, idealmente ambos:
- **Estadístico:** acompañar todo DIR/SPD con **intervalos de confianza por bootstrap** o un **test exacto de Fisher** sobre las tasas de selección por grupo. Reportar DIR sin IC en este tamaño muestral es riesgoso.
- **Retórico:** degradar las afirmaciones de H3 de "se demuestra que…" a "evidencia exploratoria/ilustrativa", y mover el hallazgo principal hacia el plano cualitativo (la anonimización superficial no basta), que sí es sostenible.

### 4. El "147.8×" es la cifra más citable y la más frágil
Los tiempos de C0 son **imputados**, no medidos (distribución uniforme calibrada con estimaciones del panel). Por tanto, los factores de aceleración son aproximaciones conceptuales. Recomendación: (a) atenuar el framing del speedup en el resumen y en las conclusiones ("del orden de dos órdenes de magnitud" en lugar de "147.8×" como dato duro), y (b) si es viable antes de la entrega, **cronometrar 3-5 cribados manuales reales** para anclar empíricamente la imputación. Una mini-medición real vale más que un número grande sin respaldo observacional.

### 5. Conectar OE2 (recall@10 ≥ 0.80) con la discusión de H2
El resultado contraintuitivo (C2 peor que C1 en F₁) se atribuye al truncamiento a 5 chunks. Esa explicación se refuerza muchísimo si se reporta el **recall de recuperación** (OE2): si la recuperación es buena pero el F₁ baja, queda demostrado que el problema es la **pérdida de información por el cap de top-5**, no la calidad del retriever. Hoy OE2 se enuncia como objetivo pero no se cruza con los resultados. Cerrar ese lazo.

---

## B. Rigor metodológico (impacto medio)

### 6. κ de Cohen con tres evaluadores: precisar el cálculo
Cohen's κ se define para **dos** anotadores. Con un panel de tres, hay que aclarar si κ = 0.76 es un **promedio de κ por pares** o si en realidad se usó **Fleiss' κ** (la métrica correcta para 3+ raters). El archivo `consistencia_global.md` cambió deliberadamente "Fleiss" por "Cohen"; conviene que el texto explique en una frase cómo se computó la concordancia entre los tres evaluadores para evitar una observación del tribunal.

### 7. Intervalos de confianza también para equidad
Se calcula IC por bootstrap para el AUC pero no para DIR/SPD. Dado el n pequeño de subgrupos, los IC de equidad son más necesarios que los de AUC. Homogeneizar el tratamiento estadístico.

### 8. Persistir artefactos faltantes (reproducibilidad)
Los DIR por rango de edad y los recuentos por subgrupo aparecen en el texto pero no en ningún CSV de los revisados. Generar `tab_resultados_h3_edad.csv` y un CSV de recuentos por género/edad. Coherente con INV-W2 e INV-11 del propio proyecto.

### 9. Elevar la divergencia de signo Claude vs Gemini a contribución
Que Claude sesgue contra mujeres (DIR 0.602) y Gemini a favor (DIR 1.397) en C2 no es ruido: es un hallazgo sobre **sesgo específico del modelo**, no inherente a la tarea. Hoy se menciona al pasar en §5.10/§6.1.3. Vale la pena destacarlo como una de las contribuciones empíricas (refuerza la #4 de §6.2.3).

---

## C. Coherencia y presentación (impacto medio-bajo, rápido de aplicar)

### 10. Unificar el nombre del modelo
Coexisten "Claude Sonnet 4.5" (§4.4) y "Claude 4.5 Sonnet" (§5.10 y tabla comparativa). Elegir una sola forma en todo el documento.

### 11. Unificar el título del trabajo
La portada dice "Selección de Talento Automatizada y Equitativa: Un Enfoque basado en LLMs y Recuperación Aumentada", mientras que el archivo y el repositorio hablan de "Optimización del Proceso de Selección de Talento". Asegurar un título único en portada, resumen, repositorio y cualquier referencia cruzada.

### 12. Convertir el Anexo A en un mapa módulo→archivo
Al sacar los nombres de archivo del cuerpo (Eje F), la trazabilidad código-texto no debe perderse. El Anexo A hoy es solo el enlace al repositorio; agregar una **tabla breve** que mapee cada módulo funcional (extracción, embeddings, retrieval, scoring, anonimización, métricas) a su ruta en el repo. Así el cuerpo queda limpio y la reproducibilidad se conserva donde corresponde.

### 13. Recomendación a Matriz más accionable
La conclusión ("no usar de forma autónoma") es correcta. Reforzarla con un **guardarraíl de despliegue** concreto: human-in-the-loop obligatorio en la decisión, calibración empírica del umbral antes de producción, y auditoría periódica de sesgo (en línea con el espíritu de la Local Law 144 que ya se cita). Convierte una conclusión defensiva en una recomendación profesional.

### 14. Asegurar 300 dpi en las figuras de resultados
INV-W3 del proyecto exige 300 dpi mínimo para figuras generadas por script. Verificar `fig6_2/6_3/6_4` antes de insertarlas en el .docx final.

---

## Síntesis
Las mejoras **1, 3 y 4** son las que más cambian la solidez de la defensa: recalibrar la lectura de H2, blindar H3 frente a su n minúsculo y atenuar/anclar el speedup. Son, además, coherentes con lo que el propio documento ya admite en su discusión; se trata sobre todo de **cuantificar y enmarcar** lo que hoy está enunciado de forma cualitativa.
