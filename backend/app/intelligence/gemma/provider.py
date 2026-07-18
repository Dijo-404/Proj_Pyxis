import json
from typing import Protocol


class GemmaProvider(Protocol):
    def investigate(self, evidence_package: dict) -> str: ...


class LocalFallbackGemmaProvider:
    def investigate(self, evidence_package: dict) -> str:
        return json.dumps(
            {
                "case_summary": (
                    "Local Gemma investigation indicates the transaction requires review "
                    "against competing legitimate and suspicious scenarios."
                ),
                "recommended_actions": [
                    "Verify beneficiary supplier relationships",
                    "Request source-of-funds evidence",
                ],
                "scenarios": [
                    {
                        "scenario_id": "SCN-LEGIT-001",
                        "category": "LEGITIMATE",
                        "name": "Legitimate Business Payment",
                        "description": (
                            "The transaction may represent a valid business settlement or "
                            "expansion payment."
                        ),
                        "expected_signals": [
                            {"signal": "invoice_exists", "weight": 0.25},
                            {"signal": "verified_supplier_relationships", "weight": 0.35},
                            {"signal": "business_profile_alignment", "weight": 0.2},
                            {"signal": "large_incoming_transaction", "weight": 0.2},
                        ],
                    },
                    {
                        "scenario_id": "SCN-SUSP-001",
                        "category": "SUSPICIOUS",
                        "name": "Transaction Layering",
                        "description": (
                            "Large unusual funds may be moving through the account toward "
                            "weakly known beneficiaries."
                        ),
                        "expected_signals": [
                            {"signal": "large_incoming_transaction", "weight": 0.3},
                            {"signal": "rapid_outgoing_transfers", "weight": 0.2},
                            {"signal": "new_beneficiaries", "weight": 0.3},
                            {"signal": "weak_business_explanation", "weight": 0.2},
                        ],
                    },
                    {
                        "scenario_id": "SCN-UNC-001",
                        "category": "UNCERTAIN",
                        "name": "Insufficient Relationship Evidence",
                        "description": (
                            "The case cannot be resolved without stronger beneficiary and "
                            "document evidence."
                        ),
                        "expected_signals": [
                            {"signal": "missing_supplier_verification", "weight": 0.6},
                            {"signal": "incomplete_documentation", "weight": 0.4},
                        ],
                    },
                ],
            }
        )
