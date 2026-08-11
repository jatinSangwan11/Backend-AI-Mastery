import pytest

from notification import EmailSender, send_otp_notification, send_password_reset_email, send_security_alert, send_welcome_email, User
from notification import AWS_SES_PROVIDER, AWS_SNS_PROVIDER, FCM_PROVIDER, MAILGUN_PROVIDER, SECURITY_SENDER_EMAIL, MARKETING_SENDER_EMAIL, SENDGRID_PROVIDER, SUPPORT_SENDER_EMAIL, TWILIO_PROVIDER

# pytest automatically regonizes test_*.py / *_test.py   x

@pytest.fixture
def user() -> User:
    return User("jatin@example.com", "8182828232", "device-token-123")


def test_email_sender_prints_email_message(capsys) -> None:
    # When I send a welcome notification to this email, the terminal output should contain the recipient, 
    # subject, and message.

    email_sender = EmailSender(MARKETING_SENDER_EMAIL, SENDGRID_PROVIDER)
    email_sender.send("jatin@example.com", "Greetings", "Welcome to our app!")

    output = capsys.readouterr().out # this says-- give me everything printed to stdout so far

    # checking what happened
    assert f"Sending email using {SENDGRID_PROVIDER}" in output
    assert f"Sending email from {MARKETING_SENDER_EMAIL} to jatin@example.com" in output  # it is checking whether the output printed similar lines
    assert "Subject: Greetings" in output
    assert "Message: Welcome to our app!" in output

def test_email_sender_for_promotional_message(capsys) -> None:
    email_sender = EmailSender(MARKETING_SENDER_EMAIL, SENDGRID_PROVIDER)
    email_sender.send("jatin@example.com", "Promotional subject", "Try the offers from Myntra.")

    output = capsys.readouterr().out

    assert f"Sending email using {SENDGRID_PROVIDER}" in output
    assert f"Sending email from {MARKETING_SENDER_EMAIL} to jatin@example.com" in output
    assert "Subject: Promotional subject" in output
    assert "Message: Try the offers from Myntra." in output

def test_send_otp_notification_prints_sms_message(user, capsys) -> None:
    
    send_otp_notification(user, "1234")

    output = capsys.readouterr().out

    assert f"Sending SMS using {TWILIO_PROVIDER}" in output
    assert "Sending SMS to 8182828232" in output
    assert "OTP: 1234" in output

def test_send_otp_notification_rejects_short_phone_number() -> None:
    user = User("jatin@example.com", "1232345", "device-token-123")

    with pytest.raises(Exception, match="Phone number should have a length of 10"):
        send_otp_notification(user, "1234")


def test_send_otp_notification_rejects_non_numeric_phone_number() -> None:
    user = User("jatin@example.com", "81642abc07", "device-token-123")

    with pytest.raises(Exception, match="This is a invalid phone number"):
        send_otp_notification(user, "1234")


def test_welcome_email(user, capsys) -> None:
    send_welcome_email(user)

    output = capsys.readouterr().out

    assert f"Sending email using {SENDGRID_PROVIDER}" in output
    assert f"Sending email from {MARKETING_SENDER_EMAIL} to jatin@example.com" in output 
    assert "Subject: Greetings" in output
    assert "Message: Welcome to our app!" in output

def test_password_reset_email(user, capsys) -> None:
    send_password_reset_email(
        user,
        "dcaoni3u3i2bibini2n"
    )
     
    output =  capsys.readouterr().out
    
    assert f"Sending email using {MAILGUN_PROVIDER}" in output
    assert f"Sending email from {SUPPORT_SENDER_EMAIL} to jatin@example.com" in output
    assert "Subject: Reset your Password" in output
    assert "Message: Here is your password reset link: dcaoni3u3i2bibini2n"


def test_security_alert_happy_case(user, capsys) -> None:
    send_security_alert(user)
    
    output = capsys.readouterr().out 

    assert f"Sending email using {AWS_SES_PROVIDER}" in output
    assert f"Sending email from {SECURITY_SENDER_EMAIL} to jatin@example.com" in output
    assert "Subject: Security Alert" in output
    assert "Message: New login detected on your account" in output
    assert f"Sending SMS using {AWS_SNS_PROVIDER}" in output
    assert "Sending SMS to 8182828232" in output
    assert "Security Alert: New login detected on your account" in output
    assert f"Sending push using {FCM_PROVIDER}" in output
    assert "Sending push to device-token-123" in output
    assert "Title: Security Alert" in output
