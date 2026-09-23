# JEV Lab: Technical Exploration & Benchmark Specification

This document records the architectural exploration of the upstream Jev Lab playground ([https://jev-lab.jasontorres.chatgpt.site/](https://jev-lab.jasontorres.chatgpt.site/)) and defines the benchmark fixtures extracted for this workspace.

---

## 1. System One Architecture & Protocol

Jev ("System One") provides a low-latency, typed-decision interface designed for small, discrete judgments within larger compound AI pipelines and agent loops.

### Endpoint Contract
- **Method**: `POST /v1/systemone`
- **Default Model**: `jev-latest` (e.g. `jev-1.13.0` at runtime)
- **Headers**:
  ```http
  Authorization: Bearer <API_KEY>
  Content-Type: application/json
  ```
- **Request Body**:
  ```json
  {
    "model": "jev-latest",
    "state": { ... },
    "questions": {
      "<question_name>": {
        "type": "noul" | "choice" | "score",
        "instructions": "Prompt string referring to state fields...",
        "criteria": { ... } | [ ... ]
      }
    }
  }
  ```

### The Three Typed Primitives
1. **Noul (`noul`)**:
   - Binary decision returning a calibrated probability and boolean decision.
   - Ground truth label is a JSON boolean (`true` or `false`).
   - Criteria describes boundary conditions for `true` vs `false`.
2. **Choice (`choice`)**:
   - Categorical decision over a closed set of named options.
   - Criteria maps option names to qualitative descriptions/rubrics.
   - Ground truth label is the selected option name string.
3. **Score (`score`)**:
   - Ordered discrete rating scale (0 to N-1).
   - Criteria is an ordered list of at least two qualitative level descriptions.
   - Ground truth label is a zero-based integer index.

### Operational Metrics
- **Latency**: Measured per request in milliseconds (`p50` median and `p95` tail latency).
- **Throughput**: Records evaluated per second of wall time.
- **Accuracy**: Exact match on `choice` and `noul`; Mean Absolute Error (MAE) and accuracy on `score`.

---

## 2. The 27 Benchmark Experiments (164 Cases)

The extracted suites contain 27 experiments categorized into 4 operational domains:

### Group A: Core Playground Presets (4 experiments, 36 cases) — `benchmarks/jev_core.jsonl`
1. **Support triage (`support`)** — 12 cases
   - *Subtitle*: Classify, detect urgency, and prioritize.
   - *Pattern*: Map → group → reduce
   - *Questions*:
     - `category` (`choice`): billing, technical, sales, other
     - `urgent` (`noul`): true (outage/blocked) vs false (routine)
     - `severity` (`score`, 4 levels): 0 (no disruption) to 3 (critical work blocked)
2. **Semantic ranking (`ranking`)** — 8 cases
   - *Subtitle*: Find evidence beyond keyword matches.
   - *Pattern*: Map → score → sort
   - *Questions*:
     - `relevance` (`score`, 4 levels): 0 (irrelevant) to 3 (exact answer)
     - `evidence` (`noul`): whether text contains direct factual support
3. **Citation verification (`verification`)** — 8 cases
   - *Subtitle*: Check claims against their evidence.
   - *Pattern*: Map → filter → report
   - *Questions*:
     - `verdict` (`choice`): supported, contradicted, insufficient_evidence
     - `supported` (`noul`): whether claim is strictly supported
4. **Feedback signals (`feedback`)** — 8 cases
   - *Subtitle*: Turn free text into reusable features.
   - *Pattern*: Map → count → route
   - *Questions*:
     - `topic` (`choice`): bugs, performance, pricing, usability, missing_feature
     - `sentiment` (`score`, 3 levels): 0 (negative), 1 (neutral), 2 (positive)
     - `churn` (`noul`): explicit cancellation or churn signal

### Group B: Agentic Reasoning & Integrity (9 experiments, 36 cases) — `benchmarks/jev_agentic.jsonl`
5. **Plan scope checks (`scope`)** — 4 cases
   - *Pattern*: Map → flag → review
   - *Questions*: `membership` (`choice`: inside, outside, ambiguous), `violates` (`noul`)
6. **Premise validation (`premises`)** — 4 cases
   - *Pattern*: Guard → filter → proceed
   - *Questions*: `status` (`choice`: sound, flawed, unverifiable), `assumes` (`noul`)
7. **Behavioral contracts (`contracts`)** — 4 cases
   - *Pattern*: Diff → evaluate → gate
   - *Questions*: `compatibility` (`choice`: compatible, breaking, ambiguous), `changed` (`noul`)
8. **Instruction boundaries (`boundaries`)** — 4 cases
   - *Pattern*: Parse → flag → sanitize
   - *Questions*: `redirects` (`noul`), `kind` (`choice`: benign, prompt_injection, override)
9. **Conversation goal shifts (`goals`)** — 4 cases
   - *Pattern*: Step → detect → adapt
   - *Questions*: `transition` (`choice`: same_goal, refinement, pivot, abandoned), `sameGoal` (`noul`)
10. **Evidence supersession (`supersession`)** — 4 cases
    - *Pattern*: Map → supersede → resolve
    - *Questions*: `relation` (`choice`: supersedes, supplements, contradicts, unrelated), `stale` (`noul`)
11. **Semantic answer pairs (`voting`)** — 4 cases
    - *Pattern*: Pair → classify → cluster
    - *Questions*: `relation` (`choice`: equivalent, complementary, contradictory, distinct), `equivalent` (`noul`)
12. **Agent stopping signals (`termination`)** — 4 cases
    - *Pattern*: Step → check → halt
    - *Questions*: `complete` (`noul`), `irreversibility` (`score`, 4 levels 0-3)
13. **Semantic regression (`regression`)** — 4 cases
    - *Pattern*: Compare → score → report
    - *Questions*: `outcome` (`choice`: regression, neutral, improvement), `candidatePasses` (`noul`)

### Group C: Safety, Governance & Alignment (10 experiments, 60 cases) — `benchmarks/jev_governance.jsonl`
14. **Evidence routing (`evidence-routing`)** — 6 cases
    - *Questions*: `route` (`choice`: support, contradiction, neutral, noisy), `relevant` (`noul`), `contradicts` (`noul`)
15. **Hallucination severity (`severity`)** — 6 cases
    - *Questions*: `support` (`choice`: supported, unsupported, contradicted), `severity` (`score`, 4 levels 0-3)
16. **Terminology consistency (`terminology`)** — 6 cases
    - *Questions*: `usage` (`choice`: approved, deprecated, conflicting, non_standard), `conflict` (`noul`)
17. **Instruction creep (`instruction-creep`)** — 6 cases
    - *Questions*: `kind` (`choice`: benign_clarification, scope_expansion, goal_replacement), `changesGoal` (`noul`)
18. **Freshness routing (`freshness`)** — 6 cases
    - *Questions*: `route` (`choice`: static, recent_web, real_time), `timeSensitive` (`noul`)
19. **Multi-axis triage (`triage`)** — 6 cases
    - *Questions*: `severity` (`score`, 4 levels), `recurrence` (`score`, 3 levels), `effort` (`score`, 3 levels)
20. **Documentation drift (`doc-drift`)** — 6 cases
    - *Questions*: `verdict` (`choice`: aligned, outdated, conflicting, unmentioned), `stale` (`noul`)
21. **Behavioral policy checks (`policy`)** — 6 cases
    - *Questions*: `verdict` (`choice`: compliant, non_compliant, escalation_needed), `violation` (`noul`)
22. **Persona consistency (`persona`)** — 6 cases
    - *Questions*: `consistency` (`choice`: consistent, slight_drift, direct_violation), `violates` (`noul`)
23. **Analogy component checks (`analogy`)** — 6 cases
    - *Questions*: `validity` (`choice`: sound, partial_mismatch, false_analogy), `transfers` (`noul`)

### Group D: Architectural Patterns (4 experiments, 32 cases) — `benchmarks/jev_patterns.jsonl`
24. **Speculative fan-out (`pattern-fan-out`)** — 8 cases
    - *Questions*: `intent` (`choice`), `severity` (`score`), `reproducible` (`noul`), `refund` (`noul`)
25. **Confidence-gated routing (`pattern-confidence`)** — 10 cases
    - *Questions*: `intent` (`choice`) with margin gating for ambiguous cases
26. **Composite scoring (`pattern-composite`)** — 6 cases
    - *Questions*: `impact` (`score`), `reach` (`score`), `ease` (`score`)
27. **Intent routing & handlers (`pattern-intent`)** — 8 cases
    - *Questions*: `intent` (`choice`), `complexity` (`score`)

---

## 3. The 50 Use-Cases Taxonomy

The Jev Lab Use-Case Library defines 50 real-world applications of typed decisions across 8 operational families:

| # | Title | Family | Primitives | Preset Link |
|---|-------|--------|------------|-------------|
| 1 | LLM Faithfulness Scoring | Evidence & reasoning | Noul, Choice | `verification` |
| 2 | Hallucination Severity Binning | Safety & governance | Score, Choice | `severity` |
| 3 | Value-Erosion Scoring in Long-Context | Safety & governance | Score, Noul | — |
| 4 | Uncertainty Localization in Reasoning | Evidence & reasoning | Noul, Choice | — |
| 5 | Semantic Jailbreak Classification | Safety & governance | Choice, Noul | — |
| 6 | Agent Plan Scope Enforcement | Agent orchestration | Choice, Noul | `scope` |
| 7 | Behavioral Contract Compliance | Developer experience | Choice, Noul | `contracts` |
| 8 | Semantic Regression Testing | Developer experience | Choice, Noul | `regression` |
| 9 | Evidence Supersession & Staleness | Evidence & reasoning | Choice, Noul | `supersession` |
| 10 | Semantic Answer Equivalence Voting | Evidence & reasoning | Choice, Noul | `voting` |
| 11 | Prompt Injection Boundary Guard | Safety & governance | Noul, Choice | `boundaries` |
| 12 | Conversation Goal Shift Tracking | Agent orchestration | Choice, Noul | `goals` |
| 13 | Multi-Axis Ticket Triage | Support & operations | Score | `triage` |
| 14 | Customer Feedback Feature Extraction | Support & operations | Choice, Score, Noul | `feedback` |
| 15 | Semantic Document Search Reranking | Recommendation & search | Score, Noul | `ranking` |
| 16 | Terminology & Brand Consistency | Governance & compliance | Choice, Noul | `terminology` |
| 17 | Agent Stopping Signal Detection | Agent orchestration | Noul, Score | `termination` |
| 18 | Instruction Creep & Scope Drift | Agent orchestration | Choice, Noul | `instruction-creep` |
| 19 | Query Freshness Routing | Recommendation & search | Choice, Noul | `freshness` |
| 20 | API & Documentation Drift Detection | Developer experience | Choice, Noul | `doc-drift` |
| 21 | Behavioral Policy Enforcement | Safety & governance | Choice, Noul | `policy` |
| 22 | Persona Voice & Drift Verification | Safety & governance | Choice, Noul | `persona` |
| 23 | Logical Analogy Component Testing | Evidence & reasoning | Choice, Noul | `analogy` |
| 24 | Speculative Fan-Out Intent Engine | Architectural pattern | Choice, Score, Noul | `pattern-fan-out` |
| 25 | Confidence-Gated Review Routing | Architectural pattern | Choice | `pattern-confidence` |
| 26 | RICE Composite Feature Scoring | Architectural pattern | Score | `pattern-composite` |
| 27 | Typed Intent & Complexity Dispatch | Architectural pattern | Choice, Score | `pattern-intent` |
| 28 | Premise Soundness Validation | Evidence & reasoning | Choice, Noul | `premises` |
| 29 | Evidence Multi-Way Routing | Evidence & reasoning | Choice, Noul | `evidence-routing` |
| 30 | Source Provenance Attribution | Evidence & reasoning | Choice, Noul | — |
| 31 | Redaction Verification in PII ETL | Safety & governance | Noul, Choice | — |
| 32 | Claim Extraction Completeness | Evidence & reasoning | Noul, Score | — |
| 33 | Entity Resolution & Deduplication | Data quality & ETL | Choice, Noul | — |
| 34 | Schema Migration Semantic Compatibility| Developer experience | Choice, Noul | — |
| 35 | Query Facet Intent Extraction | Recommendation & search | Choice, Noul | — |
| 36 | Code Review Nit vs Blocker Triage | Developer experience | Score, Choice | — |
| 37 | Churn Intent Detection in Cancellation| Support & operations | Choice, Noul | — |
| 38 | Out-of-Domain Detection for RAG | Recommendation & search | Noul, Score | — |
| 39 | Tool Call Permission Preflight | Agent orchestration | Choice, Noul | — |
| 40 | Subagent Delegation Router | Agent orchestration | Choice, Score | — |
| 41 | Contract Clause Compliance Extraction | Document intelligence | Choice, Noul | — |
| 42 | Invoice Line Item Reconciliation | Document intelligence | Choice, Noul | — |
| 43 | Customer Escalation Severity Triage | Support & operations | Score, Noul | — |
| 44 | Duplicate Payment Detection | Support & operations | Choice, Noul | — |
| 45 | Sentiment-Gated Support Handoff | Support & operations | Score, Noul | — |
| 46 | Synthetic Evaluation Metric Calibration| Developer experience | Score, Choice | — |
| 47 | Context Compression Fidelity Scoring | Evidence & reasoning | Score, Noul | — |
| 48 | Anomaly Severity in System Telemetry | Developer experience | Score, Choice | — |
| 49 | Translation Nuance & Tone Verification| Document intelligence | Choice, Noul | — |
| 50 | Structured Spec vs Code Consistency | Developer experience | Choice, Noul | — |

---

## 4. Evaluation Contract & Methodology

To compare Jev and local open-source/free alternatives (Kev, OpenJev Verdict, NanoJev, open-jev/logit-scoring, ModernBERT/SetFit baselines):

1. **Exact-Match Accuracy**:
   - For `choice`: fraction of cases where predicted option matches ground truth label.
   - For `noul`: fraction of cases where predicted boolean matches ground truth label.
2. **Noul Precision, Recall, & F1**:
   - Assesses sensitivity on positive classes (e.g. `urgent: true`, `violates: true`, `stale: true`).
3. **Score Ordinal Quality**:
   - **MAE (Mean Absolute Error)**: average distance $|pred - label|$.
   - **Exact Score Accuracy**: fraction of predictions with zero error.
4. **Latency & Throughput**:
   - `p50`, `p90`, and `p95` per-case latency in milliseconds.
   - End-to-end throughput in cases per second.
5. **Policy Compliance**:
   - Jev responses are used strictly as an external evaluation reference baseline.
   - Ground truth benchmark labels remain independent and objective.
