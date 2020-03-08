import json
# import pdb
import sys, os
# sys.path.append("/path/to/project")
import django
import csv
import requests, json


os.environ["DJANGO_SETTINGS_MODULE"] = "zapyle_new.settings.prod"
django.setup()

from zap_apps.zap_catalogue.models import *
from django.conf import settings
from openpyxl import load_workbook, Workbook
from zap_apps.zap_catalogue.models import Hashtag
from zap_apps.zap_catalogue.product_serializer import *
from zap_apps.zapuser.models import ZapExclusiveUserData
import urllib2
import re

SEARCH_URL = "https://search-zapylesearch-oh745tarex4gbmbmndo7ek6inq.us-west-1.es.amazonaws.com/"
PRODUCT_INDEX = "products/"
DESIGNER_DOCUMENT = "designer/"
CURATED_DOCUMENT = "curated/"
MARKET_DOCUMENT = "market/"
USERS_DOCUMENT = "users/"

products = ApprovedProduct.objects.all()

for product in products:
    try:
        print product.id
        # this_product = ApprovedProduct.objects.get(id=product.id)
        if product.user.user_type.name == "designer":
            final_url = SEARCH_URL+PRODUCT_INDEX+DESIGNER_DOCUMENT
        elif product.user.user_type.name == "zap_exclusive":
            final_url = SEARCH_URL+PRODUCT_INDEX+CURATED_DOCUMENT
        else:
            final_url = SEARCH_URL+PRODUCT_INDEX+MARKET_DOCUMENT

        serializer = ProductIndexSerializer(product)
        post_data = dict(serializer.data)
        es = ElasticSearch()
        if not es.is_product_indexed(es, product.id):
            # Create a new index
            r = requests.post(final_url, data=json.dumps(post_data))
            print "New Index Created"
            print r.status_code
            print r.text

            response = json.loads(r.text)

            # if r.status_code == 201:
            #     product.elastic_index = response["_id"]
            #     product.save()
        else:
            # Update existing index
            elastic_index = es.get_index(es, product.id)
            final_url = final_url + elastic_index + "/"
            r = requests.put(final_url, data=json.dumps(post_data))
            print "Existing Index updated"
            print r.status_code
            print r.text

    except ApprovedProduct.DoesNotExist:
        break
