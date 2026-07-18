import json

import pytest

from backend.app.intelligence.gemma.output_parser import parse_investigation_output


def test_parse_investigation_output_validates_scenarios():
    payload = {
        "case_summary": "Review required",
        "scenarios": [
            {
                "scenario_id": "SCN-1",
                "category": "SUSPICIOUS",
                "name": "Transaction Layering",
                "description": "Rapid movement",
                "expected_signals": [
                    {"signal": "large_incoming_transaction", "weight": 0.5},
                    {"signal": "new_beneficiaries", "weight": 0.5},
                ],
            }
        ],
        "recommended_actions": ["Verify suppliers"],
    }

    parsed = parse_investigation_output(json.dumps(payload))

    assert parsed.case_summary == "Review required"
    assert parsed.scenarios[0].category == "SUSPICIOUS"


def test_parse_investigation_output_rejects_malformed_json():
    with pytest.raises(ValueError):
        parse_investigation_output("not-json")
