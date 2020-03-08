from zap_apps.zap_catalogue.product_serializer import *
from django.conf import settings
from zap_apps.zap_catalogue.models import *
import json
import sys
import os
import csv
import requests
import django
import csv
import requests


class CreateDocs:

    def __init__(self):
        pass

    @staticmethod
    def trial(self):
        products = ApprovedProduct.ap_objects.all()


        file = open('zap_apps/zap_catalogue/docs/elastic_index_ops.json', 'w')

        for product in products:
            serializer = ProductIndexSerializer(product)
            doc = dict(serializer.data)
            file.write('{"index":{"_index":"test_local","_type":"all_products","_id":"1"}}\n')
            file.write(str(doc) + "\n")

    @staticmethod
    def index(self):
        url = 'https://search-zapylesearch-oh745tarex4gbmbmndo7ek6inq.us-west-1.es.amazonaws.com/_bulk'
        with open('zap_apps/zap_catalogue/docs/elastic_index_ops.json') as json_data:
            d = json.load(json_data)
            r = requests.post(url, data=d)
            print r.status_code
            print r.content








