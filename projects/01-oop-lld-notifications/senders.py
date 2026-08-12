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
