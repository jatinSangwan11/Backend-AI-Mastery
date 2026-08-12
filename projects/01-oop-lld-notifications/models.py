from dataclasses import dataclass


@dataclass
class User:
    email: str
    phone_no: str
    device_token: str
