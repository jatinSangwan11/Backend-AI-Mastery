from notifications.manager import NotificationManager
from notifications.models import Notification, User
from notifications.senders import NotificationSender
from notifications.user_service import UserService


class SpySender(NotificationSender):
    def __init__(self) -> None:
        self.sent: list[tuple[User, Notification]] = []

    def send(self, user: User, notification: Notification) -> None:
        self.sent.append((user, notification))


def test_notification_manager_sends_to_all_channels() -> None:
    user = User(
        id="user-1",
        email="jatin@example.com",
        phone_number="+910000000000",
        slack_id="U123",
    )
    notification = Notification(subject="Hello", message="Welcome")
    email = SpySender()
    sms = SpySender()
    slack = SpySender()

    manager = NotificationManager([email, sms, slack])
    manager.notify(user, notification)

    assert email.sent == [(user, notification)]
    assert sms.sent == [(user, notification)]
    assert slack.sent == [(user, notification)]


def test_user_service_depends_on_notification_manager() -> None:
    user = User(
        id="user-1",
        email="jatin@example.com",
        phone_number="+910000000000",
        slack_id="U123",
    )
    sender = SpySender()
    service = UserService(NotificationManager([sender]))

    service.welcome_user(user)

    assert len(sender.sent) == 1
    sent_user, notification = sender.sent[0]
    assert sent_user == user
    assert notification.subject == "Welcome"
    assert "user-1" in notification.message

