from notification import send_welcome_notification

# pytest automatically regonizes test_*.py / *_test.py   x

def test_send_welcome_notification_prints_email_message(capsys) -> None:
    # When I send a welcome notification to this email, the terminal output should contain the recipient, 
    # subject, and message.

    send_welcome_notification("jatin@example.com")

    output = capsys.readouterr().out # this says-- give me everything printed to stdout so far

    # checking what happened
    assert "Sending email to jatin@example.com" in output  # it is checking whether the output printed similar lines
    assert "Subject: Welcome" in output
    assert "Message: Welcome to our app!" in output
