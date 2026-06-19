# Voz académica — Mario Agustín Belvisi Lescano

Estas reglas aplican a TODO el texto que se produce para el TFE SISTAC. No hay
excepciones. Rigen especialmente la redacción de los Capítulos 5 a 9
(implementación, validación, resultados, discusión y conclusiones).

---

## Tono a partir del Capítulo 5

A partir del Capítulo 5, el tono cambia respecto al marco teórico: se va directo
al trabajo realizado. No se contextualiza desde la literatura. No se justifican
las decisiones con citas de terceros; se justifican con la lógica del diseño
experimental o con los resultados observados.

El patrón de escritura en los capítulos de implementación y resultados es:

```
qué se hizo → cómo se hizo → por qué se tomó esa decisión → qué resultado produjo
```

---

## Construcción de oraciones

- 20–35 palabras por oración (más cortas que en el marco teórico, más directas).
- Gerundios como conectores internos: "generando", "permitiendo", "incorporando",
  "evitando".
- "lo que" para encadenar consecuencias: "...lo que permitió X".
- "esto a su vez" para efectos secundarios.
- Sin puntos seguidos muy cortos: las ideas fluyen en cadenas lógicas.

---

## Conectores preferidos

"En este sentido" / "Por lo tanto" / "Sin embargo" / "Adicionalmente" /
"Como consecuencia" / "A partir de esto".

Usarlos solo para transiciones reales entre ideas, nunca como decoración.

---

## Persona gramatical

NUNCA primera persona singular. Siempre voz impersonal o pasiva:

- "se implementó", "se diseñó", "se seleccionó", "se observó".
- "el presente trabajo", "el sistema", "SISTAC".
- "los autores" solo si es imprescindible referirse a quienes tomaron la decisión.

---

## Sin citas en los Capítulos 5 a 9

Los capítulos de implementación, resultados, discusión y conclusiones no llevan
citas académicas de terceros. Todo es trabajo propio. Si algo técnico necesita
referencia (por ejemplo, la fórmula de DIR o SPD), se menciona la fuente
brevemente en el texto, sin aparato citacional formal.

---

## Limpieza obligatoria — eliminar siempre

| Construcción problemática | Acción |
|---------------------------|--------|
| "Cabe destacar que" | Reformular como afirmación directa |
| "Es importante señalar" | Eliminar; la oración se sostiene sola |
| "Resulta evidente" | Eliminar |
| "interesante / innovador / robusto" sin dato que lo respalde | Eliminar el adjetivo |
| Guiones largos (—) | Reemplazar por coma o punto |
| Bullets en el texto corrido | Convertir a prosa |
| Primera persona singular | Reescribir en impersonal |

---

## Notación (consistente en todo el documento — INV-7)

| Símbolo | Significado |
|---------|-------------|
| F1 | F1-score macro |
| AUC-ROC | Area Under the ROC Curve |
| DIR | Disparate Impact Ratio |
| SPD | Statistical Parity Difference |
| T_cand | Tiempo de procesamiento por candidato |
| κ | Cohen's Kappa |
| C0, C1, C2, C3 | Configuraciones experimentales |
