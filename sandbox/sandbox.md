# Pyxis Agent Sandbox

This directory is the central manifest for isolated Pyxis agent simulations. The
canonical implementation files remain in their architecture-defined packages; this
document links them in execution order so they are not copied or allowed to drift.

## Simulation boundary

- Use synthetic customers, transactions, KYC summaries, and documents only.
- Run Gemma through a local provider; never call an external hosted LLM.
- Treat database records and input evidence as read-only.
- Permit deterministic calculations through explicitly registered local tools only.
- Validate structured model output before scoring, storing, or rendering it.
- Keep AI recommendations separate from human reviewer decisions.
- Do not update a financial twin from unresolved or suspicious behavior.

## Agent simulation flow

```text
Synthetic case input
        |
        v
Context Builder
        |
        v
Investigation Orchestrator
        |
        +--> Scenario Generator
        +--> Deterministic analysis tools
        |
        v
Scenario Simulator and Match Scorer
        |
        v
Evidence Critic
        |
        v
Decision-Evidence Agent
        |
        v
Report Writer and deterministic renderer
```

## Core agent files

- [Investigation orchestrator](../intelligence/gemma/orchestrator.py)
- [Scenario generator](../intelligence/gemma/scenario_generator.py)
- [Evidence critic](../intelligence/gemma/evidence_critic.py)
- [Decision-evidence agent](../intelligence/gemma/decision_evidence_agent.py)
- [Report writer](../intelligence/gemma/report_writer.py)
- [Context builder](../intelligence/gemma/context_builder.py)
- [Structured-output parser](../intelligence/gemma/output_parser.py)

## Local Gemma provider files

- [Provider interface](../intelligence/gemma/providers/base.py)
- [Provider package exports](../intelligence/gemma/providers/__init__.py)
- [Transformers provider](../intelligence/gemma/providers/transformers_provider.py)
- [llama.cpp provider](../intelligence/gemma/providers/llamacpp_provider.py)
- [LiteRT-LM provider](../intelligence/gemma/providers/litert_provider.py)

## Member 2 case-assistant files

- [Private local Gemma HTTP client](../local_ai/gemma/client.py)
- [Case assistant](../local_ai/gemma/case_assistant.py)
- [Case-only context builder](../local_ai/gemma/context_builder.py)
- [Evidence critic](../local_ai/gemma/evidence_critic.py)
- [Report writer](../local_ai/gemma/report_writer.py)
- [Structured-output parser](../local_ai/gemma/output_parser.py)
- [Synthetic case generator](../data_pipeline/synthetic_data/dataset.py)

## Agent prompt files

- [Investigation system prompt](../intelligence/prompts/investigation_system.txt)
- [Scenario-generation prompt](../intelligence/prompts/scenario_generation.txt)
- [Evidence-critic prompt](../intelligence/prompts/evidence_critic.txt)
- [Counterfactual-analysis prompt](../intelligence/prompts/counterfactual_analysis.txt)
- [Compliance-report prompt](../intelligence/prompts/compliance_report.txt)

## Deterministic financial-twin tools

- [Twin builder](../intelligence/financial_twin/twin_builder.py)
- [Profile updater](../intelligence/financial_twin/profile_updater.py)
- [Trust gate](../intelligence/financial_twin/trust_gate.py)
- [Behavior features](../intelligence/financial_twin/behavior_features.py)
- [Drift detector](../intelligence/financial_twin/drift_detector.py)

## Deterministic anomaly tools

- [Rule engine](../intelligence/anomaly_detection/rule_engine.py)
- [Statistical detector](../intelligence/anomaly_detection/statistical_detector.py)
- [Isolation Forest adapter](../intelligence/anomaly_detection/isolation_forest.py)
- [Anomaly scorer](../intelligence/anomaly_detection/anomaly_scorer.py)
- [Anomaly explanations](../intelligence/anomaly_detection/explanations.py)

## Deterministic scenario tools

- [Scenario simulator](../intelligence/scenario_engine/simulator.py)
- [Scenario domain schema](../intelligence/scenario_engine/scenario_schema.py)
- [Signal evaluator](../intelligence/scenario_engine/signal_evaluator.py)
- [Match scorer](../intelligence/scenario_engine/match_scorer.py)
- [Counterfactual engine](../intelligence/scenario_engine/counterfactual_engine.py)

## Evidence tools

- [Evidence collector](../intelligence/evidence_engine/evidence_collector.py)
- [Contradiction detector](../intelligence/evidence_engine/contradiction_detector.py)
- [Critical-evidence engine](../intelligence/evidence_engine/critical_evidence.py)
- [Evidence ranker](../intelligence/evidence_engine/evidence_ranker.py)

## Graph-analysis tools

- [Transaction graph](../intelligence/graph_analysis/transaction_graph.py)
- [Relationship analyzer](../intelligence/graph_analysis/relationship_analyzer.py)
- [Money-flow tracer](../intelligence/graph_analysis/money_flow_tracer.py)

## Local retrieval tools

- [Document indexer](../intelligence/retrieval/document_indexer.py)
- [Local retriever](../intelligence/retrieval/local_retriever.py)
- [FAISS store](../intelligence/retrieval/faiss_store.py)

## Member 2 document tools

- [Local parser](../document_processing/parser.py)
- [Deterministic field extractor](../document_processing/extractor.py)
- [Local OCR fallback](../document_processing/ocr.py)
- [Source-addressable indexer](../document_processing/indexer.py)

## Backend integration files

- [Case service](../backend/app/services/case_service.py)
- [Case-assistant service](../backend/app/services/assistant_service.py)
- [Evidence service](../backend/app/services/evidence_service.py)
- [Document service](../backend/app/services/document_service.py)
- [Review service](../backend/app/services/review_service.py)
- [Audit service](../backend/app/services/audit_service.py)
- [Report service](../backend/app/services/report_service.py)
- [Risk-case schema](../backend/app/schemas/case.py)
- [Scenario schema](../backend/app/schemas/scenario.py)
- [Evidence schema](../backend/app/schemas/evidence.py)
- [Report schema](../backend/app/schemas/report.py)
- [Security helpers](../backend/app/core/security.py)

## Simulation entry points and tests

- [Demo runner](../scripts/run_demo.py)
- [Scenario scorer tests](../tests/scenario_tests/test_match_scorer.py)
- [Backend API smoke test](../backend/tests/test_health.py)

## Governing documentation

- [System architecture](../docs/architecture.md)
- [Gemma design](../docs/gemma-design.md)
- [Scenario-engine design](../docs/scenario-engine.md)
- [Security rules](../docs/security.md)
- [API contracts](../docs/api-contracts.md)
- [Demo sequence](../docs/demo-script.md)

## Current readiness

The Member 2 case-management, local assistant, document, audit, review, and report
flows are implemented and independently testable with the synthetic risk-case input.
Member 1's financial-intelligence provider adapters and most intelligence modules are
still architectural placeholders.
