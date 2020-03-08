import json
# import pdb
import sys, os
# sys.path.append("/path/to/project")
import django
import csv


os.environ["DJANGO_SETTINGS_MODULE"] = "zapyle_new.settings.prod"
django.setup()

from zap_apps.zap_catalogue.models import *
from zap_apps.marketing.models import *
from django.conf import settings
from openpyxl import load_workbook, Workbook
from zap_apps.zap_catalogue.models import Hashtag
from zap_apps.zap_catalogue.product_serializer import ZapProductSerializer, ProductImageSerializer, NumberOfProductSrlzr
from zap_apps.zapuser.models import ZapExclusiveUserData
import urllib2
import re

# Update title and description of product ids
# with open('sheet.csv') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         print row['product_id'] + " " + row['title'] + " " + row['description']
#         product_object = ApprovedProduct.objects.get(pk=row['product_id'])
#         product_object.title = row['title']
#         if row['description'] != None or row['description'] != "":
#             product_object.description = row['description']
#
#         product_object.save()
#         print "successful update"


# Update Listing Price and original price of product id's
with open('pricing.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print row['product_id'] + " " + row['listing_price']
        product_object = ApprovedProduct.objects.get(pk=row['product_id'])
        product_object.original_price = row['listing_price']
        product_object.listing_price = row['listing_price']
        product_object.save()
        print "successful update"

# Update categories
# with open('subcat.csv') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         print row['product_id'] + " " + row['category']
#         product_object = ApprovedProduct.objects.filter(pk=row['product_id']).\
#             update(product_category=row['category'])
#         print "successful update"

# Delete Products
# with open('delete.csv') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         print row['id']
#         product_object = ApprovedProduct.objects.filter(pk=row['id']).delete()
#         print "successful delete"

# Make products Sold Out
# with open('sold_out.csv') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         print row['code']
#         product_object = NumberOfProducts.objects.get(product=row['code'])
#         product_object.quantity = 0
#         product_object.save()
#         print "Quantity made Zero"

# Update Brand URL's
# with open('brand.csv') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         print row['BRAND_ID']
#         brand_object = Brand.objects.get(pk=row['BRAND_ID'])
#         brand_object.clearbit_logo = row['BRAND_URL']
#         brand_object.save()
#         print "Clearbit URL updated"

# Flyrobe quantity edits
# with open('flyrobe_edits.csv') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         product_id = row['product_id']
#         title = row['title']
#         listing_price = row['listing_price']
#         sizes = row['size'].split(',')
#         ap = ApprovedProduct.objects.get(pk=product_id)
#         ap.title = title
#         ap.listing_price = listing_price
#         ap.save()
#         print "Listing Price and Title Updated"
#
#         for size in sizes:
#             al = NumberOfProducts(product=ApprovedProduct.objects.get(pk=product_id),
#                                   size=Size.objects.get(size=int(size)))
#             al.save()
#             print "size added"
# Add partner ID
# with open('old_products.csv') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         ap = ApprovedProduct.objects.get(pk=row['product_id'])
#         ap.partner_id = row['partner_id']
#         ap.save()
#         print "Partner ID updated"

# Campaign Update
# with open('sheet3.csv') as csvfile:
#     reader = csv.DictReader(csvfile)
#     # product_ids = []
#     #
#     # for row in reader:
#     #     product_ids.append(row['product_id'])
#     #
#     # campaign_products = CampaignProducts.objects.filter(pk__in=product_ids, campaign=20)
#
#     # for product in campaign_products:
#     #     product.original_listing_price =
#
#     for row in reader:
#         ap = ApprovedProduct.objects.get(pk=row['product_id'])
#         # product_ids.append(row['product_id'])
#         # ap.listing_price = row['listing_price']
#         # ap.original_price = row['original_price']
#         # ap.save()
#         # print "Listing Price Updated"
#
#         price = int(row['original_price'])
#         print row['discount']
#         discount = int(int(int(row['discount']) * price) / 100)
#         print price
#         print discount
#         new_price = price - discount
#         print new_price
#         ap.listing_price = new_price
#         # ap.original_price = row['original_price']
#         ap.save()
#         print "Listing Price further Updated"

    # for row in reader:
    #     ap = ApprovedProduct.objects.get(pk=row['product_id'])
    #     # product_ids.append(row['product_id'])

