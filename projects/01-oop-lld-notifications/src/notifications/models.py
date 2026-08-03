from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: str
    email: str
    phone_number: str
    slack_id: str


@dataclass(frozen=True)
class Notification:
    subject: str
    message: str

