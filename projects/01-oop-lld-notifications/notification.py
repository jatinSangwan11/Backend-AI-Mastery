def send_welcome_notification(user_email: str) -> None:
    subject = "Welcome"
    message = "Welcome to our app!"

    print(f"Sending email to {user_email}")
    print(f"Subject: {subject}")
    print(f"Message: {message}")
