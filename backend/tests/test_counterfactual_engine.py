"""Deterministic counterfactual analysis (spec §19)."""

from backend.app.intelligence.scenario_engine.counterfactual_engine import compute_counterfactual
from backend.app.schemas.evidence import EvidenceComparison, SignalEvaluation
from backend.app.schemas.scenario import Scenario


def _scenario(scenario_id: str, category: str) -> Scenario:
    return Scenario(
        scenario_id=scenario_id,
        category=category,
        name=scenario_id,
        description="desc",
        expected_signals=[{"signal": "x", "weight": 1}],
    )


def test_no_steps_when_nothing_is_unknown():
    comparisons = [
        EvidenceComparison(
            scenario_id="S1",
            match_score=0.8,
            signals=[SignalEvaluation(signal="a", status="MATCH", weight=0.5)],
        )
    ]
    steps = compute_counterfactual(
        comparisons=comparisons,
        scenarios=[_scenario("S1", "SUSPICIOUS")],
        anomaly_score=80,
        current_risk_score=80,
    )
    assert steps == []


def test_ranks_by_total_unknown_weight_and_is_cumulative():
    comparisons = [
        EvidenceComparison(
            scenario_id="SUSP",
            match_score=0.9,
            signals=[
                SignalEvaluation(signal="heavy", status="UNKNOWN", weight=0.6),
                SignalEvaluation(signal="light", status="UNKNOWN", weight=0.1),
            ],
        ),
        EvidenceComparison(
            scenario_id="LEGIT",
            match_score=0.2,
            signals=[
                SignalEvaluation(signal="heavy", status="UNKNOWN", weight=0.3),
            ],
        ),
    ]
    scenarios = [_scenario("SUSP", "SUSPICIOUS"), _scenario("LEGIT", "LEGITIMATE")]

    steps = compute_counterfactual(
        comparisons=comparisons, scenarios=scenarios, anomaly_score=50, current_risk_score=90
    )

    assert [step.condition for step in steps] == [
        "If heavy is verified",
        "If light is verified",
    ]
    # First step's "from" matches the case's current risk; each step chains into the next.
    assert steps[0].from_score == 90
    assert steps[1].from_score == steps[0].to_score
    # Resolving the heaviest unknown signal (present in both scenarios) should not
    # increase risk, and must never drop below the fixed deterministic anomaly floor.
    assert steps[0].to_score <= 90
    assert all(step.to_score >= 50 for step in steps)


def test_suspicious_scenarios_resolve_toward_contradict_not_match():
    # A SUSPICIOUS scenario whose only signal is UNKNOWN should have its match score
    # driven toward 0 (not 1) once that signal is "resolved", since resolving evidence
    # in the counterfactual sense means resolving it in the customer's favor.
    comparisons = [
        EvidenceComparison(
            scenario_id="SUSP",
            match_score=0.5,
            signals=[SignalEvaluation(signal="only", status="UNKNOWN", weight=1)],
        )
    ]
    steps = compute_counterfactual(
        comparisons=comparisons,
        scenarios=[_scenario("SUSP", "SUSPICIOUS")],
        anomaly_score=10,
        current_risk_score=50,
    )
    assert len(steps) == 1
    # anomaly_score floor is 10; with the only scenario's match score driven to 0, the
    # new risk should collapse to the anomaly floor.
    assert steps[0].to_score == 10


def test_serializes_with_from_to_keys_for_the_mobile_web_contract():
    comparisons = [
        EvidenceComparison(
            scenario_id="S1",
            match_score=0.5,
            signals=[SignalEvaluation(signal="a", status="UNKNOWN", weight=1)],
        )
    ]
    steps = compute_counterfactual(
        comparisons=comparisons,
        scenarios=[_scenario("S1", "LEGITIMATE")],
        anomaly_score=10,
        current_risk_score=50,
    )
    dumped = steps[0].model_dump(by_alias=True)
    assert set(dumped) == {"condition", "from", "to"}


def test_caps_at_max_steps():
    signals = [SignalEvaluation(signal=f"sig{i}", status="UNKNOWN", weight=1 + i) for i in range(5)]
    comparisons = [EvidenceComparison(scenario_id="S1", match_score=0.5, signals=signals)]
    steps = compute_counterfactual(
        comparisons=comparisons,
        scenarios=[_scenario("S1", "SUSPICIOUS")],
        anomaly_score=10,
        current_risk_score=90,
        max_steps=3,
    )
    assert len(steps) == 3
