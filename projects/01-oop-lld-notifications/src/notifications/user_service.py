from notifications.manager import NotificationManager
from notifications.models import Notification, User


class UserService:
    def __init__(self, notification_manager: NotificationManager) -> None:
        self._notification_manager = notification_manager

    def welcome_user(self, user: User) -> None:
        notification = Notification(
            subject="Welcome",
            message=f"Welcome, user {user.id}!",
        )
        self._notification_manager.notify(user, notification)

