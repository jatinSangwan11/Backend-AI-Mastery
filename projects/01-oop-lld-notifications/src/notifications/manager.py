from notifications.models import Notification, User
from notifications.senders import NotificationSender


class NotificationManager:
    def __init__(self, senders: list[NotificationSender]) -> None:
        self._senders = senders

    def notify(self, user: User, notification: Notification) -> None:
        for sender in self._senders:
            sender.send(user, notification)

