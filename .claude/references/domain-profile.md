# Domain Profile — SISTAC

<!--
Perfil de dominio para el proyecto SISTAC.
Todos los agentes leen este archivo para calibrar su comportamiento específico del campo.
-->

## Field

**Primary:** Inteligencia Artificial Aplicada — NLP, Modelos de Lenguaje Grande (LLMs), Recuperación Aumentada por Generación (RAG)
**Adjacent subfields:** Algorithmic Fairness / Responsible AI, Privacy-Preserving ML (PII, anonimización), HR Technology (ATS, recruiting automation), Procesamiento de Lenguaje Natural

---

## Target Journals/Conferences (ranked by tier)

<!-- El Orchestrator usa esto para selección de venue. El Librarian prioriza estas búsquedas. -->

| Tier | Venue |
|------|-------|
| Top conferences | ACL, EMNLP, NeurIPS (fairness track), FAccT |
| Top journals | Expert Systems with Applications, AI & Society, Information Processing & Management |
| Strong field | AI & Ethics (Springer), IEEE Transactions on Neural Networks and Learning Systems |
| Specialty | Computers & Industrial Engineering, Journal of Information Science |

---

## Common Data Sources

<!-- El Explorer prioriza estas. El explorer-critic conoce sus particularidades. -->

| Dataset | Type | Access | Notes |
|---------|------|--------|-------|
| Dataset sintético SISTAC | synthetic CVs | Internal (generado con PrivBayes + LLM) | ~1,000-2,000 CVs con atributos demográficos controlados |
| ResuméAtlas | CV corpus | Public | 13,389 registros en 43 categorías; baseline para benchmarking |
| Kaggle Resume Dataset | CV corpus | Public | 962 CVs en 25 categorías; pequeño pero accesible |
| O*NET | occupations + skills | Public (Creative Commons) | ~1,000 ocupaciones con taxonomía de skills |
| ESCO | skills taxonomy | Public (EU) | 27 idiomas; versión es-LAC del IDB para contexto latinoamericano |
| Gold Standard RRHH | expert labels | Internal (Matriz Uruguay) | 3-5 expertos RRHH, inter-rater reliability con Cohen's κ |

---

## Experimental Design (Identification Strategy)

<!-- El Strategist considera estos primero. El strategist-critic conoce las amenazas específicas del campo. -->

