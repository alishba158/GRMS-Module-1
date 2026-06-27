import threading
from django.core.mail import send_mail
from django.conf import settings

def send_email_notification(user, subject, message, link=''):
    """Email bhejne ka function"""
    if not user or not user.email:
        return False
    
    full_message = message
    if link:
        full_message = f"{message}\n\n🔗 View Details: {link}\n\n---\nThis is an automated message from GRMS."
    
    try:
        send_mail(
            subject=subject,
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        print(f"✅ Email sent to {user.email}: {subject}")
        return True
    except Exception as e:
        print(f"❌ Email failed to {user.email}: {e}")
        return False

def send_email_async(user, subject, message, link=''):
    """Background mein email bhejna - page slow nahi hoga"""
    if not user or not user.email:
        return False
    
    thread = threading.Thread(
        target=send_email_notification,
        args=(user, subject, message, link)
    )
    thread.start()
    return True

def get_full_url(request, path):
    """Relative path ko full URL mein convert karo (jaise /student/synopsis/5/ ko complete URL)"""
    return request.build_absolute_uri(path)