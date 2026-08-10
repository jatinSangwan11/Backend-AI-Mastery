def send_email_notification(user_email: str, subject: str, message: str) -> None:
    print(f"Sending email to {user_email}")
    print(f"Subject: {subject}")
    print(f"Message: {message}")


def send_welcome_email(user_email: str) -> None:
    send_email_notification(
        user_email,
        "Greetings",
        "Welcome to our app!"
    )


def send_password_reset_email(user_email: str, reset_link: str) -> None:
    message = f"""
        Here is your password reset link: {reset_link}
    """
    send_email_notification(
        user_email,
        "Reset your Password", 
        message
    )

def send_otp_notification(phone_no: str, otp: str) -> None:
    if len(phone_no) != 10:
        raise Exception("Phone number should have a length of 10")
    
    print(phone_no.isdigit())
    if(phone_no.isdigit() == False):
        raise Exception("This is a invalid phone number")
    print(f"Sending SMS to {phone_no}")
    print(f"OTP: {otp}")



if __name__ == "__main__":

    phone_no = "8164226707"
    send_otp_notification(phone_no, "1234")

# means
# If this file is being run directly, execute this block.
# If this file is being imported, skip this block.