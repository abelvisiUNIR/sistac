---
name: write
description: Redactar secciones del TFE SISTAC en español académico. Output texto plano listo para insertar en paper/SISTAC_TFE.docx. Despacha Writer para redacción y writer-critic para revisión. Usar para redactar o revisar cualquier capítulo o sección del TFE.
argument-hint: "[sección] cap1 | cap2 | cap3 | cap4 | cap5-rag | cap5-pii | cap6 | cap7 | cap8 | cap9 | resumen | abstract"
allowed-tools: Read,Grep,Glob,Write,Edit,Task
---

# Write

Redactar secciones del TFE SISTAC en español académico. Output texto plano para insertar en `paper/SISTAC_TFE.docx`.

**Input:** `$ARGUMENTS` — sección objetivo o capítulo.

---

## Workflow estándar

1. **Leer contexto:**
   - `CLAUDE.md` — hipótesis, equipo, estado del proyecto
   - `.claude/references/domain-profile.md` — notación, métricas, referencias seminales
   - `paper/SISTAC_TFE.docx` (extracto relevante) — mantener consistencia con lo escrito
   - Resultados disponibles en `results/` — para secciones de resultados/discusión

2. **Despachar Writer** con instrucciones de sección

3. **Cleanup pass** — eliminar patrones de IA (frases genéricas, hedging excesivo, listas donde debería haber prosa)

4. **Despachar writer-critic** para revisión

5. **Iterar** si score < 80 (máx 3 rondas)

6. **Entregar** texto plano listo para Word

---

## Secciones disponibles

| Argumento | Capítulo | Responsable | Estado |
|-----------|----------|-------------|--------|
| `cap1` | Introducción | Ambos | ✅ Escrito |
| `cap2` | Estado del arte | Ambos | ✅ Escrito |
| `cap3` | Metodología | Ambos | ✅ Escrito |
| `cap4` | Diseño del sistema | Ambos | ✅ Escrito |
| `cap5-rag` | Pipeline RAG y scoring (H2) | David | 🔵 En redacción |
| `cap5-pii` | Módulo PII y equidad (H3) | Mario | 🔵 En redacción |
| `cap6` | Validación experimental (H1) | Ambos | 🔵 En redacción |
| `cap7` | Resultados | Ambos | ⬜ Post-experimento |
| `cap8` | Discusión | Ambos | ⬜ Post-experimento |
| `cap9` | Conclusiones | Ambos | ⬜ Post-experimento |
| `resumen` | Resumen ejecutivo (ES) | Ambos | ⬜ |
| `abstract` | Abstract (EN) | Ambos | ⬜ |

---

## Convenciones de escritura SISTAC

### Formato de output

- **Texto plano** — sin marcadores LaTeX, sin Markdown de cabeceras
- **Español académico** — plural institucional ("se observa", "los resultados indican")
- **Términos técnicos en inglés** permitidos cuando no tienen traducción estándar (RAG, pipeline, embeddings)
- Listo para copiar-pegar en Word sin reformateo adicional

### Notación obligatoria

| Concepto | Notación |
|----------|---------|
| Ratio de impacto dispar | DIR (Disparate Impact Ratio) |
| Diferencia de paridad estadística | SPD (Statistical Parity Difference) |
| Tiempo por candidato | $T_{\text{cand}}$ |
| Configuraciones | C0, C1, C2, C3 |
| Métricas de eficacia | $F_1$, AUC-ROC |

### Estructura de párrafo tipo

```
[Afirmación principal]
[Evidencia — citar tabla/figura]
[Interpretación en el contexto de H1/H2/H3]
[Conexión con la sección siguiente o limitación]
```

### Plantillas por tipo de sección

**Resultados (Cap. 7):**
- Comenzar con resumen de hallazgo principal
- Tabla de métricas por configuración
- Comparación C1 vs C2 vs C3
- Interpretación de cada hipótesis

**Discusión (Cap. 8):**
- Contrastar con literatura (citar papers del Bibliography_base.bib)
- Limitaciones del diseño experimental
- Implicaciones para RRHH y fairness algorítmica

**Conclusiones (Cap. 9):**
- Responder explícitamente H1, H2, H3
- Contribuciones al campo
- Líneas de trabajo futuro

---

## Reglas del Writer

- Output siempre en **texto plano** para Word
- Sin auto-puntuación del output
- Toda cita con entrada en `Bibliography_base.bib`
- Números en texto = números en tablas (INV-11)
- Lenguaje causal solo donde el diseño lo justifica (INV-8)
