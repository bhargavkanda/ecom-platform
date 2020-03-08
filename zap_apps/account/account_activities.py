import hashlib
import random
from django.core.mail import send_mail
from django.template.loader import render_to_string
from zap_apps.zap_notification.views import ZapSms, ZapEmail
from django.conf import settings


def send_invitation_email(to, ctx):
    zapemail = ZapEmail()
    subject = render_to_string("account/email/invite_user_subject.txt", ctx)
    message = render_to_string("account/email/invite_user.txt", ctx)

    zapemail.send_email_attachment(subject, settings.DEFAULT_FROM_EMAIL, to,email_body=message)
    # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, to)


def send_confirmation_email(to, ctx):
    zapemail = ZapEmail()
    subject = render_to_string(
        "account/email/email_confirmation_subject.txt", ctx)
    subject = "".join(subject.splitlines())  # remove superfluous line breaks
    message = render_to_string(
        "account/email/email_confirmation_message.txt", ctx)
    zapemail.send_email_attachment(subject, settings.DEFAULT_FROM_EMAIL, to,email_body=message)
    # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, to)


def send_password_change_email(to, ctx):
    zapemail = ZapEmail()
    subject = render_to_string("email/password_change_subject.txt", ctx)
    subject = "".join(subject.splitlines())
    message = render_to_string("email/password_change.txt", ctx)
    zapemail.send_email_attachment(subject, settings.DEFAULT_FROM_EMAIL, to,email_body=message)
    # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, to)


def send_password_reset_email(to, ctx):
    zapemail = ZapEmail()
    subject = render_to_string("email/password_reset_subject.txt", ctx)
    subject = "".join(subject.splitlines())
    message = render_to_string("email/password_reset.txt", ctx)
    zapemail.send_email_attachment(subject, settings.DEFAULT_FROM_EMAIL, to,email_body=message)
    # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, to)


def generate_random_token(extra=None, hash_func=hashlib.sha256):
    if extra is None:
        extra = []
    bits = extra + [str(random.SystemRandom().getrandbits(512))]
    return hash_func("".join(bits).encode("utf-8")).hexdigest()
