"""Import and display a synthetic Member 2 risk case through the local API."""

import argparse
import json

import httpx

from data_pipeline.synthetic_data.dataset import generate_case_dataset
from local_ai.gemma.client import validate_local_base_url


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000/api/v1",
        help="Private or loopback Pyxis API base URL",
    )
    parser.add_argument(
        "--case-id",
        default="CASE-1001",
        help="Case ID from the deterministic synthetic dataset",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    base_url = f"{validate_local_base_url(arguments.base_url)}/"
    generated = generate_case_dataset()
    selected = next(
        (item for item in generated if item.payload["case_id"] == arguments.case_id),
        None,
    )
    if selected is None:
        available = ", ".join(str(item.payload["case_id"]) for item in generated)
        raise SystemExit(f"Unknown synthetic case ID. Available cases: {available}")
    payload = selected.payload

    with httpx.Client(
        base_url=base_url,
        timeout=30,
        trust_env=False,
        follow_redirects=False,
    ) as client:
        response = client.post("cases/import", json=payload)
        if response.status_code == 409:
            response = client.get(f"cases/{payload['case_id']}")
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    main()
