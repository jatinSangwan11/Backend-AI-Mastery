from constants import (
    AWS_SES_PROVIDER,
    AWS_SNS_PROVIDER,
    EMAIL_CHANNEL,
    FCM_PROVIDER,
    MAILGUN_PROVIDER,
    MARKETING_SENDER_EMAIL,
    PUSH_CHANNEL,
    SECURITY_SENDER_EMAIL,
    SENDGRID_PROVIDER,
    SMS_CHANNEL,
    SUPPORT_SENDER_EMAIL,
    TWILIO_PROVIDER,
)
from models import User
from security_alerts import (
    SecurityAlertChannel,
    SecurityAlertNotifier,
    SecurityEmailAlertChannel,
    SecurityPushAlertChannel,
    SecuritySmsAlertChannel,
)
from senders import EmailSender, PushSender, SmsSender


otp_sms_sender = SmsSender(TWILIO_PROVIDER)
security_sms_sender = SmsSender(AWS_SNS_PROVIDER)

marketing_email_sender = EmailSender(MARKETING_SENDER_EMAIL, SENDGRID_PROVIDER)
support_email_sender = EmailSender(SUPPORT_SENDER_EMAIL, MAILGUN_PROVIDER)
security_email_sender = EmailSender(SECURITY_SENDER_EMAIL, AWS_SES_PROVIDER)

security_push_sender = PushSender(FCM_PROVIDER)

security_alert_channels: list[SecurityAlertChannel] = [
    SecurityEmailAlertChannel(security_email_sender, EMAIL_CHANNEL),
    SecuritySmsAlertChannel(security_sms_sender, SMS_CHANNEL),
    SecurityPushAlertChannel(security_push_sender, PUSH_CHANNEL),
]

security_alert_notifier = SecurityAlertNotifier(security_alert_channels)


def send_welcome_email(user: User) -> None:
    marketing_email_sender.send(
        user.email,
        "Greetings",
        "Welcome to our app!"
    )


def send_password_reset_email(user: User, reset_link: str) -> None:
    message = f"""
        Here is your password reset link: {reset_link}
    """

    support_email_sender.send(
        user.email,
        "Reset your Password",
        message
    )


def send_otp_notification(user: User, otp: str) -> None:
    otp_sms_sender.send(user.phone_no, f"OTP: {otp}")


if __name__ == "__main__":
    user = User("jatin@example.com", "8173828382", "device-token-123")
    security_alert_notifier.notify(user, [EMAIL_CHANNEL, SMS_CHANNEL, PUSH_CHANNEL])
