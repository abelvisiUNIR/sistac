---
name: analyze
description: Análisis end-to-end de SISTAC — implementa y ejecuta el pipeline Python para una configuración C0-C3 o para una hipótesis específica. Despacha Coder para implementación y coder-critic para revisión. Usar cuando se necesite correr experimentos, calcular métricas H1/H2/H3 o debuggear scripts.
argument-hint: "[objetivo] Opciones: --c0, --c1, --c2, --c3, --h1, --h2, --h3, --metrics, --debug [script.py]"
allowed-tools: Read,Grep,Glob,Write,Edit,Bash,Task
---

# Analyze

Pipeline de análisis end-to-end para SISTAC. Implementa, ejecuta y revisa los experimentos C0-C3.

**Input:** `$ARGUMENTS` — configuración objetivo, hipótesis o path a script.

---

## Modos

### `/analyze --c[0-3]` — Correr configuración experimental

Ejecutar el orquestador para una configuración específica.

**Workflow:**
1. Verificar que `scripts/python/experiments/orquestador_c0_c3.py` existe
2. Verificar que el corpus en `data/raw/` está disponible
3. Correr la configuración:
   ```bash
   cd scripts/python
   python experiments/orquestador_c0_c3.py --config C2
   ```
4. Verificar que los resultados se guardaron en `results/`
5. Despachar coder-critic para revisar outputs

---

### `/analyze --h[1-3]` — Calcular métricas de una hipótesis

**H1 (Eficiencia):**
```bash
cd scripts/python
python evaluation/compute_h1_efficiency.py
```
Calcula `T_cand` para cada configuración, compara contra C0.

**H2 (Eficacia):**
```bash
cd scripts/python
python evaluation/compute_h2_efficacy.py
```
Calcula F1 macro y AUC-ROC para C1, C2, C3 contra Gold Standard.

**H3 (Equidad):**
```bash
cd scripts/python
python evaluation/compute_h3_fairness.py
```
Calcula DIR y SPD para cada configuración, comparando C3 vs C1/C2.

---

### `/analyze --metrics` — Calcular todas las métricas

Ejecutar los tres módulos de evaluación en secuencia y consolidar resultados:
1. H1 → `results/metrics/h1_efficiency.csv`
2. H2 → `results/metrics/h2_efficacy.csv`
3. H3 → `results/metrics/h3_fairness.csv`
4. Consolidar → `results/metrics/summary.csv`
5. Exportar a `paper/tables/` para insertar en el .docx

---

### `/analyze --debug [script.py]` — Debuggear un script

1. Leer el script objetivo
2. Identificar el error o comportamiento inesperado
3. Despachar Coder para fix
4. Verificar que los tests pasan después del fix
5. Despachar coder-critic para revisión del fix

---

## Protocolo estándar de análisis

Para cualquier análisis nuevo:

```
1. Leer requerimientos (hipótesis objetivo, datos disponibles)
2. Verificar que config.py tiene PROJECT_ROOT y SEED
3. Despachar Coder para implementación
4. Correr script:
   cd scripts/python && python [modulo/script.py]
5. Verificar outputs (existen, tamaño > 0, formato correcto)
6. Despachar coder-critic para revisión
7. Si score >= 80: guardar outputs finales en paper/tables/ y results/
8. Si score < 80: iterar (máx 3 rondas)
```

---

## Checklist de verificación post-análisis

- [ ] Script corre sin errores (`exit code 0`)
- [ ] Todos los imports al inicio del archivo
- [ ] Sin rutas absolutas (usa `PROJECT_ROOT`)
- [ ] `random.seed(SEED)` + `np.random.seed(SEED)` al inicio
- [ ] Output guardado en `results/` o `paper/tables/`
- [ ] Tests pasan (`pytest -v`)
- [ ] Score coder-critic >= 80

---

## Convenciones de output

| Tipo | Destino | Formato |
|------|---------|---------|
| Métricas H1/H2/H3 | `results/metrics/` | `.csv` |
| Tablas para TFE | `paper/tables/` | `.csv` |
| Figuras para TFE | `paper/figures/` | `.png` (300 dpi) |
| Resultados piloto | `results/` | `.json` |
| Logs de experimento | `results/logs/` | `.txt` |
