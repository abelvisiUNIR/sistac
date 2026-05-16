---
name: tools
description: Utility commands — commit, validate-bib, lint, journal, context, learn. Herramientas de mantenimiento para SISTAC.
argument-hint: "[subcommand: commit | validate-bib | lint | journal | context | learn] [args]"
allowed-tools: Read,Grep,Glob,Write,Edit,Bash,Task
---

# Tools

Subcomandos utilitarios para mantenimiento e infraestructura del proyecto SISTAC.

**Input:** `$ARGUMENTS` — subcomando seguido de argumentos opcionales.

---

## Subcomandos

### `/tools commit [message]` — Git Commit

Stage de cambios, creación de commit y opcionalmente PR a `main`.

- Verificar git status para identificar cambios
- Stage de archivos relevantes (nunca `.env` ni credenciales)
- Crear commit con mensaje descriptivo
- Si hay score de calidad disponible y ≥ 80, incluirlo en el commit
- Branch activa: `desarrollo` (nunca commitear directo a `main`)

### `/tools validate-bib` — Validación de Bibliografía

Cruzar todas las citas del `.docx` y de los scripts Python contra `Bibliography_base.bib`.

Reporte:
- Entradas faltantes (citadas pero no en .bib)
- Entradas sin usar (en .bib pero no citadas)
- Claves duplicadas
- Claves con formato incorrecto (esperado: `AutorYear_keyword`)

### `/tools lint [file|dir]` — Linting mecánico de código Python

Ejecutar checks grep-based en scripts Python contra los estándares de codificación SISTAC. Detecta violaciones mecánicas antes de la revisión del coder-critic.

- **Archivo individual:** `/tools lint scripts/python/pii/anonymizer.py`
- **Directorio:** `/tools lint scripts/python/` (recursivo)
- **Default:** `/tools lint` (linta todo `scripts/python/`)

**Qué verifica:**

| Check | Severidad |
|-------|-----------|
| Rutas absolutas (`C:\\`, `/home/`, `/Users/`) | ALTA |
| `os.chdir()` | ALTA |
| `random.seed()` ausente en código estocástico | ALTA |
| `pip install` dentro de scripts | ALTA |
| Imports wildcard (`from X import *`) | MEDIA |
| `np.random.seed()` ausente en código numpy estocástico | MEDIA |
| `except:` desnudo sin tipo de excepción | MEDIA |
| Imports tardíos (no al inicio del archivo) | BAJA |

**Output:** Hallazgos por archivo con severidad, número de línea y sugerencia de corrección. Siempre advisory (exit 0).

**Cuándo usar:**
- Antes de `/review --code` — detecta violaciones mecánicas al instante
- Antes de commits — sanity check rápido

### `/tools journal` — Research Journal

Regenerar el timeline del journal de investigación desde quality_reports/ y git history.
Muestra registro cronológico de acciones de agentes, transiciones de fase, scores y decisiones.

### `/tools context` — Estado del contexto

Mostrar estado actual del contexto y salud de la sesión.
Verificar uso del contexto, si auto-compact se acerca, qué estado se preservará.

### `/tools learn` — Extraer aprendizajes

Extraer conocimiento reutilizable de la sesión actual. La auto-memoria maneja correcciones automáticamente; este subcomando es para flujos multi-paso que valen la pena documentar en `MEMORY.md`.

---

## Principios

- **Cada subcomando es liviano.** Sin orquestación multi-agente.
- **validate-bib detecta drift.** Ejecutar antes de commits para detectar citas rotas.
- **lint es advisory.** Nunca bloquea — el coder-critic hace el juicio de calidad.
