import json
import sys
import os
import csv
import requests
import django
import csv
from django.conf import settings
from zap_apps.zap_catalogue.models import *
from zap_apps.zap_catalogue.product_serializer import *
from zap_apps.zapuser.models import ZapExclusiveUserData
import urllib2
import re
from datetime import datetime


class ElasticSearch:

    def __init__(self):
        # Dev URL
        # self.SEARCH_URL = "https://search-devsearch-okxysl56e2vrdee27xerahxnca.us-west-1.es.amazonaws.com/"
        # Prod URL
        self.SEARCH_URL = "https://search-zapylesearch-oh745tarex4gbmbmndo7ek6inq.us-west-1.es.amazonaws.com/"
        self.PRODUCT_INDEX = settings.ELASTIC_INDEX_NAME
        self.DESIGNER_DOCUMENT = "designer/"
        self.CURATED_DOCUMENT = "curated/"
        self.MARKET_DOCUMENT = "market/"
        self.BRAND_DOCUMENT = "brands/"
        self.SUBCATEGORY_DOCUMENT = "subcategories/"
        self.CATEGORY_DOCUMENT = "categories/"
        self.USERS_DOCUMENT = "users/"

    @staticmethod
    def is_product_indexed(self, product_id):

        query = '{"query":{"match":{"id": "'+str(product_id)+'"}}}'

        search_url = 'https://search-zapylesearch-oh745tarex4gbmbmndo7ek6inq.us-west-1.es.amazonaws.com/' + self.PRODUCT_INDEX + 'all_products/_search'

        r = requests.request(method='get', url=search_url, data=query)

        response = json.loads(r.text)

        if response['hits']['total'] > 0:
            return True
        else:
            return False

    @staticmethod
    def get_index(self, product_id):

        query = '{"query":{"match":{"id": "' + str(product_id) + '"}}}'

        search_url = 'https://search-zapylesearch-oh745tarex4gbmbmndo7ek6inq.us-west-1.es.amazonaws.com/' + self.PRODUCT_INDEX + 'all_products/_search'

        r = requests.request(method='get', url=search_url, data=query)

        response = json.loads(r.text)

        if response['hits']['total'] > 0:
            return response['hits']['hits'][0]['_id']
        else:
            return 0

    """
    Indexes all the products and updates the index of the products
    already indexed
    """
    @staticmethod
    def index_all_products(self):
        products = ApprovedProduct.ap_objects.all()
        final_url = self.SEARCH_URL + self.PRODUCT_INDEX + 'all_products/'
        requests.post(final_url, data='{"hello": "world"}')
        for product in products:
            try:
                print product.id

                serializer = ProductIndexSerializer(product)
                post_data = dict(serializer.data)

                final_url = self.SEARCH_URL + self.PRODUCT_INDEX + 'all_products/' + str(product.id)
                r = requests.put(final_url, data=json.dumps(post_data))
                print "New Index Created"
                print r.status_code
                print r.text

                response = json.loads(r.text)

                if r.status_code == 201 or r.status_code == 200:
                    if self.is_product_indexed(self, product.id):
                        product.elastic_index = response["_id"]
                        product.save()
                    else:
                        self.add_index(self, product.id)
                else:
                    self.add_index(self, product.id)

                    # if not product.elastic_index:
                    #     # Create a new index
                    #     r = requests.put(final_url, data=json.dumps(post_data))
                    #     print "New Index Created"
                    #     print r.status_code
                    #     print r.text
                    #
                    #     response = json.loads(r.text)
                    #
                    #     if r.status_code == 201:
                    #         product.elastic_index = response["_id"]
                    #         product.save()
                    # else:
                    #     # Update existing index
                    #     final_url = final_url + product.elastic_index + "/"
                    #     r = requests.put(final_url, data=json.dumps(post_data))
                    #     print "Existing Index updated"
                    #     print r.status_code
                    #     print r.text

            except ApprovedProduct.DoesNotExist:
                break

    """
    Add a new index when product is created
    """
    @staticmethod
    def add_index(self, product_id):
        try:
            product = ApprovedProduct.objects.get(pk=product_id)

            # if product.user.user_type.name == "designer":
            #     add_url = self.SEARCH_URL + self.PRODUCT_INDEX + self.DESIGNER_DOCUMENT
            # elif product.user.user_type.name == "zap_exclusive":
            #     add_url = self.SEARCH_URL + self.PRODUCT_INDEX + self.CURATED_DOCUMENT
            # else:
            #     add_url = self.SEARCH_URL + self.PRODUCT_INDEX + self.MARKET_DOCUMENT

            add_url = self.SEARCH_URL + self.PRODUCT_INDEX + 'all_products/' + str(product.id)

            serializer = ProductIndexSerializer(product)

            post_data = dict(serializer.data)

            r = requests.put(add_url, data=json.dumps(post_data))
            print "New Index Created"
            print r.status_code
            print r.text

            response = json.loads(r.text)

            if r.status_code == 201 or r.status_code == 200:
                if self.is_product_indexed(self, product.id):
                    product.elastic_index = response["_id"]
                    product.save()
                else:
                    self.add_index(self, product_id)
            else:
                self.add_index(self, product_id)

        except ApprovedProduct.DoesNotExist:
            print "Product Does Not Exist with product id " + str(product.id)

    """
    Update the index when the product is updated
    """
    @staticmethod
    def update_index(self, product_id):
        # import pdb
        # pdb.set_trace()
        try:
            product = ApprovedProduct.objects.get(pk=product_id)

            elastic_index = product.elastic_index
            # if product.user.user_type.name == "designer":
            #     update_url = self.SEARCH_URL + self.PRODUCT_INDEX + self.DESIGNER_DOCUMENT
            # elif product.user.user_type.name == "zap_exclusive":
            #     update_url = self.SEARCH_URL + self.PRODUCT_INDEX + self.CURATED_DOCUMENT
            # else:
            #     update_url = self.SEARCH_URL + self.PRODUCT_INDEX + self.MARKET_DOCUMENT

            update_url = self.SEARCH_URL + self.PRODUCT_INDEX + 'all_products/'

            serializer = ProductIndexSerializer(product)
            post_data = dict(serializer.data)

            update_url = update_url + str(elastic_index)
            r = requests.put(update_url, data=json.dumps(post_data))
            print "Existing Index updated"
            print r.status_code
            print r.text

            response = json.loads(r.text)

            if r.status_code == 201 or r.status_code == 200:
                if self.is_product_indexed(self, product.id):
                    pass
                else:
                    self.add_index(self, product_id)
            else:
                self.add_index(self, product_id)

        except ApprovedProduct.DoesNotExist:
            print "Product Does Not Exist with product id " + str(product.id)


    """
    Delete all indexes
    """
    @staticmethod
    def delete_all_index(self):
        try:
            products = ApprovedProduct.objects.all()

            products_count = products.count()
            total_loops = products_count / 10
            current_loop = 1

            while current_loop <= total_loops:

                for product in products:
                    elastic_index = product.elastic_index
                    serializer = ProductIndexSerializer(product)
                    post_data = dict(serializer.data)

                    update_url = self.SEARCH_URL + self.PRODUCT_INDEX + 'all_products/'

                    if elastic_index:
                        update_url = update_url + elastic_index + "/"
                        product.elastic_index = None
                        product.save()
                        r = requests.delete(update_url, data=json.dumps(post_data))
                        print "Existing Index Deleted"
                        print r.status_code
                        print r.text

                        product._id = None
                        product.save()
                    else:
                        print 'No index exists for this product'
                        pass

                current_loop += 1

        except Exception as e:
            print e


    """
    Delete the index when the product has been deleted
    """
    @staticmethod
    def delete_index(self, product_id):
        try:
            product = ApprovedProduct.objects.get(pk=product_id)

            elastic_index = product.elastic_index
            # if product.user.user_type.name == "designer":
            #     update_url = self.SEARCH_URL + self.PRODUCT_INDEX + self.DESIGNER_DOCUMENT
            # elif product.user.user_type.name == "zap_exclusive":
            #     update_url = self.SEARCH_URL + self.PRODUCT_INDEX + self.CURATED_DOCUMENT
            # else:
            #     update_url = self.SEARCH_URL + self.PRODUCT_INDEX + self.MARKET_DOCUMENT

            update_url = self.SEARCH_URL + self.PRODUCT_INDEX + 'all_products/'

            serializer = ProductIndexSerializer(product)
            post_data = dict(serializer.data)

            update_url = update_url + str(elastic_index) + "/"
            product.elastic_index = None
            product.save()
            r = requests.delete(update_url, data=json.dumps(post_data))
            print "Existing Index Deleted"
            print r.status_code
            print r.text
        except ApprovedProduct.DoesNotExist:
            print "Product Does Not Exist with product id " + str(product_id)

    """
    Index Brands with products
    """
    @staticmethod
    def index_all_brands(self):
        try:
            brands = Brand.objects.all()
            for brand in brands:
                products_count = ApprovedProduct.objects.filter(brand=brand.id).count()
                brand_data = {
                    "id": brand.id,
                    "name": brand.brand,
                    "is_designer_brand": brand.designer_brand,
                    "logo": brand.logo.url if brand.logo else None,
                    "clearbit_logo": brand.clearbit_logo if brand.clearbit_logo else None,
                    "meta_description": brand.meta_description if brand.meta_description else None,
                    "web_cover": brand.web_cover.url if brand.web_cover else None,
                    "mobile_cover": brand.mobile_cover.url if brand.mobile_cover else None,
                    "products_count": products_count
                }

                add_url = self.SEARCH_URL + self.PRODUCT_INDEX + self.BRAND_DOCUMENT

                r = requests.post(add_url, data=json.dumps(brand_data))
                print "Brand Index Added"
                print r.status_code
                print r.text

        except Brand.DoesNotExist:
            print "No brand exists"

    """
    Index Sub Categories with products
    """
    @staticmethod
    def index_all_subcategories(self):
        try:
            sub_cats = SubCategory.objects.all()
            for sub_cat in sub_cats:
                products_count = ApprovedProduct.objects.filter(product_category=sub_cat.id).count()
                sub_cat_data = {
                    "id": sub_cat.id,
                    "name": sub_cat.name,
                    "parent": sub_cat.parent.name,
                    "category_type": sub_cat.category_type if sub_cat.category_type else None,
                    "meta_description": sub_cat.meta_description if sub_cat.meta_description else None,
                    "web_cover": sub_cat.web_cover.url if sub_cat.web_cover else None,
                    "mobile_cover": sub_cat.mobile_cover.url if sub_cat.mobile_cover else None,
                    "products_count": products_count
                }

                add_url = self.SEARCH_URL + self.PRODUCT_INDEX + self.SUBCATEGORY_DOCUMENT

                r = requests.post(add_url, data=json.dumps(sub_cat_data))
                print "Sub Category Index Added"
                print r.status_code
                print r.text

        except SubCategory.DoesNotExist:
            print "No subcategory exists"


    """
    Index categories with products
    """
    @staticmethod
    def index_all_categories(self):
        try:
            cats = Category.objects.all()
            for cat in cats:
                products_count = ApprovedProduct.objects.filter(product_category__parent__id=cat.id).count()
                cat_data = {
                    "id": cat.id,
                    "name": cat.name,
                    "category_type": cat.category_type if cat.category_type else None,
                    "meta_description": cat.meta_description if cat.meta_description else None,
                    "web_cover": cat.web_cover.url if cat.web_cover else None,
                    "mobile_cover": cat.mobile_cover.url if cat.mobile_cover else None,
                    "products_count": products_count
                }

                add_url = self.SEARCH_URL + self.PRODUCT_INDEX + self.CATEGORY_DOCUMENT

                r = requests.post(add_url, data=json.dumps(cat_data))
                print "Sub Category Index Added"
                print r.status_code
                print r.text

        except Category.DoesNotExist:
            print "No Category exists"



