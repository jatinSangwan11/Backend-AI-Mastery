from dataclasses import dataclass


@dataclass
class PaymentResult:
    status: str
    provider_name: str
    provider_message: str
