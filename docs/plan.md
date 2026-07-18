# Gemma Financial Compliance & Risk Triage — AI & Backend Architecture Plan

Reference base: `mongodb-industry-solutions/fsi-aml-fraud-detection` (ThreatSight 360) — dual-backend
microservices + LangGraph multi-agent SAR pipeline + MongoDB Atlas (Vector Search, Atlas Search,
$rankFusion, $graphLookup, Change Streams). This plan keeps that skeleton but swaps the model layer
to **Gemma** (self-hosted / Ollama / vLLM, not Bedrock) and adds the **explainable multi-agent risk
sandbox** as the core novelty. No frontend scope here — backend + AI system design only.

---

## 1. Core Novelty — What We're Actually Building

Not just "flag transaction → score it." For every flagged transaction or transaction cluster, a
**multi-agent sandbox** runs a structured investigation that answers four questions in order:

1. **Why** was this transaction / set of transactions marked risky? (evidence + reasoning trace)
2. **What might happen** — near-term projection if this is left unaddressed (single event impact)
3. **What would happen if this pattern continues** — simulated trajectory (velocity, escalation,
   typology match against known laundering/fraud patterns)
4. **What should the risk analyst do** — concrete recommended actions, ranked, with confidence

All four are agent-generated, grounded in retrieved evidence (never freeform hallucination), and
persisted so the same case is auditable later.

On top of that: the system **auto-tunes per user/entity** — same transaction shape triggers a
different agent workflow depth and different thresholds depending on the individual's or
organization's behavioral baseline and credential/identity risk profile (KYC tier, watchlist
proximity, historical false-positive rate, account age, etc). This is "adaptive triage," not a
static rule engine.

---

## 2. High-Level System Layers

```
┌─────────────────────────────────────────────────────────────────────┐
│ Layer 4: Reporting & Audit         → compliance-ready reports, SAR   │
├─────────────────────────────────────────────────────────────────────┤
│ Layer 3: Multi-Agent Sandbox       → Gemma-powered LangGraph agents  │
│          (explainability + simulation + recommendation)              │
├─────────────────────────────────────────────────────────────────────┤
│ Layer 2: Adaptive Risk Engine      → per-entity behavioral profiling,│
│          dynamic threshold tuning, credential/identity scrutiny      │
├─────────────────────────────────────────────────────────────────────┤
│ Layer 1: Ingestion & Detection     → transaction stream, rules,      │
│          vector similarity, entity resolution                        │
├─────────────────────────────────────────────────────────────────────┤
│ Layer 0: Data Platform             → MongoDB Atlas (documents,       │
│          vector, search, graph, change streams)                      │
└─────────────────────────────────────────────────────────────────────┘
```

