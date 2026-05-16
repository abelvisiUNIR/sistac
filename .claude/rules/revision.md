# Protocolo de Revisión — Comentarios de la Tutora

**Cuando llegan los comentarios de la Dra. Arguedas Lafuente, `/revise` clasifica cada uno y lo rutea al agente correcto.**

## Clasificación de comentarios

| Clasificación | Qué significa | Ruteado a |
|--------------|---------------|-----------|
| **NUEVO ANÁLISIS** | Requiere nuevo experimento, script o métrica | Coder → coder-critic |
| **ACLARACIÓN** | Revisión de texto suficiente | Writer → writer-critic |
| **REESCRITURA** | Revisión estructural de sección completa | Writer → writer-critic |
| **DESACUERDO** | Requiere respuesta diplomática | Flaggeado para revisión del Usuario |
| **MENOR** | Tipografía, formato, coherencia menor | Writer |

## El flujo de revisión

```
Comentarios de tutora llegan (documento Word, correo, etc.)
        │
        ▼
   /revise clasifica cada comentario
        │
        ├── NUEVO ANÁLISIS → Coder → coder-critic → Writer actualiza la sección
        ├── ACLARACIÓN    → Writer → writer-critic
        ├── REESCRITURA   → Writer → writer-critic
        ├── DESACUERDO    → Usuario decide → respuesta diplomática redactada
        └── MENOR         → Writer
        │
        ▼
   Sección revisada → writer-critic → Orchestrator re-verifica
        │
        ▼
   Respuesta a tutora producida en texto (insertar en .docx o enviar por correo)
```

## Reglas

- Se usan los mismos agentes pero de forma dirigida — no es un reinicio completo del pipeline
- Cada comentario tiene su propio ruteo — un solo reporte de tutora puede activar múltiples pares de agentes
- La respuesta mapea cada comentario al cambio específico realizado en el `.docx`
- Los items DESACUERDO siempre se flaggean para revisión del usuario — Claude nunca responde autónomamente a la tutora
- El Orchestrator registra qué comentarios están resueltos y cuáles pendientes en `quality_reports/revision_tracker_[fecha].md`
