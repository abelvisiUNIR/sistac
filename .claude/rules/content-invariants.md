# Content Invariants — SISTAC

Estas reglas son no negociables. Cada agente las verifica. Las violaciones son
deducciones, no sugerencias. Los críticos citan el número de invariante en sus
reportes (ej: "viola INV-W2").

---

## Documento (Word)

**INV-W1.** El documento principal es `paper/SISTAC_TFE.docx` — fuente de verdad única.
Antes de cualquier edición estructural (reorganizar secciones, cambiar estilos de
párrafo en bloque), crear una copia de respaldo en `paper/backups/` con fecha en el
nombre.

**INV-W2.** Toda tabla generada por script Python debe existir como archivo en
`paper/tables/` (formato `.docx` o `.csv`) antes de insertarse en el documento
principal. No insertar tablas copiadas directamente desde la terminal o desde un
notebook sin guardar el artefacto primero.

**INV-W3.** Toda figura generada por script Python debe existir en `paper/figures/`
en formato `.png` (300 dpi mínimo) o `.svg` antes de insertarse en el documento.
No insertar capturas de pantalla de gráficos como sustituto de las figuras generadas
por script.

**INV-W4.** Las citas siguen APA 7 sin excepción: formato `(Autor, año)` en texto
corrido, `Autor (año)` cuando el autor es sujeto gramatical, lista de referencias
completa al final del documento ordenada alfabéticamente. Ninguna cita en el texto
sin entrada correspondiente en `Bibliography_base.bib`.

**INV-W5.** Ningún script en `scripts/python/` puede escribir directamente sobre
`paper/SISTAC_TFE.docx`. Los scripts solo generan artefactos en `paper/tables/` o
`paper/figures/`. La inserción en el `.docx` es siempre manual o a través del script
dedicado en `scripts/office/`.

**INV-7.** La notación es consistente en todas las secciones — el mismo símbolo
significa lo mismo en todo el documento. Símbolos diferentes para conceptos
diferentes. Seguir la tabla de notación en `.claude/references/domain-profile.md`.

**INV-8.** Toda afirmación causal tiene una sección de identificación correspondiente.
No usar lenguaje causal (`provoca`, `genera`, `determina`) en secciones descriptivas.
En SISTAC: los resultados de H1/H2/H3 se interpretan como evidencia de asociación
hasta que el diseño factorial lo justifique.

**INV-11.** Los números en el texto coinciden exactamente con las tablas y figuras.
Sin discrepancias de redondeo, sin valores desactualizados. Cuando cambia un resultado,
actualizar texto y tabla simultáneamente.

---

## Código (Python)

**INV-14.** `random.seed()` + `np.random.seed()` llamados exactamente una vez, al
comienzo del script principal, si existe cualquier elemento estocástico. Usar la
semilla documentada en `CLAUDE.md` o `MEMORY.md` para reproducibilidad.

**INV-15.** Todas las librerías importadas al comienzo del script, antes de cualquier
carga de datos o cómputo.

**INV-16.** Sin rutas absolutas. Todas las rutas relativas a la raíz del proyecto
mediante `pathlib.Path` y la función `PROJECT_ROOT` definida en
`scripts/python/config.py`.

**INV-17.** Sin listas crecientes en loops. Pre-alocar contenedores de resultados
o usar operaciones vectorizadas (pandas, numpy).

**INV-18.** Los archivos de output van a la ruta especificada por la configuración
de Output Organization en `CLAUDE.md`: tablas → `paper/tables/`, figuras →
`paper/figures/`, datos procesados → `data/cleaned/`.

**INV-19.** Sin funciones prohibidas: `os.chdir()`, `install.packages()` en scripts,
`sys.path.insert()` para importar módulos del proyecto (usar rutas relativas con
`pathlib`).

---

## Cómo usan este archivo los agentes

| Agente | Verifica | Acción ante violación |
|--------|----------|----------------------|
| **writer-critic** | INV-W1, INV-W4, INV-W5, INV-7, INV-8, INV-11 | Deducción según rúbrica |
| **coder-critic** | INV-W2, INV-W3, INV-W5, INV-14 a INV-19 | Deducción según rúbrica |
| **verifier** | INV-W1, INV-W5, INV-14, INV-15, INV-16, INV-19 | FAIL si presente |
| **lint hook** | INV-14, INV-15, INV-16, INV-19 | Advertencia informativa |
