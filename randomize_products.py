import radar
import json
# import pdb
import sys, os
# sys.path.append("/path/to/project")
import django
import csv


os.environ["DJANGO_SETTINGS_MODULE"] = "zapyle_new.settings.prod"
django.setup()

from zap_apps.zap_catalogue.models import *
from django.conf import settings
from openpyxl import load_workbook, Workbook
from zap_apps.zap_catalogue.models import Hashtag
from zap_apps.zap_catalogue.product_serializer import ZapProductSerializer, ProductImageSerializer, NumberOfProductSrlzr
from zap_apps.zapuser.models import ZapExclusiveUserData
import urllib2
import re

product_objects = ApprovedProduct.objects.all()
for product in product_objects:
    days_passed = (timezone.now() - product.update_time).days
    product.score = product.score - days_passed
    product.save()
    print "Score updated to: "+str(product.score)