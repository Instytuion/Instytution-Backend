import random
from django.core.mail import send_mail
from django.conf import settings


def generate_otp():
    """
    Generate a random 6-digit OTP.

    Returns Randomly generated OTP.
    """
    return ''.join(random.choices('0123456789', k=6))


def send_otp_email(email, username, otp):
    subject = "Your OTP for Verification"
    message = f"Hi {username},\n\nYour OTP is: {otp}\n\nPlease use this OTP to complete your Verification process.\n\nThank you."
    sender = settings.EMAIL_HOST_USER 
    recipient_list = [email]
    send_mail(subject, message, sender, recipient_list)


def send_credentials_email (email, password, role, first_name):
        """Send email containing the user's login credentials."""

        try:
            email_subject = "Your Login Credentials"
            email_message = f"""
            Dear {first_name},

            Your account has been successfully created for {role}. Here are your login credentials:

            email: {email}
            Password: {password}

            Please log in and change your password immediately.

            Thank you!
            InstyTution 
            """

            # Sending the email (optional, based on your settings)
            send_mail(
                email_subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            print('error while senting credentials to email',e)