import json
import sys
import os
import csv
import requests
import django
import csv
from django.conf import settings
from zap_apps.zap_catalogue.models import *
from zap_apps.marketing.models import CampaignProducts
from zap_apps.zap_catalogue.product_serializer import *
from zap_apps.zapuser.models import ZapExclusiveUserData
import urllib2
import re
from datetime import datetime


class ElasticFilters:

    search_score = 0.5

    def __init__(self):
        pass

    # Get all the filters applied on the
    # Product listing page
    @staticmethod
    def get_applied_filters(self, filters, page, size):

        product_category = brand = size = condition = age = style = color = occasion = []
        discount = 0
        price = [0, 10000000]
        shop = ['1', '2', '3']
        # product_category = ['17', '24']
        # brand = ['162', '256']
        # size = ['XS', 'S', '5', '7']
        # price = [0, 100000]
        # discount = 12
        # condition = ['0', '1', '2']
        # age = ['1', '2', '3']
        # style = ['1', '2', '3']
        # color = ['13', '14', '15', '16']
        # occasion = ['9', '5', '8']

        page = 1

        filters = {
            "page": page,
            "shop": shop,
            "product_category": product_category,
            "brand": brand,
            "size": size,
            "price": price,
            "discount": discount,
            "condition": condition,
            "age": age,
            "style": style,
            "color": color,
            "occasion": occasion
        }

        return filters

    @staticmethod
    def return_shop_request(self, filters):
        # shops = self.get_applied_filters(self, filters={}, page=1)['shop']
        shops = filters['shop']
        query = ''
        i = 1
        size = len(shops)
        for shop in shops:
            if shop.isdigit():
                query += '{"match": {"shop_id": "' + shop +'"}}'
            else:
                query += '{"match": {"shop": "' + shop + '"}}'
            i += 1

            if i <= size:
                query += ','

        body = '{' \
                   + '"bool": {' \
                        + '"should": [' \
                            + query\
                        + ']' \
                    + '}' \
                + '}'

        return body

    @staticmethod
    def return_product_category_request(self, filters):
        # product_categories = self.get_applied_filters(self, filters={}, page=1)['product_category']
        product_categories = filters['product_category']
        query = ''
        i = 1
        size = len(product_categories)
        for product_category in product_categories:
            if str(product_category).isdigit():
                query += '{"match": {"product_category_id": "'+ str(product_category) +'"}}'
            else:
                query += '{"match": {"product_category_slug": "' + str(product_category) + '"}}'
            i += 1

            if i <= size:
                query += ','

        body = '{' \
                    + '"bool": {' \
                        + '"should": [' \
                            + query \
                        + ']' \
                    + '}' \
               + '}'

        return body

    @staticmethod
    def return_product_parent_category_request(self, filters):
        # product_categories = self.get_applied_filters(self, filters={}, page=1)['product_category']
        product_categories = filters['product_parent_category']
        query = ''
        i = 1
        size = len(product_categories)
        for product_category in product_categories:
            if str(product_category).isdigit():
                query += '{"match": {"product_parent_category_id": "'+ str(product_category) +'"}}'
            else:
                query += '{"match": {"product_parent_category_slug": "' + str(product_category) + '"}}'
            i += 1

            if i <= size:
                query += ','

        body = '{' \
                    + '"bool": {' \
                        + '"should": [' \
                            + query \
                        + ']' \
                    + '}' \
               + '}'

        return body

    @staticmethod
    def return_brand_request(self, filters):
        # brands = self.get_applied_filters(self, filters={}, page=1)['brand']
        brands = filters['brand']
        query = ''
        i = 1
        size = len(brands)
        for brand in brands:
            if str(brand).isdigit():
                query += '{"match": {"brand_id": "'+ str(brand) +'"}}'
            else:
                query += '{"match": {"brand_slug": "' + str(brand) + '"}}'
            i += 1

            if i <= size:
                query += ','

        body = '{' \
                   + '"bool": {' \
                        + '"should": [' \
                            + query\
                        + ']' \
                    + '}' \
                + '}'

        return body

    @staticmethod
    def return_condition_request(self, filters):
        # conditions = self.get_applied_filters(self, filters={}, page=1)['condition']
        conditions = filters['condition']
        query = ''
        i = 1
        size = len(conditions)
        for condition in conditions:
            query += '{"match": {"condition_id": "'+ str(condition) +'"}}'
            i += 1

            if i <= size:
                query += ','

        body = '{' \
                   + '"bool": {' \
                        + '"should": [' \
                            + query\
                        + ']' \
                    + '}' \
                + '}'

        return body

    @staticmethod
    def return_age_request(self, filters):
        # ages = self.get_applied_filters(self, filters={}, page=1)['age']
        ages = filters['age']
        query = ''
        i = 1
        size = len(ages)
        for age in ages:
            query += '{"match": {"age_id": "'+ str(age) +'"}}'
            i += 1

            if i <= size:
                query += ','

        body = '{' \
                   + '"bool": {' \
                        + '"should": [' \
                            + query\
                        + ']' \
                    + '}' \
                + '}'

        return body

    @staticmethod
    def return_style_request(self, filters):
        # styles = self.get_applied_filters(self, filters={}, page=1)['style']
        styles = filters['style']
        query = ''
        i = 1
        size = len(styles)
        for style in styles:
            if str(style).isdigit():
                query += '{"match": {"style_id": "'+ str(style) +'"}}'
            else:
                query += '{"match": {"style_slug": "' + str(style) + '"}}'
            i += 1

            if i <= size:
                query += ','

        body = '{' \
                   + '"bool": {' \
                        + '"should": [' \
                            + query\
                        + ']' \
                    + '}' \
                + '}'

        return body

    @staticmethod
    def return_color_request(self, filters):
        # colors = self.get_applied_filters(self, filters={}, page=1)['color']
        colors = filters['color']
        query = ''
        i = 1
        size = len(colors)
        for color in colors:
            if str(color).isdigit():
                query += '{"match": {"color_id": "'+ str(color) + '"}}'
            else:
                query += '{"match": {"color": "' + str(color) + '"}}'
            i += 1

            if i <= size:
                query += ','

        body = '{' \
                   + '"bool": {' \
                        + '"should": [' \
                            + query\
                        + ']' \
                    + '}' \
                + '}'

        return body

    @staticmethod
    def return_occasion_request(self, filters):
        # occasions = self.get_applied_filters(self, filters={}, page=1)['occasion']
        occasions = filters['occasion']
        query = ''
        i = 1
        size = len(occasions)
        for occasion in occasions:
            if str(occasion).isdigit():
                query += '{"match": {"occasion_id": "'+ str(occasion) +'"}}'
            else:
                query += '{"match": {"occasion_slug": "' + str(occasion) + '"}}'
            i += 1

            if i <= size:
                query += ','

        body = '{' \
                   + '"bool": {' \
                        + '"should": [' \
                            + query\
                        + ']' \
                    + '}' \
                + '}'

        return body

    @staticmethod
    def return_size_request(self, filters):
        # sizes = self.get_applied_filters(self, filters={}, page=1)['size']
        sizes = filters['size']
        query = ''
        i = 1
        size = len(sizes)
        for s in sizes:
            query += '{"match": {"size.size": "'+ str(s) +'"}}'
            i += 1

            if i <= size:
                query += ','

        body = '{' \
                   + '"bool": {' \
                        + '"should": [' \
                            + query\
                        + ']' \
                    + '}' \
                + '}'

        return body

    @staticmethod
    def return_status_request(self):
        return '{"match": {"status": "1"}}'

    @staticmethod
    def return_discount_request(self, filters):
        # discount = self.get_applied_filters(self, filters={}, page=1)['discount']
        discount = filters['discount']
        if discount == 1:
            discount = 70
        elif discount == 2:
            discount = 50
        elif discount == 3:
            discount = 30
        elif discount == 4:
            discount = 10
        else:
            discount = 0
        query = '{"range": {"discount": {"from": ' + str(discount) + ', "to": 100}}}'

        return query

    @staticmethod
    def return_sort_request(self, filters):
        sort = filters['sort']
        print "sort is " + str(sort)
        if sort == 1:
            query = '"sort": {"listing_price": "desc"}'
        elif sort == 2:
            query = '"sort": {"listing_price": "asc"}'
        elif sort == 4:
            query = '"sort": {"discount": "desc"}'
        elif sort == 3:
            query = '"sort": {"loves": "desc"}'
        else:
            query = '"sort": {"upload_time": "desc"}'

        return query

    @staticmethod
    def return_price_request(self, filters):
        # prices = self.get_applied_filters(self, filters={}, page=1)['price']
        prices = filters['price']
        query = '{"range": {"listing_price": {"from": ' + str(prices[0]) + ', "to": ' + str(prices[1]) + '}}}'

        return query

    @staticmethod
    def return_product_id_request(self, filters):
        if filters['id']:
            product_ids = str(filters['id']).replace("'", "\"")
            query = '{"terms": {"id": ' + product_ids + '}}'
        else:
            query = '{}'

        return query

    @staticmethod
    def return_search_request(self, filters):

        query = filters['search']
        search_query = ''.join(query).split(' ')
        print search_query
        search_phrase = ''
        query_builder = ''

        try:
            search_query.remove('color')
        except Exception:
            pass

        for phrase in search_query:
            search_phrase += phrase
            search_phrase += ' '
            print phrase

            query_builder += '{ "match": { "brand":  "' + phrase + '" }},'
            query_builder += '{ "match": { "style":  "' + phrase + '" }},'
            query_builder += '{ "match": { "color":  "' + phrase + '" }},'
            query_builder += '{ "match": { "product_category_slug":  "' + phrase + '" }},'
            query_builder += '{ "match": { "product_parent_category_slug":  "' + phrase + '" }},'

        if len(filters['search']) > 0:
            self.search_score = 2.0
            query_builder += '{ "match": { "title":  "' + search_phrase + '" }},' \
                '{ "match": { "description": "' + search_phrase + '" }}'

            query_builder = '{"multi_match": {' + \
                '"query": "' + search_phrase + '",' + \
                '"fields": ["title", "description", "brand", "product_category", "product_parent_category", "style",' \
                '"brand_slug", "product_category_slug", "product_parent_category_slug", "style",' \
                '"color"],' + \
                '"type": "cross_fields",' + \
                '"operator": "and"' + \
                '}}'

            return '"should": [ ' + query_builder + ']'
        else:
            return '"should": []'

    @staticmethod
    def return_product_properties(self):

        return '"aggs" : { "color" : { "terms" : { "field" : "color_id" } }, "product_category" : ' \
               '{ "terms" : { "field" : "product_category_id" } }, "brand" : ' \
               '{ "terms" : { "field" : "brand_id" } }, "condition" : { "terms" : { "field" : "condition_id" } }, ' \
               '"age" : { "terms" : { "field" : "age_id" } }, "style" : { "terms" : { "field" : "style_id" } }, ' \
               '"occasion" : { "terms" : { "field" : "occasion_id" } }, "discount" : ' \
               '{ "terms" : { "field" : "discount" } }, "price" : { "terms" : { "field" : "listing_price" } }, "shop" : { "terms" : { "field" : "shop_id" } }, ' \
               '"size" : { "terms" : { "field" : "size.id" } } }'

    @staticmethod
    def return_request_skeleton(self, filters, size, page, score):

        body = '{' + self.return_product_properties(self) + ',' \
                + '"min_score": ' + str(score) + ',' \
                + '"size": ' + str(size) + ',' \
                + '"from": ' + str(page) + ',' \
                + self.return_sort_request(self, filters) + ',' \
                + '"_source": {' \
                + '"includes": ["id", "listing_price"]},' \
                + '"query":{' \
                +       '"bool": {' \
                +           self.return_search_request(self, filters) + ','\
                +           '"must": [' \
                +                  self.return_status_request(self) + ','\
                +                  self.return_product_id_request(self, filters) + ','\
                +                  self.return_shop_request(self, filters) + ','\
                +                  self.return_product_category_request(self, filters) + ',' \
                +                  self.return_product_parent_category_request(self, filters) + ',' \
                +                  self.return_brand_request(self, filters) + ',' \
                +                  self.return_condition_request(self, filters) + ',' \
                +                  self.return_style_request(self, filters) + ',' \
                +                  self.return_occasion_request(self, filters) + ',' \
                +                  self.return_age_request(self, filters) + ',' \
                +                  self.return_color_request(self, filters) + ',' \
                +                  self.return_size_request(self, filters) + ',' \
                +                  self.return_discount_request(self, filters) + ',' \
                +                  self.return_price_request(self, filters) \
                +           ']' \
                +        '}' \
                +  '}' \
                + '}'

        print body
        return body

    @staticmethod
    def get_elastic_input(self, dict, filters=None):
        SHOP_TYPES = {
            'brand-new': ['designer', 'brand'],
            'pre-loved': ['curated', 'market']
        }
        if not filters:
            filters = {
                "page": [],
                "shop": [],
                "product_category": [],
                "product_parent_category": [],
                "brand": [],
                "size": [],
                "price": [0, 10000000],
                "discount": 0,
                "condition": [],
                "age": [],
                "style": [],
                "color": [],
                "occasion": [],
                "search": '',
                "sort": 0,
                "id": [],
                'score': 0.5
            }
        for key in dict:
            if key == 'disc':
                filters['discount'] = min(dict[key])
            elif key == 'sort':
                filters['sort'] = dict[key][0]
            elif key == 'search':
                filters['search'] = dict[key]
            elif key == 'initial_filters':
                self.get_elastic_input(self, dict[key], filters)
            elif key == 'shop':
                for shop_value in dict[key]:
                    if shop_value == 'pre-loved' or shop_value == 'brand-new':
                        filters['shop'].extend(SHOP_TYPES[shop_value])
                    else:
                        filters['shop'].extend([shop_value])
            elif key == 'price':
                dict_prices = dict[key]
                print dict_prices[0]
                print dict_prices[1]
                prices = [0, 1000000000]
                if str(dict_prices[0]) == '':
                    prices[0] = 0
                else:
                    prices[0] = dict_prices[0]

                if str(dict_prices[1]) == '':
                    prices[1] = 100000000
                else:
                    prices[1] = dict_prices[1]

                filters['price'] = prices
                print "prices"
                print filters['price']
            elif key == 'category':
                filters['product_parent_category'].extend(dict[key])
            elif key == 'campaign':
                campaigns = dict[key]
                campaign_products = CampaignProducts.objects.filter(campaign__in=campaigns).all().values_list(
                    'products', flat=True).distinct()
                campaign_products = list(map(str, campaign_products))
                filters['id'].extend(campaign_products)
            elif key == 'product_collection':
                collections = dict[key]
                products = ProductCollection.objects.filter(campaign__in=campaigns).all().values_list(
                    'products', flat=True).distinct()
                campaign_products = list(map(str, campaign_products))
                filters['id'].extend(campaign_products)
            else:
                try:
                    filters[key].extend(dict[key])
                except:
                    pass

        if filters['search']:
            filters['score'] = 2.0
        elif len(filters['id']) > 0:
            filters['score'] = 0.0

        return filters

    @staticmethod
    def call_endpoint(self, filters, size, page, score, end):
        index = settings.ELASTIC_INDEX_NAME
        search_url = 'https://search-zapylesearch-oh745tarex4gbmbmndo7ek6inq.us-west-1.es.amazonaws.com/' + index + 'all_products/_search'
        request_body = self.return_request_skeleton(self, filters, size, page, score)
        r = {}
        r['result'] = requests.request(method='get', url=search_url, data=request_body)
        r['end'] = end

        return r

    @staticmethod
    def return_filtered_products(self, dict, size, page, is_filter=False, filter=None):

        filters = self.get_elastic_input(self, dict)

        print filters
        r = self.call_endpoint(self, filters, size, page, filters['score'], end=None)['result']

        # print r.text

        time = r.elapsed.total_seconds()
        print "time taken"
        print time

        data = json.loads(r.text)

        product_ids = []
        occasion = []
        condition = []
        color = []
        size = []
        price = []
        discount = []
        style = []
        brand = []
        product_category = []
        age = []
        shop = []

        total_hits = data['hits']['total']

        if total_hits > 0:
            hits = data['hits']['hits']

            for hit in hits:
                product_ids.append(int(hit['_source']['id']))
                price.append(int(hit['_source']['listing_price']))

            price = sorted(price)

            filters = data['aggregations']

            for bucket in filters['occasion']['buckets']:
                occasion.append(int(bucket['key']))

            for bucket in filters['shop']['buckets']:
                shop.append(int(bucket['key']))

            for bucket in filters['condition']['buckets']:
                condition.append(int(bucket['key']))

            for bucket in filters['color']['buckets']:
                color.append(int(bucket['key']))

            for bucket in filters['size']['buckets']:
                size.append(bucket['key'])

            # for bucket in filters['price']['buckets']:
            #     price.append(int(bucket['key']))

            for bucket in filters['discount']['buckets']:
                discount.append(int(bucket['key']))

            for bucket in filters['style']['buckets']:
                style.append(int(bucket['key']))

            for bucket in filters['brand']['buckets']:
                brand.append(int(bucket['key']))

            for bucket in filters['product_category']['buckets']:
                product_category.append(int(bucket['key']))

            for bucket in filters['age']['buckets']:
                age.append(int(bucket['key']))

            result = {}

            if is_filter is False:
                result["products"] = product_ids
                result["total_hits"] = total_hits
                print result
                return result
            elif is_filter and filter == "all":
                result["occasion"] = occasion
                result["condition"] = condition
                result["color"] = color
                result["age"] = age
                result["size"] = size
                result["price"] = price
                result["discount"] = discount
                result["style"] = style
                result["brand"] = brand
                result["shop"] = shop
                result["product_category"] = product_category
                print result
                return result
            elif is_filter and filter is not "all":
                if filter == "occasion":
                    return_filter = occasion
                elif filter == "condition":
                    return_filter = condition
                elif filter == "color":
                    return_filter = color
                elif filter == "age":
                    return_filter = age
                elif filter == "size":
                    return_filter = size
                elif filter == "price":
                    return_filter = price
                elif filter == "discount":
                    return_filter = discount
                elif filter == "style":
                    return_filter = style
                elif filter == "brand":
                    return_filter = brand
                elif filter == "product_category":
                    return_filter = product_category
                elif filter == "shop":
                    return_filter = shop
                else:
                    return_filter = []

                result[filter] = return_filter

                return result
            else:
                return result
        else:
            result = {}
            result["products"] = product_ids
            result["total_hits"] = total_hits
            result["occasion"] = occasion
            result["condition"] = condition
            result["color"] = color
            result["age"] = age
            result["size"] = size
            result["price"] = price
            result["discount"] = discount
            result["style"] = style
            result["brand"] = brand
            result["shop"] = shop
            result["product_category"] = product_category

            print result

            return result
