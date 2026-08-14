import pytest

from models import PaymentResult
from payment import charge_payment
from providers import (
    RazorpayPaymentProvider,
    StripePaymentProvider,
    get_payment_provider,
)


class FakePaymentProvider:
    def __init__(self, payment_result: PaymentResult) -> None:
        self.payment_result = payment_result
        self.charged_users = []

    def charge(self, user_id: str, amount: int) -> PaymentResult:
        self.charged_users.append((user_id, amount))
        return self.payment_result


def test_charge_payment_prints_stripe_charge_message(capsys) -> None:
    provider = get_payment_provider("stripe")

    result = charge_payment("40", 500, provider)

    output = capsys.readouterr().out

    assert "Charging user 40 amount 500 using stripe" in output
    assert result == {
        "status": "success",
        "message": "Payment successful",
    }


def test_charge_payment_prints_razorpay_charge_message(capsys) -> None:
    provider = get_payment_provider("razorpay")

    result = charge_payment("40", 500, provider)

    output = capsys.readouterr().out

    assert "Charging user 40 amount 500 using razorpay" in output
    assert result == {
        "status": "success",
        "message": "Payment successful",
    }


def test_charge_payment_rejects_unsupported_provider() -> None:
    with pytest.raises(ValueError, match="Unsupported payment provider"):
        get_payment_provider("paypal")


def test_charge_payment_returns_failed_result_when_provider_fails() -> None:
    provider = StripePaymentProvider(
        "stripe-test-api-key",
        "sandbox",
        should_succeed=False,
    )

    result = charge_payment("40", 500, provider)

    assert result == {
        "status": "failed",
        "message": "Payment failed",
    }


def test_stripe_provider_returns_payment_result() -> None:
    provider = StripePaymentProvider("stripe-test-api-key", "sandbox")

    result = provider.charge("40", 500)

    assert result == PaymentResult(
        "success",
        "stripe",
        "Payment completed successfully",
    )


def test_stripe_provider_returns_failed_payment_result() -> None:
    provider = StripePaymentProvider(
        "stripe-test-api-key",
        "sandbox",
        should_succeed=False,
    )

    result = provider.charge("40", 500)

    assert result == PaymentResult(
        "failed",
        "stripe",
        "Payment failed",
    )


def test_razorpay_provider_returns_payment_result() -> None:
    provider = RazorpayPaymentProvider("razorpay-merchant-123", "sandbox")

    result = provider.charge("40", 500)

    assert result == PaymentResult(
        "success",
        "razorpay",
        "Payment captured successfully",
    )


def test_razorpay_provider_returns_failed_payment_result() -> None:
    provider = RazorpayPaymentProvider(
        "razorpay-merchant-123",
        "sandbox",
        should_succeed=False,
    )

    result = provider.charge("40", 500)

    assert result == PaymentResult(
        "failed",
        "razorpay",
        "Payment failed",
    )


def test_charge_payment_orchestration_under_fake_provider() -> None:
    provider = FakePaymentProvider(PaymentResult("failed", "fake", "Fake payment failed"))
    result = charge_payment("40", 500, provider)

    assert provider.charged_users == [("40", 500)]
    assert result == {
        "status": "failed",
        "message": "Payment failed",
    }


def test_stripe_provider_stores_stable_config() -> None:
    provider = StripePaymentProvider("custom-stripe-key", "production")

    assert provider.api_key == "custom-stripe-key"
    assert provider.environment == "production"


def test_razorpay_provider_stores_stable_config() -> None:
    provider = RazorpayPaymentProvider("merchant-456", "production")

    assert provider.merchant_id == "merchant-456"
    assert provider.environment == "production"
