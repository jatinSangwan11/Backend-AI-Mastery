import pytest

from payment import (
    PaymentResult,
    RazorpayPaymentProvider,
    StripePaymentProvider,
    charge_payment,
    get_payment_provider,
)


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
    provider = StripePaymentProvider(should_succeed=False)

    result = charge_payment("40", 500, provider)

    assert result == {
        "status": "failed",
        "message": "Payment failed",
    }


def test_stripe_provider_returns_payment_result() -> None:
    provider = StripePaymentProvider()

    result = provider.charge("40", 500)

    assert result == PaymentResult(
        "success",
        "stripe",
        "Payment completed successfully",
    )


def test_stripe_provider_returns_failed_payment_result() -> None:
    provider = StripePaymentProvider(should_succeed=False)

    result = provider.charge("40", 500)

    assert result == PaymentResult(
        "failed",
        "stripe",
        "Payment failed",
    )


def test_razorpay_provider_returns_payment_result() -> None:
    provider = RazorpayPaymentProvider()

    result = provider.charge("40", 500)

    assert result == PaymentResult(
        "success",
        "razorpay",
        "Payment captured successfully",
    )


def test_razorpay_provider_returns_failed_payment_result() -> None:
    provider = RazorpayPaymentProvider(should_succeed=False)

    result = provider.charge("40", 500)

    assert result == PaymentResult(
        "failed",
        "razorpay",
        "Payment failed",
    )
