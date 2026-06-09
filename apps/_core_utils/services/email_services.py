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