Two FastAPI services (mirroring the reference repo's dual-backend split), plus one new service for
the sandbox:

| Service | Port | Responsibility |
|---|---|---|
| `risk-backend` | 8000 | Transaction ingestion, rules engine, vector search, adaptive scoring |
| `compliance-backend` | 8001 | Entity/KYC management, entity resolution, document analysis, case store |
| `sandbox-orchestrator` | 8002 | Gemma multi-agent workflows: explain / simulate / recommend, sandbox runs |

All three share one MongoDB Atlas cluster, separated by collection namespace.

---

## 3. Data Model (MongoDB Atlas)

Core collections:

- `entities` — individuals & organizations, KYC tier, credential verification status, aliases,
  identifiers, risk profile, embedding vector.
- `transactions` — amount, parties, channel, device, geo (GeoJSON), timestamp, embedding vector,
  raw risk score.
- `behavior_profiles` — **per-entity rolling baseline**: avg transaction size, usual counterparties,
  usual geography/time windows, device fingerprints, velocity stats, decayed over time (EWMA).
  This is what drives auto-tuning (Section 5).
- `credential_signals` — KYC/KYB verification level, document authenticity checks, watchlist/PEP
  screening hits, account age, prior false-positive/true-positive history, login/auth anomaly
  signals (impossible travel, new device, etc).
- `risk_models` — versioned, hot-reloadable multi-factor models (kept from reference repo's
  Change-Streams-driven config).
- `sandbox_runs` — one document per multi-agent investigation: input transaction(s)/entity, full
  agent trace, evidence citations, why/what-if/if-continues/recommendation outputs, human review
  state. This is the audit artifact.
- `typology_library` — known fraud/AML pattern descriptions + embeddings (structuring, layering,
  smurfing, account takeover, mule network, etc), used as grounding/RAG context for agents.
- `compliance_policies` — regulatory text corpus (FinCEN-style), RAG-searchable, used by Report
  Agent for citations.
- `reports` — generated compliance-ready output documents (versioned, exportable).

Indexes: Atlas Vector Search on `transactions.embedding`, `entities.embedding`,
`typology_library.embedding`, `compliance_policies.embedding`; Atlas Search (fuzzy + autocomplete)
on entity name/address; `$graphLookup`-friendly relationship edges collection
(`entity_relationships`) for network hops; Change Streams on `risk_models` and `sandbox_runs` for
live status.

---

## 4. Layer 1 — Ingestion & Detection (risk-backend)

Kept close to the reference repo's fraud engine, generalized beyond transactions to also cover
onboarding documents:

1. **Ingest** — transaction stream (simulated or real feed) + onboarding document uploads
   (parsed via OCR/text extraction into structured fields).
2. **Rules pass** — deterministic checks (amount thresholds, velocity, geo-distance from usual
   location, new device, sanctions list match).
3. **Vector similarity pass** — embed transaction (Gemma embedding or dedicated embedding model)
   → Atlas Vector Search against `typology_library` and historical flagged transactions →
   similarity score per known pattern.
4. **Composite raw score** — weighted combination (config from `risk_models`), same pattern as
   reference repo's `WEIGHT_AMOUNT`, `WEIGHT_LOCATION`, etc., but weights become entity-specific
   in Layer 2.
5. **Threshold check** — if raw score crosses the entity's *current adaptive threshold* (not a
   global constant), the transaction/cluster is pushed into the sandbox queue.

---

## 5. Layer 2 — Adaptive Risk Engine (the "auto-tune" requirement)

This is the layer that makes the system behave differently per user based on behavior and
credential scrutiny. Two feedback loops:

### 5.1 Behavioral auto-tuning
- Each entity has a `behavior_profiles` document updated incrementally after every transaction
  (EWMA on amount, frequency, geography, counterparties, device).
- A transaction's *anomaly score* is computed relative to **that entity's own baseline**, not a
  global average — e.g. a $50k transfer is normal for one business account and extreme for
  another.
- Thresholds for "flag" / "escalate to sandbox" / "auto-block" are derived per entity:
  `threshold = base_threshold * credential_multiplier * history_multiplier`
- `history_multiplier` decreases sensitivity for entities with a long track record of true
  negatives (fewer false alarms → less friction), and increases it for entities with prior
  confirmed fraud/AML findings.

### 5.2 Credential/identity-based scrutiny
- `credential_signals` feed a `credential_multiplier`: weaker KYC tier, unverified documents,
  PEP/watchlist proximity, brand-new account, or recent auth anomalies push the multiplier up
  (more scrutiny, lower threshold to trigger sandbox, deeper agent workflow requested).
- Strong, long-verified, low-risk credential profiles get a lighter-touch workflow (fewer agent
  hops, faster path to auto-clear) — this is what "perform differently for user based on their
  behaviour and credential scrutiny" means concretely.
- This multiplier is recomputed on every KYC review or credential event (not just on schedule),
  via a MongoDB Change Stream trigger.

### 5.3 Workflow depth selection
Adaptive engine doesn't just set a score threshold — it selects **which agents run and how deep**:

| Profile | Sandbox depth |
|---|---|
| Low credential risk + stable behavior baseline | Explainer agent only (fast why-flag) |
| Medium risk OR moderate behavior deviation | Explainer + Simulator agents |
| High credential risk OR severe behavior deviation OR watchlist proximity | Full pipeline: Explainer + Simulator + Network agent + Recommender + Report Agent, with mandatory human review gate |

This routing decision itself is logged into `sandbox_runs.routing_rationale` so it's auditable —
the system must be able to explain why it chose a given depth, too.

---

