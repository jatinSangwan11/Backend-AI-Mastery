from dataclasses import dataclass


@dataclass
class User:
    email: str
    phone_no: str

MARKETING_SENDER_EMAIL = "marketing@ourapp.com"
SUPPORT_SENDER_EMAIL = "support@ourapp.com"
SECURITY_SENDER_EMAIL = "security@ourapp.com"

SENDGRID_PROVIDER = "SendGrid"
MAILGUN_PROVIDER = "Mailgun"
AWS_SES_PROVIDER = "AWS SES"


def send_email_notification(
    user_email: str,
    subject: str,
    message: str,
    sender_email: str,
    provider_name: str,
) -> None:
    print(f"Sending email using {provider_name}")
    print(f"Sending email from {sender_email} to {user_email}")
    print(f"Subject: {subject}")
    print(f"Message: {message}")


def send_welcome_email(user: User) -> None:
    send_email_notification(
        user.email,
        "Greetings",
        "Welcome to our app!",
        MARKETING_SENDER_EMAIL,
        SENDGRID_PROVIDER
    )


def send_password_reset_email(user: User, reset_link: str) -> None:
    message = f"""
        Here is your password reset link: {reset_link}
    """
    send_email_notification(
        user.email,
        "Reset your Password", 
        message,
        SUPPORT_SENDER_EMAIL,
        MAILGUN_PROVIDER
    )


def validate_phone_no(phone_no: str) -> None:
    if len(phone_no) != 10:
        raise Exception("Phone number should have a length of 10")

    print(phone_no.isdigit())

    if phone_no.isdigit() == False:
        raise Exception("This is a invalid phone number")


def send_sms_notification(phone_no: str, message: str) -> None:
    print(f"Sending SMS to {phone_no}")
    print(message)


def send_otp_notification(user: User, otp: str) -> None:
    validate_phone_no(user.phone_no)
    send_sms_notification(user.phone_no, f"OTP: {otp}")       


def send_security_alert(user: User) -> None:
    send_email_notification(
        user.email,
        "Security Alert",
        "New login detected on your account",
        SECURITY_SENDER_EMAIL,
        AWS_SES_PROVIDER
    )

    validate_phone_no(user.phone_no)
    send_sms_notification(user.phone_no, "Security Alert: New login detected on your account")


if __name__ == "__main__":

    user = User("jatin@example.com", "8173828382")
    send_security_alert(user)

# means
# If this file is being run directly, execute this block.
# If this file is being imported, skip this block.
