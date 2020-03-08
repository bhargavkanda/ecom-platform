import json
# import pdb
import sys, os
# sys.path.append("/path/to/project")
import django
import csv

reload(sys)
sys.setdefaultencoding('utf-8')


os.environ["DJANGO_SETTINGS_MODULE"] = "zapyle_new.settings.prod"
django.setup()

from zap_apps.zap_catalogue.models import *
from zap_apps.zapuser.models import *
from django.conf import settings
from openpyxl import load_workbook, Workbook
from zap_apps.zap_catalogue.models import Hashtag
from zap_apps.zap_catalogue.product_serializer import ZapProductSerializer, ProductImageSerializer, NumberOfProductSrlzr
from zap_apps.zapuser.models import ZapExclusiveUserData
import urllib2
import re
from django.db.models import Sum


# Get details of all the approved products
f = open('products.csv', 'w')

products = ApprovedProduct.objects.all()

for product in products:
    available = str(product.product_count.all().aggregate(Sum('quantity'))['quantity__sum'])
    if available <= 0:
        sold_out = "True"
    else:
        sold_out = "False"

    if product.images.all():
        images = product.images.all()
        all_images = ""
        for image in images:
            all_images = all_images + str(image.image.url) + " "
    else:
        all_images = ""

    if product.size.all():
        sizes = product.size.all()
        all_sizes = ""
        for size in sizes:
            all_sizes = all_sizes + str(size.size)
    else:
        all_sizes = ""

    content = str(product.id) + "," + str(product.original_price) \
              + "," + str(product.product_category) + "," + all_images \
              + "," + all_sizes + "," + (str(product.title).replace(",", "")).replace("\n", "") \
              + "," + str(product.listing_price) + "," + str(product.color) \
              + "," + available + "," + (str(product.description).replace(",", "")).replace("\n", "") \
              + "," + str(product.brand) + "," + str(product.style) \
              + "," + str(product.discount) + "," + str(product.condition) \
              + "," + str(product.age) + "," + str(product.sale) \
              + "," + sold_out + "," + str(product.occasion)

    f.write(content)
    f.write("\n")

f.close()


# Get details of the zapexclusive user data
fo = open("zapexclusiveuserdata.csv", "w")
users = ZapExclusiveUserData.objects.all()

for u in users:

    user_products = u.products.all()

    for product in user_products:
        user_details = ""
        all_data = ""
        user_details += str(u.full_name) + "," + str(u.account_number) + "," + str(u.account_holder) + "," + str(
            u.ifsc_code) + ","

        all_data += user_details

        available = str(product.product_count.all().aggregate(Sum('quantity'))['quantity__sum'])
        if available <= 0:
            sold_out = "True"
        else:
            sold_out = "False"

        if product.images.all():
            images = product.images.all()
            all_images = ""
            for image in images:
                all_images = all_images + str(image.image.url) + " "
        else:
            all_images = ""

        if product.size.all():
            sizes = product.size.all()
            all_sizes = ""
            for size in sizes:
                all_sizes = all_sizes + str(size.size)
        else:
            all_sizes = ""

        all_data += str(product.id) + "," + str(product.original_price) \
              + "," + str(product.product_category) + "," + all_images \
              + "," + all_sizes + "," + (str(product.title).replace(",", "")).replace("\n", "") \
              + "," + str(product.listing_price) + "," + str(product.color) \
              + "," + available + "," + (str(product.description).replace(",", "")).replace("\n", "") \
              + "," + str(product.brand) + "," + str(product.style) \
              + "," + str(product.discount) + "," + str(product.condition) \
              + "," + str(product.age) + "," + str(product.sale) \
              + "," + sold_out + "," + str(product.occasion)

        fo.write(all_data)
        fo.write("\n")
fo.close()