| Strategy | Application | Key Assumption to Defend |
|----------|-------------|--------------------------|
| Diseño factorial 4 condiciones | C0 (manual), C1 (LLM), C2 (LLM+RAG), C3 (LLM+RAG+PII) evaluadas simultáneamente | Homogeneidad de CVs entre condiciones; Gold Standard como proxy válido de decisión humana experta |
| Gold Standard de expertos | 3-5 RRHH evalúan el mismo conjunto de CVs independientemente | Alta concordancia inter-evaluador (Cohen's κ > 0.6); los expertos no conocen la configuración del sistema |
| Shadow deployment | SISTAC corre en paralelo al proceso manual sin influir en él | Ausencia de contaminación entre condiciones; datos de tiempo no alterados por observación |
| Ablation study | Comparar C1 vs C2 vs C3 isolando contribución de cada componente | Todas las diferencias atribuibles al componente añadido, no a variación en datos |

---

## Field Conventions

<!-- El Coder y Writer siguen estas. El writer-critic las verifica. -->

- Reportar **F1-score macro-averaged** junto con F1 por clase (especialmente clase "apto" vs "no apto")
- Reportar **intervalos de confianza al 95%** para AUC-ROC (bootstrap con B=1000)
- **Métricas de fairness** (DIR, SPD) reportadas a nivel grupal (género, etnia inferida) Y como agregado
- **DIR ≥ 0.8** es el umbral legal (regla 4/5, EEOC) — siempre contextualizar respecto a este umbral
- Ablation study obligatorio para justificar contribución incremental de RAG y de PII anonymization
- Validar la **supresión de PII** con NER independiente (presidio o spaCy) — no asumir que el anonymizer es perfecto
- Tiempos de procesamiento reportados como **mediana ± IQR** (distribuciones de tiempo son sesgadas)
- Todo experimento con componente estocástico requiere `random.seed()` + `np.random.seed()` al inicio del script
- Pseudocódigo de algoritmos en entorno `algorithm` + `algpseudocode` de LaTeX
- Fragmentos de código Python en `listings` con `language=Python, basicstyle=\small\ttfamily`

---

## Notation Conventions

<!-- El Writer y writer-critic las aplican. -->

| Symbol | Meaning | Anti-pattern |
|--------|---------|-------------|
| $F_1$ | F1-score | No usar `F1` sin subíndice ni `f1` en minúscula |
| $\text{AUC-ROC}$ | Area Under the ROC Curve | No usar `AUC` solo (ambiguo) |
| $\text{DIR}$ | Disparate Impact Ratio: $P(\hat{y}=1 \mid g=\text{min}) / P(\hat{y}=1 \mid g=\text{maj})$ | No confundir con Discrimination Index |
| $\text{SPD}$ | Statistical Parity Difference: $P(\hat{y}=1 \mid g=\text{min}) - P(\hat{y}=1 \mid g=\text{maj})$ | No usar "fairness gap" sin definir |
| $T_{\text{cand}}$ | Tiempo de procesamiento por candidato (segundos) | No usar `t` sin subíndice |
| $\kappa$ | Cohen's Kappa para concordancia inter-evaluador | No usar solo "acuerdo" sin métrica |
| $\text{C}_i$ | Configuración experimental ($i \in \{0,1,2,3\}$) | No usar "Config A/B/C" — usar C0-C3 |
| $\hat{y}$ | Predicción del sistema (apto/no apto) | No usar $y$ sin chapeau para predicciones |
| $y^*$ | Etiqueta Gold Standard del experto | No usar $y$ a secas para la etiqueta |

---

## Seminal References

<!-- El Librarian asegura que estos se citan cuando son relevantes. El strategist-critic conoce sus métodos. -->

| Paper | Why It Matters |
|-------|---------------|
| Lewis et al. (2020) — RAG | Paper fundacional de Retrieval-Augmented Generation; C2 y C3 se basan en este paradigma |
| Gan et al. (2024) | F1=87.73% en clasificación de oraciones de CV; benchmark directo para H2 |
| Wilson & Caliskan (2024) | 3M comparaciones: LLMs favorecen nombres de raza blanca 85.1% — motivación central de H3 |
| Meng et al. (2025) | ~361K CVs: sesgo en LLMs es "taste-based" (prejudicio fijo, no relacionado con productividad) |
| Chouldechova (2017) | Teoremas de imposibilidad de fairness: Statistical Parity, Equalized Odds y Predictive Parity no pueden satisfacerse simultáneamente |
| EU AI Act 2024/1689 | Clasifica sistemas de reclutamiento AI como "alto riesgo"; requiere DPIA, supervisión humana, transparencia |
| Saldivar et al. (2025) | 1,730 CVs sintéticos con atributos demográficos controlados — metodología para generación del dataset SISTAC |

---

## Field-Specific Referee Concerns

<!-- El domain-referee y methods-referee vigilan estas. -->

- **"Data leakage en validación"** — siempre separar conjuntos de entrenamiento/embedding y evaluación; no usar CVs del Gold Standard para tune del pipeline RAG
- **"Proxies de PII implícitos"** — la anonimización de nombre/dirección puede ser insuficiente; universidades, clubs, estilos de escritura pueden revelar atributos protegidos
- **"Validez del Gold Standard"** — Cohen's κ < 0.6 invalida el Gold Standard; reportar κ por par de evaluadores
- **"Trade-off equidad-eficacia"** — esperado que C3 tenga peor F1 que C2; el paper debe teorizar cuánta degradación es aceptable
- **"Tamaño del dataset sintético"** — ~1K CVs es pequeño; comparar con ResuméAtlas para mostrar que resultados son robustos
- **"¿Por qué no fine-tuning?"** — el paper debe justificar por qué RAG es preferible a fine-tuning para este contexto (privacidad de datos, actualización dinámica de perfiles)
- **"Validez externa (contexto Matriz/Uruguay)"** — un solo contexto empresarial limita generalización; discutir explícitamente

---

## Quality Tolerance Thresholds

| Quantity | Tolerance | Rationale |
|----------|-----------|-----------|
| F1-score | ± 0.02 | Variabilidad de bootstrap con B=1000 |
| AUC-ROC | ± 0.01 | IC 95% bootstrap |
| DIR/SPD | ± 0.03 | Variabilidad por tamaño de grupo demográfico |
| $T_{\text{cand}}$ (mediana) | ± 0.5s | Variabilidad de latencia de API |
