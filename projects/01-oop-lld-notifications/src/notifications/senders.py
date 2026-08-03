from abc import ABC, abstractmethod

from notifications.models import Notification, User


class NotificationSender(ABC):
    @abstractmethod
    def send(self, user: User, notification: Notification) -> None:
        """Send a notification to a user."""


class EmailSender(NotificationSender):
    def send(self, user: User, notification: Notification) -> None:
        raise NotImplementedError


class SmsSender(NotificationSender):
    def send(self, user: User, notification: Notification) -> None:
        raise NotImplementedError


class SlackSender(NotificationSender):
    def send(self, user: User, notification: Notification) -> None:
        raise NotImplementedError

