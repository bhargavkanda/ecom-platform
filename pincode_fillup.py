import csv
import sys,os
# sys.path.append("/path/to/project")
import django
try:
    env = sys.argv[1]
except IndexError:
    raise Exception("Please provide settings [local/ staging/ prod]")

os.environ["DJANGO_SETTINGS_MODULE"] = "zapyle_new.settings.{}".format(env)
django.setup()
from django.conf import settings
from zap_apps.address.models import CityPincode
try:
    cr = csv.reader(open(settings.HOME_FOLDER+"/all_pincode.csv","rb"))
    for i in cr:
        CityPincode.objects.get_or_create(pincode=i[0],city=i[1],state=i[2])
    print 'Success'
except Exception as e:
    print str(e)
