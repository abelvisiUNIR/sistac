# Perfil de voz — Mario Agustín Belvisi Lescano

Toda redacción del TFE SISTAC aplica este perfil sin excepción.

---

## Estructura de párrafo: patrón embudo obligatorio

```
Contexto amplio → Problema concreto → Enfoque / Solución
```

Nunca arrancar un párrafo con la solución. Siempre desde el fenómeno general.
El lector debe sentir que llega a la solución por necesidad lógica, no por
decreto del autor.

**Incorrecto:**
> El módulo PII de SISTAC utiliza Presidio para eliminar entidades nombradas...

**Correcto:**
> Los sistemas de cribado curricular automatizados que procesan texto sin filtrado
> previo reproducen los sesgos demográficos presentes en los datos de entrada, lo
> que reduce la equidad del proceso de selección. En este contexto, el tratamiento
> de la información personal identificable (PII, Personally Identifiable Information)
> se convierte en un paso crítico de preprocesamiento. En el presente trabajo, el
> módulo PII de SISTAC implementa Microsoft Presidio con entidades personalizadas
> para el contexto rioplatense, suprimiendo los vectores demográficos antes de que
> el texto ingrese al pipeline RAG.

---

## Construcción de oraciones

- **Longitud:** 25–40 palabras por oración. Las ideas fluyen en cadenas lógicas,
  no en puntos cortos.
- **Subordinadas preferidas:** causales (`dado que`, `puesto que`, `ya que`) y
  consecutivas (`lo que genera`, `lo que permite`, `lo que implica`).
- **Gerundios como conectores internos:** `incorporando`, `aplicando`, `generando`,
  `permitiendo`.
- **Cadenas de consecuencia:**
  - `...lo que genera X` para consecuencias directas.
  - `esto a su vez` para efectos de segundo orden.
- **Sin punto seguido corto** cuando las ideas están relacionadas — usá punto y
  coma o subordinada.

---

## Conectores (en orden de preferencia)

Usarlos solo para marcar transiciones reales entre ideas, nunca como decoración:

1. `En este sentido`
2. `Por lo tanto`
3. `Sin embargo`
4. `Adicionalmente`
5. `Como consecuencia`
6. `A partir de esto`
7. `En concordancia con`
8. `En el presente trabajo` / `Para el caso de` / `En el contexto de Matriz`
   *(puente teoría→caso obligatorio después de cada bloque teórico)*

---

## Introducción de conceptos técnicos

**Patrón fijo:** nombre en español → sigla/nombre en inglés entre paréntesis →
definición breve con cita.

```
La recuperación aumentada por generación (RAG, Retrieval-Augmented Generation)
es definida por Lewis et al. (2020) como un paradigma que combina un módulo
de recuperación sobre una base de conocimiento externa con un modelo generativo,
permitiendo que el sistema acceda a información actualizada sin necesidad de
reentrenamiento.
```

**Regla:** NUNCA introducir una sigla sin expandirla primero. Una vez expandida
en el capítulo, puede usarse la sigla sola.

---

## Vínculo teoría-práctica (obligatorio)

Después de cada bloque teórico: puente explícito al caso SISTAC.

**Frases de puente:** `En el presente trabajo`, `Para el caso de SISTAC`,
`En el contexto de Matriz`, `Este diseño permite`.

**Ritmo invariable:**
```
Teoría → Evidencia bibliográfica → Aplicación al caso SISTAC
```

---

## Persona gramatical

NUNCA primera persona singular. Siempre voz impersonal o pasiva:

| Evitar | Usar |
|--------|------|
| `yo propongo` | `se propone` |
| `considero que` | `el presente trabajo sostiene que` |
| `elegimos ChromaDB` | `se selecciona ChromaDB` |
| `en nuestra implementación` | `en la implementación de SISTAC` |

---

## Patrón de citas APA 7

- **Afirmación estándar:** `Afirmación (Autor, año).`
- **Definición formal:** `es definido por Autor (año) como [definición].`
- **Múltiples fuentes:** `(Autor1, año1; Autor2, año2).`
- **Cita directa:** `"[texto]" (Autor, año, p. X).`
- **Regla:** NUNCA una cita sola sin una oración que la ancle semánticamente.

**Notación** (seguir domain-profile.md sin excepción):

| Símbolo | Significado |
|---------|-------------|
| F1 | F1-score macro |
| AUC-ROC | Area Under the ROC Curve |
| DIR | Disparate Impact Ratio |
| SPD | Statistical Parity Difference |
| T_cand | Tiempo de procesamiento por candidato |
| κ | Cohen's Kappa |
| C0, C1, C2, C3 | Configuraciones experimentales |

---

## Tipos de párrafo

### 1. Motivación

```
Fenómeno general observable
  → Evidencia cuantitativa de la magnitud del problema (cita)
    → Brecha de conocimiento o limitación actual
      → Lo que aborda SISTAC / el capítulo
```

**Disparadores:** inicio de capítulo, inicio de sección de revisión de literatura,
párrafo de justificación de decisión de diseño.

---

### 2. Descripción técnica

```
Componente / módulo nombrado
  → Qué hace (función en el sistema)
    → Cómo lo hace (mecanismo técnico)
      → Por qué se eligió esta implementación (justificación con cita o dato)
```

**Disparadores:** Cap. 4 (arquitectura), Cap. 5 (implementación), secciones de
stack tecnológico.

---

### 3. Resultado experimental

```
Métrica + valor obtenido (con IC 95% si aplica)
  → Comparación con umbral de referencia (H1: >50%; H2: F1≥0.85, AUC-ROC≥0.90;
    H3: DIR≥0.80)
      → Comparación entre configuraciones (C1 vs C2 vs C3)
        → Interpretación en términos del problema de Matriz
```

**Disparadores:** Cap. 7 (Resultados), párrafos de tablas de resultados.

**Regla:** NUNCA escribir "significativo" sin reportar el valor numérico y el p-value.

---

### 4. Posicionamiento bibliográfico

```
Qué encontró [Autor, Año] (resultado principal, con dato numérico)
  → En qué se diferencia del contexto / enfoque de SISTAC
    → Contribución incremental de SISTAC sobre ese trabajo
```

**Disparadores:** Cap. 2 (Estado del arte), Cap. 8 (Discusión).

---

### 5. Limitación

```
Contexto / condición donde el resultado no aplica directamente
  → Razón técnica o empírica de la limitación
    → Mitigación adoptada en SISTAC / recomendación para trabajo futuro
```

**Disparadores:** Cap. 8.3 (Limitaciones del estudio), párrafos de caveats en
metodología.

---

## Cleanup pass obligatorio

Antes de entregar cualquier output, eliminar estas construcciones:

| Construcción problemática | Reemplazo |
|--------------------------|-----------|
| `Cabe destacar que` | Reformular como afirmación directa |
| `Es importante señalar` | Eliminar; la oración se sostiene sola |
| `En este marco` sin marco previo | Eliminar |
| `A nivel de` | `en el ámbito de` / `respecto a` |
| `Dicho esto` | Eliminar |
| `robusto` / `innovador` / `novedoso` sin dato | Eliminar el adjetivo |
| Primera persona singular | Reescribir en impersonal |
| Sigla sin expandir en primera mención | Expandir |
