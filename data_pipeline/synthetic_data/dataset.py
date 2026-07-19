# ruff: noqa: E501
"""Deterministic, realistic synthetic compliance workspace data.

All people, businesses, accounts, and transactions produced here are fictional.
The generator deliberately models plausible Indian retail-banking and SME activity
without copying records from a real person or institution.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any


@dataclass(frozen=True)
class GeneratedCase:
    payload: dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime


CASE_BLUEPRINTS: tuple[dict[str, Any], ...] = (
    {
        "customer": "Nusantara Textiles",
        "type": "Business",
        "business": "Textile retail",
        "location": "Chennai, Tamil Nadu",
        "amount": 1_200_000,
        "score": 84,
        "status": "OPEN",
        "trigger": "International receipt followed by rapid redistribution to five new beneficiaries",
        "suspicious": "Transaction layering",
        "legitimate": "Export supplier settlement",
        "critical": "Are the five receiving accounts verified business suppliers?",
        "action": "Request supplier invoices and relationship records for all five beneficiaries.",
        "normal_amount": 45_000,
        "channel": "Mobile banking",
    },
    {
        "customer": "Meridian Freight Co.",
        "type": "Business",
        "business": "Regional logistics",
        "location": "Hyderabad, Telangana",
        "amount": 1_140_000,
        "score": 88,
        "status": "ESCALATED",
        "trigger": "Six cash deposits placed below the reporting threshold across separate branches",
        "suspicious": "Cash structuring",
        "legitimate": "Distributed branch collections",
        "critical": "What is the documented source of the deposited cash?",
        "action": "Obtain daily sales ledgers and source-of-funds records from all six branches.",
        "normal_amount": 80_000,
        "channel": "Branch cash deposit",
    },
    {
        "customer": "Lotus Exports",
        "type": "Business",
        "business": "Handicraft export",
        "location": "Jaipur, Rajasthan",
        "amount": 420_000,
        "score": 67,
        "status": "AWAITING_EVIDENCE",
        "trigger": "First payment to a new counterparty in a higher-risk jurisdiction",
        "suspicious": "High-risk counterparty transfer",
        "legitimate": "New sourcing relationship",
        "critical": "Has enhanced due diligence verified the new overseas counterparty?",
        "action": "Complete counterparty ownership checks and verify the purchase order.",
        "normal_amount": 120_000,
        "channel": "Corporate net banking",
    },
    {
        "customer": "Aarav Menon",
        "type": "Individual",
        "business": "Salaried professional",
        "location": "Bengaluru, Karnataka",
        "amount": 850_000,
        "score": 34,
        "status": "UNDER_REVIEW",
        "trigger": "One-off property payment substantially above the customer baseline",
        "suspicious": "Unexplained high-value transfer",
        "legitimate": "Residential property purchase",
        "critical": "Does the signed sale agreement match the developer and payment amount?",
        "action": "Verify the sale agreement against the registered developer and loan disbursement.",
        "normal_amount": 35_000,
        "channel": "NEFT",
    },
    {
        "customer": "Saffron Hospitality",
        "type": "Business",
        "business": "Boutique hotels",
        "location": "Mumbai, Maharashtra",
        "amount": 375_000,
        "score": 72,
        "status": "OPEN",
        "trigger": "Vendor payment from a previously dormant account using a newly observed device",
        "suspicious": "Dormant-account takeover",
        "legitimate": "Property renovation expense",
        "critical": "Was the new device enrolled by an authorized company signatory?",
        "action": "Confirm signatory approval and independently contact the named vendor.",
        "normal_amount": 65_000,
        "channel": "Corporate mobile app",
    },
    {
        "customer": "Maya Krishnan",
        "type": "Individual",
        "business": "Independent consultant",
        "location": "Kochi, Kerala",
        "amount": 210_000,
        "score": 22,
        "status": "CLEARED",
        "trigger": "Recurring overseas consulting receipts from a newly contracted client",
        "suspicious": "Unverified foreign remittance",
        "legitimate": "Professional services income",
        "critical": "Does the consulting agreement explain the sender and payment cadence?",
        "action": "Retain the verified consulting agreement with the case record.",
        "normal_amount": 115_000,
        "channel": "SWIFT inward remittance",
    },
    {
        "customer": "Veda Pharma Distributors",
        "type": "Business",
        "business": "Pharmaceutical distribution",
        "location": "Pune, Maharashtra",
        "amount": 685_000,
        "score": 76,
        "status": "UNDER_REVIEW",
        "trigger": "Invoice amount and beneficiary account differ from the established supplier pattern",
        "suspicious": "Invoice diversion fraud",
        "legitimate": "Supplier banking update",
        "critical": "Did the supplier independently confirm its change of bank account?",
        "action": "Verify the account change using a previously established supplier contact.",
        "normal_amount": 240_000,
        "channel": "RTGS",
    },
    {
        "customer": "BluePeak Electronics",
        "type": "Business",
        "business": "Consumer electronics assembly",
        "location": "Noida, Uttar Pradesh",
        "amount": 1_875_000,
        "score": 18,
        "status": "CLEARED",
        "trigger": "Monthly payroll batch exceeded the recent rolling average",
        "suspicious": "Unauthorized bulk payout",
        "legitimate": "Seasonal payroll and bonus run",
        "critical": "Does the approved payroll register reconcile to the batch total?",
        "action": "Archive the reconciled payroll register and approval record.",
        "normal_amount": 1_450_000,
        "channel": "Corporate bulk upload",
    },
    {
        "customer": "Arjun Rao",
        "type": "Individual",
        "business": "University student",
        "location": "Delhi, NCR",
        "amount": 490_000,
        "score": 91,
        "status": "SUSPICIOUS",
        "trigger": "Multiple unrelated incoming transfers followed by immediate wallet and bank payouts",
        "suspicious": "Money-mule activity",
        "legitimate": "Peer expense aggregation",
        "critical": "Can the customer establish a legitimate relationship with each sender and recipient?",
        "action": "Escalate for enhanced review and obtain explanations for every counterparty.",
        "normal_amount": 12_000,
        "channel": "UPI and IMPS",
    },
    {
        "customer": "Coral Coast Foods",
        "type": "Business",
        "business": "Packaged seafood exporter",
        "location": "Mangaluru, Karnataka",
        "amount": 560_000,
        "score": 47,
        "status": "OPEN",
        "trigger": "Seasonal procurement payment to three first-seen coastal suppliers",
        "suspicious": "Beneficiary splitting",
        "legitimate": "Seasonal inventory purchase",
        "critical": "Do goods-receipt records confirm purchases from all three suppliers?",
        "action": "Match goods receipts, tax invoices, and beneficiary ownership records.",
        "normal_amount": 190_000,
        "channel": "Corporate net banking",
    },
    {
        "customer": "Navya Community Foundation",
        "type": "Non-profit",
        "business": "Education grants",
        "location": "Ahmedabad, Gujarat",
        "amount": 330_000,
        "score": 63,
        "status": "AWAITING_EVIDENCE",
        "trigger": "Grant funds redistributed to newly added field coordinators within one day",
        "suspicious": "Charity fund diversion",
        "legitimate": "Field-program disbursement",
        "critical": "Are the recipients documented coordinators for the funded program?",
        "action": "Request the grant budget, coordinator contracts, and expenditure approvals.",
        "normal_amount": 95_000,
        "channel": "NEFT",
    },
    {
        "customer": "Kaveri Motors",
        "type": "Business",
        "business": "Automobile dealership",
        "location": "Mysuru, Karnataka",
        "amount": 740_000,
        "score": 29,
        "status": "CLOSED",
        "trigger": "High-value manufacturer settlement outside the usual weekly schedule",
        "suspicious": "Unscheduled inventory transfer",
        "legitimate": "Quarter-end vehicle allocation",
        "critical": "Does the manufacturer allocation notice reconcile to the settlement?",
        "action": "Retain the reconciled allocation notice and close the review.",
        "normal_amount": 520_000,
        "channel": "RTGS",
    },
)

OFFICERS = ("Priyan K.", "Anika Varma", "Neel Shah", "Meera Iyer")


def _risk_level(score: int) -> str:
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 35:
        return "MEDIUM"
    return "LOW"


def _inr(value: int) -> str:
    digits = str(abs(value))
    if len(digits) > 3:
        tail = digits[-3:]
        head = digits[:-3]
        groups: list[str] = []
        while head:
            groups.append(head[-2:])
            head = head[:-2]
        digits = ",".join(reversed(groups)) + "," + tail
    return f"₹{digits}"


def _scenario_data(
    case_id: str, blueprint: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    risk = int(blueprint["score"])
    suspicious_score = min(96, risk + 3)
    legitimate_score = max(12, 96 - risk + (18 if risk < 50 else 4))
    uncertain_score = max(14, 58 - abs(risk - 50))
    ids = [f"{case_id}-SCN-001", f"{case_id}-SCN-002", f"{case_id}-SCN-003"]
    scenarios = [
        {
            "scenario_id": ids[0],
            "name": blueprint["suspicious"],
            "category": "SUSPICIOUS",
            "match_score": suspicious_score,
            "description": f"Observed activity is consistent with {str(blueprint['suspicious']).lower()}, subject to unresolved evidence.",
        },
        {
            "scenario_id": ids[1],
            "name": blueprint["legitimate"],
            "category": "LEGITIMATE",
            "match_score": legitimate_score,
            "description": f"The activity may be explained by {str(blueprint['legitimate']).lower()} if supporting records are verified.",
        },
        {
            "scenario_id": ids[2],
            "name": "Insufficient verified context",
            "category": "UNCERTAIN",
            "match_score": uncertain_score,
            "description": "The available evidence is not yet sufficient to resolve the competing explanations.",
        },
    ]
    scenario_evidence = {
        ids[0]: {
            "supporting": [
                "Transaction pattern deviates from the trusted baseline",
                "At least one counterparty is newly observed",
            ],
            "contradicting": ["Customer authentication remained consistent"],
            "unknown": [blueprint["critical"]],
        },
        ids[1]: {
            "supporting": [
                "Customer profile is compatible with the stated purpose",
                "A commercial explanation has been supplied",
            ],
            "contradicting": ["The timing or amount remains atypical"],
            "unknown": [blueprint["critical"]],
        },
        ids[2]: {
            "supporting": ["Decision-critical records remain outstanding"],
            "contradicting": [],
            "unknown": ["Independent counterparty verification", "Complete source-of-funds trail"],
        },
    }
    return scenarios, scenario_evidence


def _transaction_history(
    rng: random.Random,
    case_id: str,
    blueprint: dict[str, Any],
    created_at: datetime,
) -> list[dict[str, Any]]:
    normal = int(blueprint["normal_amount"])
    history: list[dict[str, Any]] = []
    labels = (
        "Known supplier",
        "Utilities",
        "Payroll",
        "Customer receipt",
        "Tax payment",
        "Inventory",
    )
    for index in range(14):
        direction = "IN" if index % 3 == 0 else "OUT"
        amount = max(1_000, round(normal * rng.uniform(0.35, 1.25)))
        history.append(
            {
                "id": f"{case_id}-TXN-{index + 1:03d}",
                "label": labels[index % len(labels)],
                "amount": _inr(amount),
                "timestamp": (created_at - timedelta(days=46 - index * 3, hours=index)).isoformat(),
                "direction": direction,
                "risky": False,
                "riskScore": rng.randint(4, 24),
                "reason": "Within the trusted behavioral range",
                "explanation": "Amount, channel, counterparty familiarity, and timing align with the established baseline.",
                "firedSignals": [],
            }
        )
    history.append(
        {
            "id": str(blueprint["trigger_transaction_id"]),
            "label": str(blueprint["trigger"]),
            "amount": _inr(int(blueprint["amount"])),
            "timestamp": created_at.isoformat(),
            "direction": "OUT" if "receipt" not in str(blueprint["trigger"]).lower() else "IN",
            "risky": True,
            "riskScore": int(blueprint["score"]),
            "reason": "Multiple deterministic anomaly signals fired",
            "explanation": str(blueprint["trigger"]),
            "firedSignals": ["amount_deviation", "counterparty_novelty", "transaction_velocity"],
        }
    )
    return history


def _sandbox(
    rng: random.Random,
    case_id: str,
    blueprint: dict[str, Any],
    transactions: list[dict[str, Any]],
) -> dict[str, Any]:
    risk = int(blueprint["score"])
    stages = [
        (
            "CONTEXT_BUILDER",
            "Build trusted context",
            "DETERMINISTIC",
            "Loaded the customer twin and current transaction.",
        ),
        (
            "ORCHESTRATOR",
            "Plan investigation",
            "GEMMA",
            "Selected evidence checks without making a disposition.",
        ),
        (
            "SCENARIO_GENERATOR",
            "Generate competing scenarios",
            "GEMMA",
            "Produced legitimate, suspicious, and uncertain explanations.",
        ),
        (
            "DETERMINISTIC_TOOLS",
            "Run local analytics",
            "DETERMINISTIC",
            "Calculated amount, velocity, and beneficiary-novelty signals.",
        ),
        (
            "SIMULATOR_SCORER",
            "Score scenario fit",
            "DETERMINISTIC",
            "Compared expected signals with observed evidence.",
        ),
        (
            "EVIDENCE_CRITIC",
            "Challenge the evidence",
            "GEMMA",
            "Separated support, contradiction, and missing context.",
        ),
        (
            "DECISION_EVIDENCE",
            "Find decision-critical evidence",
            "DETERMINISTIC",
            "Ranked unresolved evidence by potential decision impact.",
        ),
        (
            "REPORT_WRITER",
            "Prepare reviewer brief",
            "GEMMA",
            "Summarized verified facts and limitations for human review.",
        ),
    ]
    stage_items = [
        {
            "kind": kind,
            "title": title,
            "actor": actor,
            "summary": summary,
            "input": "Current case-scoped evidence package",
            "output": summary,
            "toolCalls": (
                [
                    {
                        "tool": "calculate_amount_deviation",
                        "args": f"current={blueprint['amount']}, baseline={blueprint['normal_amount']}",
                        "result": f"ratio={int(blueprint['amount']) / int(blueprint['normal_amount']):.2f}",
                    }
                ]
                if actor == "DETERMINISTIC"
                else []
            ),
            "durationMs": rng.randint(18, 145),
        }
        for kind, title, actor, summary in stages
    ]
    source_id = f"{case_id}-SRC"
    customer_id = f"{case_id}-CUSTOMER"
    beneficiary_ids = [f"{case_id}-BEN-{index}" for index in range(1, 4)]
    flow_nodes = [
        {
            "id": source_id,
            "label": "Originating account",
            "kind": "SOURCE",
            "amount": _inr(int(blueprint["amount"])),
        },
        {
            "id": customer_id,
            "label": str(blueprint["customer"]),
            "kind": "CUSTOMER",
            "amount": _inr(int(blueprint["amount"])),
        },
    ] + [
        {
            "id": node_id,
            "label": f"Synthetic beneficiary {index}",
            "kind": "BENEFICIARY",
            "verified": "UNKNOWN" if index < 3 else "VERIFIED",
            "amount": _inr(int(blueprint["amount"]) // 4),
        }
        for index, node_id in enumerate(beneficiary_ids, start=1)
    ]
    return {
        "runId": f"RUN-{case_id}",
        "model": "gemma3:4b",
        "runtime": "Ollama · local",
        "boundaryHeld": True,
        "seed": rng.randint(10_000, 99_999),
        "totalDurationMs": sum(item["durationMs"] for item in stage_items),
        "anomaly": {
            "score": risk,
            "deviationLevel": "Severe" if risk >= 75 else "Moderate" if risk >= 40 else "Mild",
            "signals": [
                {
                    "key": "amount",
                    "label": "Amount deviation",
                    "metric": "ratio",
                    "value": f"{int(blueprint['amount']) / int(blueprint['normal_amount']):.1f}×",
                    "contribution": min(42, risk // 2),
                    "why": "Current amount exceeds the trusted customer range.",
                    "fired": risk >= 30,
                },
                {
                    "key": "beneficiary",
                    "label": "Counterparty novelty",
                    "metric": "first-seen",
                    "value": "Observed",
                    "contribution": 24,
                    "why": "One or more counterparties are absent from the trusted history.",
                    "fired": risk >= 45,
                },
                {
                    "key": "velocity",
                    "label": "Movement velocity",
                    "metric": "minutes",
                    "value": "40 min",
                    "contribution": 21,
                    "why": "Funds moved faster than the historical pattern.",
                    "fired": risk >= 60,
                },
            ],
            "matters": str(blueprint["trigger"]),
            "markedRisk": "The combined deterministic signals exceed the configured review threshold.",
        },
        "stages": stage_items,
        "flow": {
            "nodes": flow_nodes,
            "edges": [
                {"from": source_id, "to": customer_id, "amount": _inr(int(blueprint["amount"]))},
                *[
                    {
                        "from": customer_id,
                        "to": node_id,
                        "amount": _inr(int(blueprint["amount"]) // 4),
                    }
                    for node_id in beneficiary_ids
                ],
            ],
        },
        "transactions": transactions,
        "branches": [
            {
                "id": f"BR-{index:02d}",
                "transactionId": transaction["id"],
                "x": round(0.12 + (index % 4) * 0.24, 2),
                "y": round(0.12 + (index // 4) * 0.2, 2),
                "parents": [] if index == 0 else [f"BR-{index - 1:02d}"],
            }
            for index, transaction in enumerate(transactions)
        ],
    }


def generate_case_dataset(
    *, seed: int = 20260718, now: datetime | None = None
) -> list[GeneratedCase]:
    """Return a deterministic dataset suitable for SQLite seeding."""
    rng = random.Random(seed)
    reference_time = now or datetime.now(UTC)
    generated: list[GeneratedCase] = []
    for index, source in enumerate(CASE_BLUEPRINTS, start=1):
        blueprint = dict(source)
        case_id = f"CASE-{1000 + index}"
        customer_id = f"CUST-{index:03d}"
        transaction_id = f"TXN-{20260000 + index:04d}"
        blueprint["trigger_transaction_id"] = transaction_id
        created_at = reference_time - timedelta(days=(index - 1) % 7, hours=index * 2)
        updated_at = created_at + timedelta(minutes=rng.randint(18, 420))
        scenarios, scenario_evidence = _scenario_data(case_id, blueprint)
        transactions = _transaction_history(rng, case_id, blueprint, created_at)
        risk = int(blueprint["score"])
        normal_amount = int(blueprint["normal_amount"])
        amount = int(blueprint["amount"])
        evidence_matrix = [
            {
                "signal": "Amount within customer baseline",
                "source": "Financial twin",
                "byScenario": {
                    scenarios[0]["scenario_id"]: "CONTRADICT",
                    scenarios[1]["scenario_id"]: "PARTIAL",
                    scenarios[2]["scenario_id"]: "UNKNOWN",
                },
            },
            {
                "signal": "New counterparty observed",
                "source": "Transaction graph",
                "byScenario": {
                    scenarios[0]["scenario_id"]: "MATCH",
                    scenarios[1]["scenario_id"]: "UNKNOWN",
                    scenarios[2]["scenario_id"]: "MATCH",
                },
            },
            {
                "signal": "Commercial document supplied",
                "source": "Document index",
                "byScenario": {
                    scenarios[0]["scenario_id"]: "CONTRADICT",
                    scenarios[1]["scenario_id"]: "MATCH",
                    scenarios[2]["scenario_id"]: "PARTIAL",
                },
            },
            {
                "signal": "Authentication consistent",
                "source": "Device history",
                "byScenario": {
                    scenarios[0]["scenario_id"]: "CONTRADICT",
                    scenarios[1]["scenario_id"]: "MATCH",
                    scenarios[2]["scenario_id"]: "UNKNOWN",
                },
            },
            {
                "signal": str(blueprint["critical"]),
                "source": "Evidence request",
                "byScenario": {scenario["scenario_id"]: "UNKNOWN" for scenario in scenarios},
            },
        ]
        workspace_data = {
            "transaction_count": rng.randint(1_120, 2_480),
            "anomaly_score": min(99, risk + rng.randint(2, 9)),
            "financial_twin": [
                {
                    "label": "Typical amount",
                    "normal": _inr(normal_amount),
                    "current": _inr(amount),
                    "deviated": amount > normal_amount * 1.8,
                },
                {
                    "label": "Transactions / day",
                    "normal": str(rng.randint(2, 7)),
                    "current": str(rng.randint(8, 19)),
                    "deviated": risk >= 45,
                },
                {
                    "label": "Geography",
                    "normal": blueprint["location"],
                    "current": blueprint["location"],
                    "deviated": "jurisdiction" in str(blueprint["trigger"]).lower(),
                },
                {
                    "label": "Channel",
                    "normal": blueprint["channel"],
                    "current": blueprint["channel"],
                    "deviated": False,
                },
            ],
            "investigation": [
                {
                    "label": "Customer baseline loaded",
                    "done": True,
                    "detail": "90-day trusted window",
                },
                {
                    "label": "Deterministic anomaly signals evaluated",
                    "done": True,
                    "detail": f"risk score {risk}/100",
                },
                {
                    "label": "Transaction graph traced",
                    "done": True,
                    "detail": "counterparty and velocity checks complete",
                },
                {
                    "label": "Documents indexed",
                    "done": True,
                    "detail": "commercial context isolated",
                },
                {
                    "label": "Competing scenarios compared",
                    "done": True,
                    "detail": "three explanations retained",
                },
                {
                    "label": "Decision-critical evidence ranked",
                    "done": True,
                    "detail": str(blueprint["critical"]),
                },
            ],
            "scenario_evidence": scenario_evidence,
            "evidence_matrix": evidence_matrix,
            "counterfactual": [
                {
                    "condition": "If commercial records are independently verified",
                    "from": risk,
                    "to": max(8, risk - 18),
                },
                {
                    "condition": "If the decision-critical relationship is verified",
                    "from": max(8, risk - 18),
                    "to": max(6, risk - 48),
                },
            ],
            "transaction_history": transactions,
            "sandbox": _sandbox(rng, case_id, blueprint, transactions),
        }
        anomalies = [
            f"Amount is {amount / normal_amount:.1f}× the trusted baseline",
            "At least one counterparty is newly observed",
            "Transaction purpose requires independent verification",
        ]
        payload = {
            "case_id": case_id,
            "customer_id": customer_id,
            "customer_name": blueprint["customer"],
            "customer_type": blueprint["type"],
            "business": blueprint["business"],
            "trigger_transaction_id": transaction_id,
            "trigger_summary": blueprint["trigger"],
            "trigger_amount": _inr(amount),
            "assigned_to": OFFICERS[(index - 1) % len(OFFICERS)]
            if blueprint["status"] not in {"CLOSED", "CLEARED"}
            else "Completed review",
            "location": blueprint["location"],
            "risk_score": risk,
            "risk_level": _risk_level(risk),
            "anomalies": anomalies,
            "scenarios": scenarios,
            "supporting_evidence": [
                "Transaction graph and baseline comparison completed",
                "Customer and counterparty identifiers were screened",
            ],
            "contradicting_evidence": [
                "At least one aspect of authentication or stated purpose is consistent"
            ],
            "missing_evidence": [blueprint["critical"]],
            "decision_critical_evidence": {
                "question": blueprint["critical"],
                "why_it_matters": "Resolving this fact has the largest modeled impact on the competing scenario ranking.",
                "recommended_action": blueprint["action"],
            },
            "recommended_actions": [
                blueprint["action"],
                "Record the human review rationale before changing case status.",
            ],
            "workspace_data": workspace_data,
        }
        generated.append(
            GeneratedCase(
                payload=payload,
                status=str(blueprint["status"]),
                created_at=created_at,
                updated_at=updated_at,
            )
        )
    return generated
