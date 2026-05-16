# Agents: Pairs, Separation of Powers, and Escalation

---

## 1. Adversarial Pairing

**Every worker agent has a paired critic. The Orchestrator never dispatches a creator without scheduling its critic.**

### Worker-Critic Pairs

| Worker (Creator) | Critic (Reviewer) | What's Reviewed |
|-----------------|-------------------|-----------------|
| librarian | librarian-critic | Literature coverage, gaps, recency |
| explorer | explorer-critic | Corpus feasibility, demographic balance, reproducibility |
| coder | coder-critic | Code quality, reproducibility, test coverage |
| writer | writer-critic | Manuscript polish (Word/español), APA 7 compliance, hedging |

### Revisión de tutora (Special Case)

La revisión de la Dra. Arguedas Lafuente usa una estructura diferente — el Orchestrator
despacha al writer-critic en modo "tutora":

1. Orchestrator asigna el capítulo al writer-critic con los comentarios de la tutora
2. Writer-critic clasifica cada comentario (NUEVO ANÁLISIS / ACLARACIÓN / DESACUERDO / MENOR)
3. Orchestrator rutea según clasificación — ver `rules/revision.md`

### Enforcement

- The Orchestrator checks: if a creator artifact exists without a critic score, it is **not approved**
- No artifact advances to the next phase without its critic's score >= 80
- Critics produce scores; creators produce artifacts — never the reverse

---

## 2. Separation of Powers

**Critics never create. Creators never self-score.**

### Critics Never Create

A critic's job is to evaluate, not to produce artifacts. If a critic produces code, text, or data during its review, something is wrong.

**What critics DO:**
- Score artifacts against a rubric
- List issues with severity and deductions
- Suggest fixes (as recommendations, not implementations)

**What critics DON'T DO:**
- Write code to fix the issues they found
- Rewrite paper sections
- Produce alternative implementations

**Why:** A critic who fixes their own findings has incentive to find only fixable issues. Separation keeps criticism honest.

### Creators Can't Self-Score

A creator cannot evaluate the quality of its own work. The score always comes from the paired critic.

| Agent | Creates | Scored By |
|-------|---------|-----------|
| librarian | Annotated bibliography | librarian-critic |
| explorer | Corpus assessment and generation plan | explorer-critic |
| coder | Python scripts | coder-critic |
| writer | TFE manuscript (Word/español) | writer-critic |

### Enforcement

The Orchestrator flags violations:
- If a critic invocation produces a file in `scripts/`, `paper/`, or `paper/talks/` → flag
- If a creator reports its own score → discard, dispatch critic

---

## 3. Three Strikes Escalation

**If a worker-critic pair fails to converge after 3 rounds, the Orchestrator escalates.**

### The Protocol

```
Round 1: Critic reviews → Worker fixes
Round 2: Critic reviews → Worker fixes
Round 3: Critic reviews → Worker fixes
         Still failing?
              ↓
         ESCALATION
```

### Escalation Routing

| Pair | Escalation Target | What Happens |
|------|-------------------|--------------|
| coder + coder-critic | User | Decisión de diseño técnico — necesita criterio humano |
| writer + writer-critic | Orchestrator | Reescritura estructural, no solo pulido |
| librarian + librarian-critic | User | Desacuerdo de alcance — usuario decide profundidad vs. amplitud |
| explorer + explorer-critic | User | Deadlock de viabilidad — usuario decide trade-offs de recursos |

### Rules

- **Max 3 rounds per pair per invocation** — no infinite loops
- **Escalation is logged** in the research journal with strike count
- **User escalation requires a clear question** — not "they disagree," but "coder-critic requires X, which contradicts Y. Which takes priority?"
- **Post-escalation:** The worker starts fresh from the escalation target's decision, not from its previous attempt
