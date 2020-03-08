from celery import task
from django.core.mail import EmailMultiAlternatives

@task
def apply_offers_task(when, product=None, user=None):
	from zap_apps.zap_catalogue.models import ApprovedProduct
	from zap_apps.zapuser.models import ZapUser
	from zap_apps.offer.views import apply_offers
	if product:
		p = ApprovedProduct.objects.get(id=product)
	else:
		p = None
	if user:
		u = ZapUser.objects.get(id=user)
	else:
		u = None
	apply_offers(when=when, product=p, user=u)

@task
def send_email_to_zapyle(note, email_phone):
	print 'sending....'
	from django.conf import settings
	from django.template.loader import render_to_string
	subject, from_email, to = 'New Message', 'hello@zapyle.com', 'shafi@zapyle.com'
	text_content = "You've got a new message."
	html = settings.NEW_MESSAGE_TEMPLATE
	html_body = render_to_string(html['html'], {'email_phone':email_phone, 'message':note})
	msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
	msg.attach_alternative(html_body, "text/html")
	msg.send()