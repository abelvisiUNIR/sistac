# Quality: Scoring, Thresholds, and Severity

---

## 1. Scoring Protocol

**How individual agent scores aggregate into the overall project score.**

### Weighted Aggregation

The overall project score that gates submission (>= 95) is a weighted aggregate:

| Component | Weight | Source Agent |
|-----------|--------|-------------|
| Literatura (revisión) | 10% | librarian-critic |
| Datos (corpus sintético) | 10% | explorer-critic |
| Diseño experimental | 25% | coder-critic (plan de análisis) |
| Código Python | 15% | coder-critic |
| Documento TFE (Word) | 25% | writer-critic |
| Pulido del manuscrito | 10% | writer-critic (segunda pasada) |
| Reproducibilidad | 5% | verifier pass/fail |

### Minimum Per Component

No component can be below 80 for submission. A perfect literature review can't compensate for broken identification.

### Score Sources

- Each critic produces a score from 0 to 100 based on its deduction table
- Scores start at 100 and deduct for issues found
- The verifier is pass/fail (mapped to 0 or 100)
- writer-critic evalúa el documento dos veces: durante escritura y en pasada de pulido final

### Gate Thresholds

| Gate | Overall Score | Per-Component Minimum | Action |
|------|--------------|----------------------|--------|
| Commit | >= 80 | None enforced | Allowed |
| PR | >= 90 | None enforced | Allowed |
| Submission | >= 95 | >= 80 per component | Allowed |
| Below 80 | < 80 | — | Blocked |

### When Components Are Missing

Not every project uses all components. If a component hasn't been scored:
- It's excluded from the weighted average
- Remaining weights are renormalized
- Example: no literature review → weights become 11%, 28%, 17%, 28%, 11%, 6%

---

## 2. Severity Gradient

**Critics calibrate severity based on the phase of the project.**

### Phase-Based Severity

| Phase | Critic Stance | Rationale |
|-------|--------------|-----------|
| Discovery | Encouraging (low severity) | Early ideas need space to develop |
| Strategy | Constructive (medium severity) | Experimental design must be sound, but alternatives should be suggested |
| Execution | Strict (high severity) | Code and paper are near-final — bugs are costly |
| Revisión tutora | Adversarial (maximum severity) | Simula la revisión real de Dra. Arguedas Lafuente — sin piedad |

### How It Works

The Orchestrator includes the severity level in the critic's prompt:

```
You are reviewing at SEVERITY: HIGH (Execution phase).
Flag all issues. Do not suggest "consider" — state what must change.
```

### Deduction Scaling

The same issue may have different deductions by phase:

| Issue | Discovery | Strategy | Execution | Revisión tutora |
|-------|-----------|----------|-----------|----------------|
| Cita faltante | -2 | -5 | -10 | -15 |
| Notación inconsistente | -1 | -3 | -5 | -5 |
| Lenguaje de cobertura excesivo | — | — | -3 | -5 |
| Falta de verificación de robustez | — | -5 | -15 | -20 |

### Principle

Early phases are about getting the direction right. Late phases are about getting the details right. Critics should match their tone and rigor to the phase.
