from providers import Provider


def charge_payment(user_id: str, amount: int, provider: Provider) -> dict:
    provider_result = provider.charge(user_id, amount)

    if provider_result.status == "success":
        return {
            "status": "success",
            "message": "Payment successful",
        }

    return {
        "status": "failed",
        "message": "Payment failed",
    }
