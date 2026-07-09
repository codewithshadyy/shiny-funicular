

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3)
def send_password_reset_email(self, user_email, user_handle, uid, token):
   
    reset_link = f"http://localhost:8000/reset-password?uid={uid}&token={token}"
  
    subject = "Reset your password"
    message = (
        f"Hi {user_handle},\n\n"
        f"Someone requested a password reset for your account. "
        f"If this was you, click the link below to set a new password:\n\n"
        f"{reset_link}\n\n"
        f"This link will expire soon and can only be used once. "
        f"If you didn't request this, you can safely ignore this email."
    )

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
    except Exception as exc:
        
        raise self.retry(exc=exc, countdown=10)