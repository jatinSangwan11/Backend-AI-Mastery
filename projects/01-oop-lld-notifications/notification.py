from dataclasses import dataclass
from typing import Protocol


@dataclass
class User:
    email: str
    phone_no: str
    device_token: str

MARKETING_SENDER_EMAIL = "marketing@ourapp.com"
SUPPORT_SENDER_EMAIL = "support@ourapp.com"
SECURITY_SENDER_EMAIL = "security@ourapp.com"

SENDGRID_PROVIDER = "SendGrid"
MAILGUN_PROVIDER = "Mailgun"
AWS_SES_PROVIDER = "AWS SES"

TWILIO_PROVIDER = "Twilio"
AWS_SNS_PROVIDER = "AWS SNS"

FCM_PROVIDER = "Firebase Cloud Messaging"


class EmailSender:
    def __init__(self, sender_email: str, provider_name: str) -> None:
        self.sender_email = sender_email
        self.provider_name = provider_name

    def send(self, user_email: str, subject: str, message: str) -> None:
        print(f"Sending email using {self.provider_name}")
        print(f"Sending email from {self.sender_email} to {user_email}")
        print(f"Subject: {subject}")
        print(f"Message: {message}")


class SmsSender:
    def __init__(self, provider_name: str) -> None:
        self.provider_name = provider_name

    def validate_phone_no(self, phone_no: str) -> None:
        if len(phone_no) != 10:
            raise Exception("Phone number should have a length of 10")

        print(phone_no.isdigit())

        if phone_no.isdigit() == False:
            raise Exception("This is a invalid phone number")

    def send(self, phone_no: str, message: str) -> None:
        self.validate_phone_no(phone_no)
        print(f"Sending SMS using {self.provider_name}")
        print(f"Sending SMS to {phone_no}")
        print(message)


class PushSender: 

    def __init__(self, provider_name: str) -> None:
        self.provider_name = provider_name
        
    
    def send(self, device_token: str, title: str, message: str) -> None:
        print(f"Sending push using {self.provider_name}")
        print(f"Sending push to {device_token}")
        print(f"Title: {title}")
        print(f"Message: {message}")

class SecurityAlertChannel(Protocol):
    def notify(self, user: User) -> None:
        ...

class SecurityEmailAlertChannel:
    def __init__(self, email_sender: EmailSender) -> None:
        self.email_sender = email_sender

    def notify(self, user: User) -> None:
        self.email_sender.send(
            user.email,
            "Security Alert",
            "New login detected on your account",
        )


class SecuritySmsAlertChannel:
    def __init__(self, sms_sender: SmsSender) -> None:
        self.sms_sender = sms_sender

    def notify(self, user: User) -> None:
        self.sms_sender.send(user.phone_no, "Security Alert: New login detected on your account")


class SecurityPushAlertChannel:
    def __init__(self, push_sender: PushSender) -> None:
        self.push_sender = push_sender

    def notify(self, user: User) -> None:
        self.push_sender.send(
            user.device_token,
            "Security Alert",
            "New login detected on your account",
        )


otp_sms_sender = SmsSender(TWILIO_PROVIDER)
security_sms_sender = SmsSender(AWS_SNS_PROVIDER)

marketing_email_sender = EmailSender(MARKETING_SENDER_EMAIL, SENDGRID_PROVIDER)
support_email_sender = EmailSender(SUPPORT_SENDER_EMAIL, MAILGUN_PROVIDER)
security_email_sender = EmailSender(SECURITY_SENDER_EMAIL, AWS_SES_PROVIDER)

security_push_sender = PushSender(FCM_PROVIDER)

security_alert_channels: list[SecurityAlertChannel] = [
    SecurityEmailAlertChannel(security_email_sender),
    SecuritySmsAlertChannel(security_sms_sender),
    SecurityPushAlertChannel(security_push_sender),
]

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


def send_security_alert(user: User) -> None:
    for channel in security_alert_channels:
        notify = getattr(channel, "notify", None)
        if not callable(notify):
            raise TypeError("Invalid security alert channel")
        notify(user)


if __name__ == "__main__":

    user = User("jatin@example.com", "8173828382", "device-token-123")
    send_security_alert(user)

# means
# If this file is being run directly, execute this block.
# If this file is being imported, skip this block.
