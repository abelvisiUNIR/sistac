---
name: revise
description: Ciclo de revisión con la tutora — clasifica comentarios de la Dra. Arguedas Lafuente y los rutea al agente correcto. Reemplaza el flujo de R&R de journal.
argument-hint: "[archivo con comentarios de tutora] [sección del TFE (opcional)]"
allowed-tools: Read,Grep,Glob,Write,Edit,Task
---

# Revise

Procesar los comentarios de la tutora (Dra. Arguedas Lafuente), clasificarlos y rutearlos al agente correcto.

**Input:** `$ARGUMENTS` — path al archivo con comentarios de la tutora, opcionalmente seguido de la sección del TFE afectada.

---

## Workflow

### Paso 1: Leer inputs

1. Leer el archivo de comentarios de la tutora desde `$ARGUMENTS`
2. Leer la sección correspondiente del TFE (`paper/SISTAC_TFE.docx` o extracto en texto)
3. Leer el protocolo de revisión desde las reglas
4. Revisar scripts Python existentes para saber qué análisis ya están implementados

### Paso 2: Clasificar cada comentario

| Clase | Ruteo | Acción |
|-------|-------|--------|
| **NUEVO ANÁLISIS** | → Coder | Flag para el usuario, crear tarea de análisis |
| **ACLARACIÓN** | → Writer | Redactar sección reescrita |
| **REESCRITURA** | → Writer | Revisión estructural del texto |
| **DESACUERDO** | → Usuario (obligatorio) | Redactar respuesta diplomática, flaggear para revisión humana |
| **MENOR** | → Writer | Corrección directa (tipografía, formato, coherencia) |

### Paso 3: Construir documento de seguimiento

Guardar en `quality_reports/revision_tracker_[fecha].md` con:
- Conteo de comentarios por clase
- Lista de items por prioridad (ALTA: nuevo análisis, MEDIA: aclaración, FLAGGEADO: desacuerdos, BAJA: menores)
- Estado de cada item (pendiente / en progreso / resuelto)

### Paso 4: Despachar agentes

- ACLARACIÓN/REESCRITURA → despachar Writer con instrucciones específicas
- NUEVO ANÁLISIS → flaggear para aprobación del usuario antes de despachar Coder
- DESACUERDO → redactar respuesta diplomática, flaggear prominentemente para el usuario

### Paso 5: Redactar respuesta a la tutora

Generar documento de respuesta en texto (para insertar en el `.docx` o enviar por correo) con:
- Resumen de cambios principales
- Respuestas punto a punto con cita exacta del comentario
- Referencia a la sección/página donde se realizó el cambio

### Paso 6: Protocolo de desacuerdo diplomático

Cuando hay DESACUERDO: abrir con reconocimiento, aportar evidencia del marco teórico o diseño experimental, ofrecer concesión parcial si aplica. NUNCA decir "la tutora está equivocada." SIEMPRE flaggear para revisión del usuario antes de enviar.

### Paso 7: Guardar outputs

1. Tracker: `quality_reports/revision_tracker_[fecha].md`
2. Respuesta en texto: `quality_reports/respuesta_tutora_[fecha].md`
3. Secciones revisadas: indicar los cambios en `paper/SISTAC_TFE.docx`

---

## Principios

- **La respuesta es la voz del equipo.** Mantener el tono académico en español.
- **Nunca fabricar resultados.** Items de NUEVO ANÁLISIS quedan como TBD hasta que el Coder los implemente.
- **Flaggear todos los DESACUERDOS.** Requieren juicio humano antes de responder.
- **Registrar todo.** Cada comentario aparece en el tracker y en la respuesta.
- **El TFE es el documento de verdad.** Los cambios se hacen en `paper/SISTAC_TFE.docx`, no en borradores paralelos.
