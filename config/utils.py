from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_verification_email(user, verification_code):
    """
    Envoie un email de vérification avec le code OTP
    """
    subject = 'Code de vérification - Inscription'
    
    # Template HTML pour l'email
    html_message = render_to_string('emails/verification_email.html', {
        'user': user,
        'verification_code': verification_code,
        'expiry_minutes': getattr(settings, 'OTP_EXPIRY_TIME', 10)
    })
    
    # Version texte brut
    plain_message = strip_tags(html_message)
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")
        return False