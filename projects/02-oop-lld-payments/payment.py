from providers import PaymentProviderError, Provider


def charge_payment(user_id: str, amount: int, provider: Provider) -> dict:
    try:
        provider_result = provider.charge(user_id, amount)
    except PaymentProviderError:
        return {
            "status": "failed",
            "message": "Payment provider unavailable",
        }

    if provider_result.status == "success":
        return {
            "status": "success",
            "message": "Payment successful",
        }

    return {
        "status": "failed",
        "message": "Payment failed",
    }