## 6. Layer 3 — Multi-Agent Sandbox (the core novelty)

Built on LangGraph, orchestrated by `sandbox-orchestrator`, all reasoning steps run against
**Gemma** (e.g. Gemma 3 27B/12B served via vLLM/Ollama with an OpenAI-compatible endpoint,
`with_structured_output`-style JSON schema enforcement for deterministic agent decisions — same
pattern the reference repo uses with Claude Haiku, just swapped to a self-hosted Gemma endpoint).

### Agent roster

1. **Triage Agent**
   Classifies the alert type (fraud vs AML vs sanctions vs behavioral anomaly), gathers evidence
   in parallel: entity profile, transaction history, network edges, watchlist hits, credential
   signals. Output: alert classification + evidence bundle.

2. **Explainer Agent** *(answers "why was this flagged")*
   Consumes evidence bundle + matched typology from vector search. Produces a structured
   explanation: which specific signals fired (amount deviation %, geo distance, velocity, device
   novelty, typology similarity score), each tied to a citation from evidence — no unsupported
   claims. This is the "glass" transparency layer — every claim must trace back to a retrieved
   fact or computed metric.

3. **Simulator Agent** *(answers "what might happen" / "what if this continues")*
   Two sub-outputs:
   - **Immediate impact projection**: plausible near-term outcome of this single transaction
     given the classification (e.g. "consistent with early-stage structuring; single instance
     unlikely to trigger CTR but establishes pattern").
   - **Continuation trajectory**: runs a lightweight quantitative projection (not just LLM prose)
     using the entity's velocity/amount trend from `behavior_profiles` — e.g. extrapolate
     transaction count/volume over next N days if the current pattern holds, compare against
     known typology thresholds (structuring just-under-$10k pattern, rapid layering hops, mule
     fan-out). LLM narrates the quantitative projection; it doesn't invent numbers.

4. **Network Agent** (full-depth workflow only)
   `$graphLookup` traversal of `entity_relationships` + transaction graph to check whether this
   entity sits near other flagged/high-risk entities (shared address, shared device, rapid
   fan-in/fan-out, mule network shape).

5. **Recommender Agent** *(answers "what should the analyst do")*
   Given explanation + simulation + network context, produces a ranked action list: e.g. "file
   SAR," "request enhanced due diligence documents," "temporarily hold transaction," "no action —
   monitor," each with a confidence score and the evidence that supports it. Never auto-executes
   irreversible actions — always output is a recommendation for human sign-off.

6. **Compliance QA Agent**
   Validates the full chain (explanation grounded? simulation numbers consistent with source
   data? recommendation proportionate to risk level?). On failure, loops back to Explainer/
   Simulator for correction — same self-correction loop pattern as the reference repo's
   Compliance QA → Case Analyst loop.

7. **Human-in-the-Loop gate**
   `interrupt_before` checkpoint (LangGraph) before any recommendation is finalized for
   medium/high-risk cases, using `MongoDBSaver` so an analyst can resume review hours/days later
   with zero context loss — reused directly from the reference repo pattern.

### Sandbox execution flow

```
Transaction/Cluster flagged by adaptive engine
        │
        ▼
   Triage Agent  ──(parallel fetch)──▶ entity / txn history / network / watchlist / credentials
        │
        ▼
   Explainer Agent ──▶ "why flagged" (grounded, cited)
        │
        ▼
   Simulator Agent ──▶ "what might happen" + "what if it continues" (quant + narrated)
        │
        ▼
   [Network Agent]  (conditional, high-depth workflow only)
        │
        ▼
   Recommender Agent ──▶ ranked actions + confidence
        │
        ▼
   Compliance QA Agent ──▶ validate / loop back if inconsistent
        │
        ▼
   Human Review Gate (interrupt_before) ──▶ analyst approves/edits/rejects
        │
        ▼
   Persist sandbox_runs + emit Change Stream event ──▶ report generation
```

Every step's input/output is written into `sandbox_runs.trace[]` — this is what gives the "glassy"
transparency: the full reasoning chain is inspectable, not just a final risk score.

### Why Gemma specifically
- Self-hostable (vLLM/Ollama) → keeps sensitive financial data off third-party inference APIs,
  important for compliance data residency.
- Structured output support (JSON schema constrained decoding) needed for
  `with_structured_output`-equivalent reliable agent handoffs.
- Smaller Gemma variant (e.g. 12B) can run the lightweight Explainer path for low-risk cases;
  larger variant (27B) reserved for high-depth Simulator/Recommender/QA reasoning — this dual-size
  routing is itself part of the adaptive-depth design (cheap model for cheap cases, expensive
  model only when credential/behavior risk justifies it).

---

## 7. Layer 4 — Reporting & Audit

- **Report Agent** (extension of Recommender/QA output) assembles a compliance-ready document:
  entity summary, evidence, explanation, simulation/trajectory, recommendation, analyst decision,
  full audit trail — grounded via RAG over `compliance_policies` for correct regulatory framing
  and citations.
- Exportable (PDF/JSON) case file, immutable once analyst signs off (append-only audit log
  pattern, same as reference repo's "immutable audit trail").
- All `sandbox_runs` and `reports` are queryable for after-the-fact regulator/audit review —
  supports "why did the system do X on date Y" queries indefinitely.

---

## 8. API Surface (backend only)

`risk-backend` (8000)
- `POST /transactions/evaluate` — score a transaction against adaptive threshold
- `GET /entities/{id}/behavior-profile`
- `POST /risk-models` / `PUT /risk-models/{id}/activate`

`compliance-backend` (8001)
- `POST /entities` (onboarding) / entity resolution endpoints (Atlas Search + Vector + $rankFusion,
  reused from reference repo pattern)
- `POST /documents/analyze` — onboarding document extraction + credential signal update
- `GET /entities/{id}/credential-signals`

`sandbox-orchestrator` (8002)
- `POST /sandbox/investigate` — trigger multi-agent run for a transaction/entity/cluster
- `GET /sandbox/runs/{id}` — full trace retrieval
- `GET /sandbox/runs/{id}/stream` — SSE live pipeline status (reused ReactFlow/SSE pattern from
  reference repo, backend-side only here)
- `POST /sandbox/runs/{id}/review` — human-in-the-loop decision submission
- `POST /reports/generate` — compile final compliance report from a completed run

---

## 9. Build Sequence

1. Stand up MongoDB Atlas cluster + indexes (vector, search, graph edges) — copy reference repo's
   index definitions as starting point, extend for `behavior_profiles` and `credential_signals`.
2. Port/rebuild `risk-backend` ingestion + rules + vector scoring (swap Bedrock embeddings →
   Gemma/embedding-model endpoint).
3. Build `behavior_profiles` + `credential_signals` update pipelines and the adaptive
   threshold/multiplier logic (Layer 2) — this can be tested independently with synthetic data
   before agents exist.
4. Stand up `sandbox-orchestrator` with LangGraph + Gemma endpoint; implement Triage + Explainer
   agents first (single most important novelty: grounded "why").
5. Add Simulator Agent (quant trajectory + narration).
6. Add Network Agent, Recommender, Compliance QA loop, Human Review gate + `MongoDBSaver`.
7. Wire adaptive routing (Section 5.3) so depth changes per entity profile.
8. Build Report Agent + audit/export.
9. Synthetic data generation notebooks (adapt reference repo's transaction + entity generators to
   include richer behavior history and credential/KYC signal variety for tuning tests).

---

## 10. What's Deliberately Reused vs. New vs. Deferred

**Reused from reference repo:** dual/triple FastAPI microservice split, MongoDB Atlas
Vector+Search+Graph+Change Streams usage, LangGraph multi-agent pattern with `interrupt_before` +
`MongoDBSaver`, self-correcting QA loop, immutable audit trail concept.

**New here:** Gemma as the model backbone (self-hosted, not Bedrock/Claude), per-entity adaptive
threshold + workflow-depth engine driven by behavior profile and credential scrutiny, explicit
Explainer/Simulator separation (why vs. what-happens-next vs. what-if-continues as distinct
grounded agent outputs), dual-size model routing for cost/depth tuning.

**Deferred (frontend, per your instruction):** UI/sandbox visualization, "glassy prism" visual
design — not covered in this document.