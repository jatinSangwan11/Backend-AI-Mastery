from dataclasses import dataclass
from typing import Protocol


@dataclass
class PaymentResult:
    status: str
    provider_name: str
    provider_message: str


class Provider(Protocol):
    def charge(self, user_id: str, amount: int) -> PaymentResult:
        ...


class StripePaymentProvider:
    def __init__(
        self,
        api_key: str,
        environment: str,
        should_succeed: bool = True,
    ) -> None:
        self.api_key = api_key
        self.environment = environment
        self.should_succeed = should_succeed

    def convert_to_app_result(self, raw_result: dict) -> PaymentResult:
        if raw_result["paid"] is True:
            status = "success"
        else:
            status = "failed"

        return PaymentResult(
            status,
            "stripe",
            raw_result["description"],
        )

    def charge(self, user_id: str, amount: int) -> PaymentResult:
        print(f"Charging user {user_id} amount {amount} using stripe")
        stripe_raw_response = {
            "id": "pi_123",
            "object": "payment_intent",
            "amount": 500,
            "currency": "inr",
            "status": "succeeded" if self.should_succeed else "failed",
            "paid": self.should_succeed,
            "description": "Payment completed successfully" if self.should_succeed else "Payment failed",
        }
        result = self.convert_to_app_result(stripe_raw_response)
        return result


class RazorpayPaymentProvider:
    def __init__(
        self,
        merchant_id: str,
        environment: str,
        should_succeed: bool = True,
    ) -> None:
        self.merchant_id = merchant_id
        self.environment = environment
        self.should_succeed = should_succeed

    def convert_to_app_result(self, raw_result: dict) -> PaymentResult:
        if raw_result["captured"] is True:
            status = "success"
        else:
            status = "failed"

        return PaymentResult(
            status,
            "razorpay",
            raw_result["description"],
        )

    def charge(self, user_id: str, amount: int) -> PaymentResult:
        print(f"Charging user {user_id} amount {amount} using razorpay")
        razorpay_raw_response = {
            "id": "pay_456",
            "entity": "payment",
            "amount": 500,
            "currency": "INR",
            "status": "captured" if self.should_succeed else "failed",
            "captured": self.should_succeed,
            "description": "Payment captured successfully" if self.should_succeed else "Payment failed",
        }
        result = self.convert_to_app_result(razorpay_raw_response)
        return result


def get_payment_provider(provider_name: str) -> Provider:
    if provider_name == "stripe":
        return StripePaymentProvider("stripe-test-api-key", "sandbox")

    if provider_name == "razorpay":
        return RazorpayPaymentProvider("razorpay-merchant-123", "sandbox")

    raise ValueError("Unsupported payment provider")


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
