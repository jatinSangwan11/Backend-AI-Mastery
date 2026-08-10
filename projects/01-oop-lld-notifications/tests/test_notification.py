import pytest

from notification import send_otp_notification, send_email_notification, send_password_reset_email, send_welcome_email

# pytest automatically regonizes test_*.py / *_test.py   x

def test_send_email_notification_prints_email_message(capsys) -> None:
    # When I send a welcome notification to this email, the terminal output should contain the recipient, 
    # subject, and message.

    send_email_notification("jatin@example.com", "Greetings", "Welcome to our app!")

    output = capsys.readouterr().out # this says-- give me everything printed to stdout so far

    # checking what happened
    assert "Sending email to jatin@example.com" in output  # it is checking whether the output printed similar lines
    assert "Subject: Greetings" in output
    assert "Message: Welcome to our app!" in output

def test_send_email_notification_for_promotional_message(capsys) -> None:
    send_email_notification("jatin@example.com", "Promotional subject", "Try the offers from Myntra.")

    output = capsys.readouterr().out

    assert "Sending email to jatin@example.com" in output
    assert "Subject: Promotional subject" in output
    assert "Message: Try the offers from Myntra." in output

def test_send_otp_notification_prints_sms_message(capsys) -> None:
    send_otp_notification("8164226707", "1234")

    output = capsys.readouterr().out

    assert "Sending SMS to 8164226707" in output
    assert "OTP: 1234" in output

def test_send_otp_notification_rejects_short_phone_number() -> None:
    with pytest.raises(Exception, match="Phone number should have a length of 10"):
        send_otp_notification("1232345", "1234")


def test_send_otp_notification_rejects_non_numeric_phone_number() -> None:
    with pytest.raises(Exception, match="This is a invalid phone number"):
        send_otp_notification("81642abc07", "1234")


def test_welcome_email(capsys) -> None:
    send_welcome_email("jatin@example.com") 

    output = capsys.readouterr().out

    assert "Sending email to jatin@example.com" in output 
    assert "Subject: Greetings" in output
    assert "Message: Welcome to our app!" in output

def test_password_reset_email(capsys) -> None:
    send_password_reset_email(
        "jatin@example.com",
        "dcaoni3u3i2bibini2n"
    )
     
    output =  capsys.readouterr().out
    
    assert "Sending email to jatin@example.com" in output
    assert "Subject: Reset your Password" in output
    assert "Message: Here is your password reset link: dcaoni3u3i2bibini2n"