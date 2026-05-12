---
name: write
description: Draft academic paper sections using paragraph-level argument moves. Cleanup pass strips AI patterns after drafting. Replaces /draft-paper and /humanizer.
argument-hint: "[section or mode: intro | strategy | results | conclusion | abstract | full | humanize] [file path (optional)]"
allowed-tools: Read,Grep,Glob,Write,Edit,Task
---

# Write

Draft paper sections or apply cleanup pass by dispatching the **Writer** agent.

**Input:** `$ARGUMENTS` — section name or mode, optionally followed by file path.

---

## Modes

### `/write [section]` — Draft Paper Section
Draft a specific section: `intro`, `strategy`, `results`, `conclusion`, `abstract`, or `full`.

**Agent:** Writer
**Output:** LaTeX section file in paper/sections/

Workflow:

#### 1. Context Gathering

Before drafting, read all available context:
1. Read existing paper draft in `paper/` (if it exists)
2. Read `master_supporting_docs/` for notes, outlines, research specs
3. Read most recent `quality_reports/research_spec_*.md` or `quality_reports/lit_review_*.md`
4. Read `.claude/references/domain-profile.md` for field conventions
5. Check `Bibliography_base.bib` for available citations
6. Scan `paper/tables/` and `paper/figures/` for generated output
7. Read `quality_reports/results_summary.md` if it exists (from Coder)

#### 2. Paper Type Detection

Before routing, identify the paper type from the strategy memo or existing draft:
- **Reduced-form** — DiD, IV, RDD, event study
- **Structural** — Model estimation, counterfactual simulations
- **Theory + empirics** — Propositions tested with data
- **Descriptive / measurement** — New data, new measure, stylized facts

This determines which section templates the Writer uses.

#### 3. Section Routing

Based on `$ARGUMENTS`:
- **`full`**: Draft all sections in sequence, pausing between major sections for user feedback
- **`intro`**: Draft introduction (most common request)
- **`strategy`**: Draft empirical strategy (reduced-form), model + estimation (structural), or model + tests (theory+empirics)
- **`results`**: Draft results — narration style depends on paper type and output type (regression tables, event study figures, counterfactual simulations, etc.)
- **`conclusion`**: Draft conclusion with type-appropriate ending (policy implications, counterfactual implications, or research agenda)
- **`abstract`**: Draft abstract (must have other sections first)
- **`data`**: Draft data section — expanded for descriptive/measurement papers
- **`model`**: Draft model section (structural or theory+empirics papers only)
- **No argument**: Ask user which section to draft

#### 4. Dispatch Writer

Dispatch Writer with paper type and argument-move templates for the target section. The writer drafts using paragraph types (motivation, result statement, mechanism, etc.), applies design-specific moves, then runs the cleanup pass. Save to `paper/sections/[section].tex`.

#### 5. Quality Self-Check

Before presenting the draft:
- [ ] Paper type identified and correct template used
- [ ] Every paragraph has an identifiable purpose (argument move type)
- [ ] Findings lead sentences — not buried after setup
- [ ] Design-specific elements present (see writer.md for checklists per design)
- [ ] Every displayed equation is numbered (`\label{eq:...}`)
- [ ] All `\cite{}` keys exist in `Bibliography_base.bib`
- [ ] Introduction contribution paragraph names specific papers
- [ ] Effect sizes stated with units
- [ ] No banned hedging phrases
- [ ] Notation consistent throughout
- [ ] All tables/figures referenced actually exist in `paper/tables/` or `paper/figures/`
- [ ] Results narrated correctly for output type (tables, event study figures, counterfactuals)

#### 6. Present to User

Present each section for feedback. Flag items that need attention:
- **TBD items:** Where empirical results are needed but not yet available
- **VERIFY items:** Citations that need user confirmation
- **PLACEHOLDER items:** Effect sizes awaiting final estimates

### `/write humanize [file]` — Cleanup Pass Only
Strip AI writing patterns from existing text without rewriting content.

**Agent:** Writer (cleanup mode)
**Output:** Edited file with AI patterns removed

Strips 24 patterns across 4 categories:
- Structural: forced narrative arcs, artificial progression
- Lexical: "delve, leverage, nuanced, robust"
- Rhetorical: rule-of-three, negative parallelisms, em dash overuse
- Formatting: excessive bullet points, promotional language

---

## Section Standards

**All paper types share the same backbone. Moves diverge by type — see writer.md for full templates.**

| Section | Length | Reduced-Form | Structural | Theory+Empirics | Descriptive |
|---------|--------|-------------|-----------|----------------|-------------|
| Introduction | 1000-1500 | ...preview → result → contribution | ...model preview → counterfactual → contribution | ...theory preview → test result → contribution | ...data innovation → key fact → contribution |
| Data | 800-1200 | Treatment, outcome, controls | Moments that identify parameters | Standard | 1200-1800 (core contribution) |
| Strategy/Model | 800-1500 | Design-specific (DiD/IV/RDD/ES) | Environment → decisions → equilibrium → estimation | Model → propositions → tests | N/A (merged into Data) |
| Results | 800-1500 | Main spec → robustness → heterogeneity | Estimates → model fit → counterfactuals → welfare | Prediction-by-prediction evidence | Key facts → decompositions → implications |
| Conclusion | 500-700 | Policy implications | Counterfactual implications + model limitations | What model gets right/wrong | Research agenda enabled by new data |
| Abstract | 100-150 | Question, design, finding with magnitude | Question, model, counterfactual finding | Question, prediction, test result | Question, measurement, key fact |

---

## LaTeX Conventions

- `\citet{}` for textual citations ("Smith (2024) shows...")
- `\citep{}` for parenthetical citations ("...is well documented (Smith, 2024)")
- `booktabs` rules (`\toprule`, `\midrule`, `\bottomrule`) — never `\hline`
- Notation protocol: `Y_{it}`, `D_{it}`, `\gamma_i`, `\delta_t`, `\varepsilon_{it}`

---

## Principles
- **This is the user's paper, not Claude's.** Match their voice and style.
- **Never fabricate results.** Use TBD placeholders.
- **Citations must be verifiable.** Only cite confirmed papers.
- **Argument moves first, cleanup second.** Draft with structure, then strip AI patterns.
