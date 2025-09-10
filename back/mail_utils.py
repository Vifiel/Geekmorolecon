import traceback
import os
from flask_mail import Message, Mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app_config import app

mail = Mail()

# Token Serializer
s = URLSafeTimedSerializer(app.config["SECRET_KEY"])

def generate_token(email):
    """Generate a time-limited token for email verification."""
    return s.dumps(email, salt="email-confirm")

def confirm_token(token, expiration=3600):
    """Validate the token and extract the email if valid."""
    try:
        return s.loads(token, salt="email-confirm", max_age=expiration)
    except SignatureExpired:
        return False  # Token expired
    except BadSignature:
        return False  # Token is invalid

def send_verification_email(to, verify_code):
    """Send the verification email with a secure link."""
    msg = Message(
        subject="Verify Your Account",
        recipients=[to],
        sender=app.config["MAIL_USERNAME"],
        html=f"""
        <h1>Код подтверждения {verify_code}<h1>
        <p>Отвечать на это сообщение не нужно</p>
        """
    )
    mail.send(msg)
    print("Месседж послан")

    return True
