from typing import Protocol

from models import User
from senders import EmailSender, PushSender, SmsSender


class SecurityAlertChannel(Protocol):
    channel_type: str

    def notify(self, user: User) -> None:
        ...


class SecurityEmailAlertChannel:
    def __init__(self, email_sender: EmailSender, channel_type: str) -> None:
        self.email_sender = email_sender
        self.channel_type = channel_type

    def notify(self, user: User) -> None:
        self.email_sender.send(
            user.email,
            "Security Alert",
            "New login detected on your account",
        )


class SecuritySmsAlertChannel:
    def __init__(self, sms_sender: SmsSender, channel_type: str) -> None:
        self.sms_sender = sms_sender
        self.channel_type = channel_type

    def notify(self, user: User) -> None:
        self.sms_sender.send(user.phone_no, "Security Alert: New login detected on your account")


class SecurityPushAlertChannel:
    def __init__(self, push_sender: PushSender, channel_type: str) -> None:
        self.push_sender = push_sender
        self.channel_type = channel_type

    def notify(self, user: User) -> None:
        self.push_sender.send(
            user.device_token,
            "Security Alert",
            "New login detected on your account",
        )


class SecurityAlertNotifier:
    def __init__(self, configured_channels: list[SecurityAlertChannel]) -> None:
        self.configured_channels = configured_channels

    def notify(self, user: User, enabled_channels: list[str]) -> None:
        for channel in self.configured_channels:
            notify = getattr(channel, "notify", None)
            if not callable(notify):
                raise TypeError("Invalid security alert channel")

            if channel.channel_type in enabled_channels:
                notify(user)
