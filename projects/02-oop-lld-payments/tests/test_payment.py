import pytest

from payment import PaymentResult, RazorpayPaymentProvider, StripePaymentProvider, charge_payment


def test_charge_payment_prints_stripe_charge_message(capsys) -> None:
    result = charge_payment("40", 500, "stripe")

    output = capsys.readouterr().out

    assert "Charging user 40 amount 500 using stripe" in output
    assert result == {
        "status": "success",
        "message": "Payment successful",
    }


def test_charge_payment_prints_razorpay_charge_message(capsys) -> None:
    result = charge_payment("40", 500, "razorpay")

    output = capsys.readouterr().out

    assert "Charging user 40 amount 500 using razorpay" in output
    assert result == {
        "status": "success",
        "message": "Payment successful",
    }


def test_charge_payment_rejects_unsupported_provider() -> None:
    with pytest.raises(ValueError, match="Unsupported payment provider"):
        charge_payment("40", 500, "paypal")


def test_stripe_provider_returns_payment_result() -> None:
    provider = StripePaymentProvider()

    result = provider.charge("40", 500)

    assert result == PaymentResult(
        "success",
        "stripe",
        "Payment completed successfully",
    )


def test_razorpay_provider_returns_payment_result() -> None:
    provider = RazorpayPaymentProvider()

    result = provider.charge("40", 500)

    assert result == PaymentResult(
        "success",
        "razorpay",
        "Payment captured successfully",
    )
