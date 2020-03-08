import sys,os
# sys.path.append("/path/to/project")
import django
try:
    env = sys.argv[1]
except IndexError:
    raise Exception("Please provide settings [local/ staging/ prod]")

os.environ["DJANGO_SETTINGS_MODULE"] = "zapyle_new.settings.{}".format(env)
django.setup()


from zap_apps.offer.models import ZapCredit
from zap_apps.payment.models import ZapWallet


all_credits = ZapCredit.objects.all()
try:
	for cr in all_credits:
		ZapWallet.objects.create(user=cr.user, credit=cr.credit, amount=cr.amount, mode='0', purpose=cr.purpose)
	print 'Success'
except Exception as e:
	print e
