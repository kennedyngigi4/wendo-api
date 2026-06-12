from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class EmailService:

    @staticmethod
    def send_welcome_email(user):

        try:
            subject = "Welcome to Wendo Health"
            html_content = render_to_string(
                "notifications/welcome.html",
                {
                    "fullname": user.fullname,
                    "unsubscribe_url": "https://wendohealth.com",
                }
            )

            text_content = f"""
            Hi {user.fullname},

            Welcome to Wendo Health.
            """

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )

            email.attach_alternative(html_content, "text/html")

            email.send(fail_silently=False)

            print("WELCOME EMAIL SENT")

        except Exception as e:
            print("EMAIL ERROR:", str(e))



    @staticmethod
    def send_password_reset_email(user, reset_url):

        try:
            subject = "Reset Your Wendo Password"


            html_content = render_to_string(
                "notifications/reset_password.html",
                {
                    "fullname": user.fullname,
                    "reset_url": reset_url,
                    "support_email": settings.DEFAULT_FROM_EMAIL,
                }
            )

            text_content = f"""
            Hi {user.fullname},

            We received a request to reset your Wendo Health password.

            Reset your password here:
            {reset_url}

            If you did not request this password reset, please ignore this email.
            """

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )

            email.attach_alternative(html_content, "text/html")

            email.send(fail_silently=False)

            print("PASSWORD RESET EMAIL SENT")

        except Exception as e:
            print("EMAIL ERROR:", str(e))



