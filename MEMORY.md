# Project Memory

Corrections and learned facts that persist across sessions.
When a mistake is corrected, append a `[LEARN:category]` entry below.

---

<!-- Append new entries below. Most recent at bottom. -->

## Workflow Patterns

[LEARN:workflow] Requirements specification phase catches ambiguity before planning → reduces rework 30-50%. Use spec-then-plan for complex/ambiguous tasks (>1 hour or >3 files).

[LEARN:workflow] Spec-then-plan protocol: AskUserQuestion (3-5 questions) → create `quality_reports/specs/YYYY-MM-DD_description.md` with MUST/SHOULD/MAY requirements → declare clarity status (CLEAR/ASSUMED/BLOCKED) → get approval → then draft plan.

[LEARN:workflow] Context survival before compression: (1) Update MEMORY.md with [LEARN] entries, (2) Ensure session log current (last 10 min), (3) Active plan saved to disk, (4) Open questions documented. The pre-compact hook displays checklist.

[LEARN:workflow] Plans, specs, and session logs must live on disk (not just in conversation) to survive compression and session boundaries. Quality reports only at merge time.

## Documentation Standards

[LEARN:documentation] When adding new features, update BOTH README and guide immediately to prevent documentation drift. Stale docs break user trust.

[LEARN:documentation] Always document new templates in README's "What's Included" section with purpose description. Template inventory must be complete and accurate.

[LEARN:documentation] Guide must be generic (framework-oriented) not prescriptive. Provide templates with examples for multiple workflows (LaTeX, R, Python, Jupyter), let users customize. No "thou shalt" rules.

[LEARN:documentation] Date fields in frontmatter and README must reflect latest significant changes. Users check dates to assess currency.

## Design Philosophy

[LEARN:design] Framework-oriented > Prescriptive rules. Constitutional governance works as a TEMPLATE with examples users customize to their domain. Same for requirements specs.

[LEARN:design] Quality standard for guide additions: useful + pedagogically strong + drives usage + leaves great impression + improves upon starting fresh + no redundancy + not slow. All 7 criteria must hold.

[LEARN:design] Generic means working for any academic workflow: pure LaTeX (no Quarto), pure R (no LaTeX), Python/Jupyter, any domain (not just econometrics). Test recommendations across use cases.

## File Organization

[LEARN:files] Specifications go in `quality_reports/specs/YYYY-MM-DD_description.md`, not scattered in root or other directories. Maintains structure.

[LEARN:files] Templates belong in `templates/` directory with descriptive names. Currently have: session-log.md, quality-report.md, exploration-readme.md, archive-readme.md, requirements-spec.md, constitutional-governance.md.

## Constitutional Governance

[LEARN:governance] Constitutional articles distinguish immutable principles (non-negotiable for quality/reproducibility) from flexible user preferences. Keep to 3-7 articles max.

[LEARN:governance] Example articles: Primary Artifact (which file is authoritative), Plan-First Threshold (when to plan), Quality Gate (minimum score), Verification Standard (what must pass), File Organization (where files live).

[LEARN:governance] Amendment process: Ask user if deviating from article is "amending Article X (permanent)" or "overriding for this task (one-time exception)". Preserves institutional memory.

## Skill Creation

[LEARN:skills] Effective skill descriptions use trigger phrases users actually say: "check citations", "format results", "validate protocol" → Claude knows when to load skill.

[LEARN:skills] Skills need 3 sections minimum: Instructions (step-by-step), Examples (concrete scenarios), Troubleshooting (common errors) → users can debug independently.

[LEARN:skills] Domain-specific examples beat generic ones: citation checker (psychology), protocol validator (biology), regression formatter (economics) → shows adaptability.

## Memory System

[LEARN:memory] Two-tier memory solves template vs working project tension: MEMORY.md (generic patterns, committed), personal-memory.md (machine-specific, gitignored) → cross-machine sync + local privacy.

[LEARN:memory] Post-merge hooks prompt reflection, don't auto-append → user maintains control while building habit.

## Meta-Governance

[LEARN:meta] Repository dual nature requires explicit governance: what's generic (commit) vs specific (gitignore) → prevents template pollution.

[LEARN:meta] Dogfooding principles must be enforced: plan-first, spec-then-plan, quality gates, session logs → we follow our own guide.

[LEARN:meta] Template development work (building infrastructure, docs) doesn't create session logs in quality_reports/ → those are for user work (slides, analysis), not meta-work. Keeps template clean for users who fork.

## SISTAC — Decisiones de proyecto

[LEARN:setup] Limpieza .claude/ completada para SISTAC (2026-04-15): eliminados 14 archivos heredados del template de economía/LaTeX (~127 KB, ~1.900 líneas). Archivos eliminados: journal-profiles.md (39.5KB), coding-standards-julia.md, coding-standards-r.md, working-paper-format.md, storyteller.md, storyteller-critic.md, editor.md, domain-referee.md, methods-referee.md, lint-scripts.sh, post-edit-lint.sh, post-merge.sh, skills/submit/SKILL.md, skills/talk/SKILL.md. writer.md reescrito para TFE Word en español con perfil de voz de Mario Agustín Belvisi Lescano (patrón embudo, conectores específicos, voz impersonal, citas APA 7). WORKFLOW_QUICK_REF.md actualizado para SISTAC. domain-profile.md, workflow.md, content-invariants.md, quality.md, agents.md, logging.md, meta-governance.md, revision.md y coding-standards-python.md conservados sin cambios.

[LEARN:stack] Stack activo SISTAC: Python + LangChain + ChromaDB/FAISS + spaCy + Presidio + sentence-transformers + scikit-learn (solo métricas clasificación) + python-docx. NO usar R, Julia, LaTeX. Documento principal: paper/SISTAC_TFE.docx (Word).

[LEARN:doc] Capítulos 1-4 migrados a paper/SISTAC_TFE.docx (2026-04-15). Fuente: Optimizacion_del_Proceso_de_Seleccion_de_Talento_.docx. Capítulos 5-9 tienen secciones stub con [TODO]. Documento generado con python-docx: 351 párrafos, 66.8 KB. Estructura del documento refleja diseño factorial C0-C3 y las tres hipótesis H1/H2/H3.

[LEARN:data] Dataset sintético aún no generado. Pipeline: PrivBayes (smartnoise-sdk) para distribuciones demográficas + LLM (GPT-4o mini en dev, LLaMA 3.1 8B local para experimento final). Target: ≥300 pares CV-JD, split 70/15/15, demografía balanceada (género + rango edad). Referencia metodológica: Bruera et al. (2022) + Saldivar et al. (2025).

[LEARN:setup] content-invariants.md actualizado (2026-04-15): INVs LaTeX/R (INV-1 a INV-6, INV-9, INV-10, INV-12, INV-13, INV-20, INV-21) reemplazados por INV-W1 a INV-W5 para stack Word/Python. INVs de código Python INV-14 a INV-19 conservados sin cambios. rules/agents.md: eliminada fila storyteller+storyteller-critic, par de Peer Review reemplazado por "Revisión de tutora" (writer-critic en modo revisión). rules/workflow.md: eliminadas referencias a /talk, Beamer, R scripts, "Presentation" phase y "Submission" phase de journals; actualizadas tablas de Agent Dispatch, Standalone Skills y Phase Dependencies para SISTAC.
