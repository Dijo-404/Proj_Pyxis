"""Cloud Gemma provider selection, structured-output calls, and graceful degradation."""

from datetime import datetime

import httpx
import pytest

from backend.app.core.config import Settings
from backend.app.intelligence.gemma.provider import (
    GeminiGemmaProvider,
    LocalFallbackGemmaProvider,
    build_investigation_provider,
    describe_investigation_provider,
)
from backend.app.schemas.anomaly import AnomalyAssessment
from backend.app.schemas.financial_twin import FinancialTwin
from backend.app.schemas.scenario import GemmaInvestigation
from backend.app.schemas.transaction import TransactionInput
from backend.app.services.errors import ExternalAIUnavailableError
from backend.app.services.investigation_service import InvestigationService


@pytest.fixture
def mock_transaction_twin_anomaly() -> tuple[TransactionInput, FinancialTwin, AnomalyAssessment]:
    transaction = TransactionInput(
        transaction_id="TXN-1",
        customer_id="CUST-1",
        source_account="ACC-1",
        destination_account="ACC-2",
        amount=500000,
        currency="INR",
        transaction_type="BANK_TRANSFER",
        direction="CREDIT",
        timestamp=datetime(2026, 1, 1, 10, 0, 0),
        channel="MOBILE_BANKING",
        country="India",
        beneficiary_id="BEN-1",
        status="SUCCESS",
    )
    twin = FinancialTwin.demo_baseline("CUST-1")
    anomaly = AnomalyAssessment(score=80, risk_level="HIGH", deviation_level="SEVERE")
    return transaction, twin, anomaly


def _settings(**overrides: object) -> Settings:
    return Settings(**overrides)


def test_cloud_provider_requires_all_three_settings() -> None:
    # Missing key, missing opt-in, and wrong provider name each fall back to local.
    assert isinstance(
        build_investigation_provider(_settings(gemma_provider="gemini", allow_external_ai=True)),
        LocalFallbackGemmaProvider,
    )
    assert isinstance(
        build_investigation_provider(
            _settings(gemma_provider="gemini", gemini_api_key="k", allow_external_ai=False)
        ),
        LocalFallbackGemmaProvider,
    )
    assert isinstance(
        build_investigation_provider(
            _settings(gemma_provider="ollama", allow_external_ai=True, gemini_api_key="k")
        ),
        LocalFallbackGemmaProvider,
    )
    assert isinstance(
        build_investigation_provider(
            _settings(gemma_provider="gemini", allow_external_ai=True, gemini_api_key="k")
        ),
        GeminiGemmaProvider,
    )


def test_describe_provider_never_overclaims_the_privacy_boundary() -> None:
    local_model, local_runtime, local_boundary = describe_investigation_provider(_settings())
    assert local_boundary is True
    assert "fallback" in local_runtime.lower()

    cloud_model, cloud_runtime, cloud_boundary = describe_investigation_provider(
        _settings(gemma_provider="gemini", allow_external_ai=True, gemini_api_key="k")
    )
    assert cloud_boundary is False
    assert "gemini" in cloud_runtime.lower()
    assert cloud_model == _settings().gemini_model


def test_gemini_provider_rejects_empty_api_key() -> None:
    with pytest.raises(ValueError, match="API key"):
        GeminiGemmaProvider(api_key="", model="gemma-3-27b-it")


def test_gemini_provider_calls_generate_content_and_returns_text() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1beta/models/gemma-3-27b-it:generateContent"
        assert request.url.params["key"] == "test-key"
        return httpx.Response(
            200,
            json={"candidates": [{"content": {"parts": [{"text": '{"case_summary":"ok"}'}]}}]},
        )

    provider = GeminiGemmaProvider(
        api_key="test-key", model="gemma-3-27b-it", transport=httpx.MockTransport(handler)
    )
    assert provider.investigate({"a": 1}) == '{"case_summary":"ok"}'


def test_gemini_provider_raises_on_http_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        del request
        return httpx.Response(503, json={"error": "unavailable"})

    provider = GeminiGemmaProvider(
        api_key="k", model="gemma-3-27b-it", transport=httpx.MockTransport(handler)
    )
    with pytest.raises(ExternalAIUnavailableError):
        provider.investigate({})


def test_gemini_provider_raises_on_malformed_envelope() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        del request
        return httpx.Response(200, json={"unexpected": "shape"})

    provider = GeminiGemmaProvider(
        api_key="k", model="gemma-3-27b-it", transport=httpx.MockTransport(handler)
    )
    with pytest.raises(ExternalAIUnavailableError, match="invalid response envelope"):
        provider.investigate({})


class _AlwaysFailsProvider:
    def investigate(self, evidence_package: dict) -> str:
        raise ExternalAIUnavailableError("simulated outage")


class _BadThenGoodProvider:
    def __init__(self) -> None:
        self.calls = 0

    def investigate(self, evidence_package: dict) -> str:
        self.calls += 1
        if self.calls == 1:
            return "not json"
        return LocalFallbackGemmaProvider().investigate(evidence_package)


def test_investigation_service_degrades_gracefully_after_retry_fails(mock_transaction_twin_anomaly):
    transaction, twin, anomaly = mock_transaction_twin_anomaly
    service = InvestigationService(provider=_AlwaysFailsProvider())
    result = service.investigate(transaction, twin, anomaly)
    assert isinstance(result, GemmaInvestigation)
    assert result.scenarios  # the deterministic fallback always has scenarios


def test_investigation_service_succeeds_on_stricter_retry(mock_transaction_twin_anomaly):
    transaction, twin, anomaly = mock_transaction_twin_anomaly
    flaky = _BadThenGoodProvider()
    service = InvestigationService(provider=flaky)
    result = service.investigate(transaction, twin, anomaly)
    assert flaky.calls == 2
    assert isinstance(result, GemmaInvestigation)
    assert result.scenarios
