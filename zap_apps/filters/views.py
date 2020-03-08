# -*- coding: utf-8 -*-
from collections import Counter

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.db.models import Count
from zap_apps.account.zapauth import ZapView
from zap_apps.filters.filters_common import *
from zap_apps.discover.models import Banner, ProductCollection
from zap_apps.filters.filters_serializer import (FilterCategorySeriaizer, FilterBrandSerializer,
                                                 FilterStyleSerializer, FilterColorSerializer, FilterOccasionSerializer)
from zap_apps.filters.models import DISCOUNT_RULE, disc_range, FILTER_PRICE_TOLERANCE
from zap_apps.filters.tasks import filter_tracker
from zap_apps.zap_analytics.tasks import track_impressions, track_filter, track_sort
from zap_apps.zap_catalogue.models import (ApprovedProduct, Size, SubCategory,
                                           Category, Occasion, Style, Brand, Color, AGE, CONDITIONS)
from zap_apps.zap_catalogue.product_serializer import ApprovedProductSerializer, ApprovedProductSerializerAndroid
from itertools import chain
from zap_apps.filters.get_filters import get_filters
import math
import pdb
import datetime
from django.core.cache import cache

"""
1. Get all the filters applied
2. Hide the filters applied
3. Individually getFilters on all the filters applied
"""


class InitialFilters(ZapView):

    def get(self, request, format=None):

        app_version = request.COOKIES.get('VER', None)

        # Get all the filters applied
        sorted_request_dict = cache_sort(request.GET.copy())
        product_type = None

        # Show all the filters to be hidden in response
        hidden_filters = sorted_request_dict.keys()
        resp = []

        for filter in hidden_filters:
            resp.append(get_filters({}, filter, None, app_version))

        print request.GET.copy(), 'Get parameters'
        print sorted_request_dict, 'Filters applied'
        print hidden_filters, 'Filters to Hide'

        resp.append(hidden_filters)

        return  self.send_response(1, resp)


class Filters(ZapView):

    def get(self, request, filter_type, page_type, format=None):
        #
        app_version = request.COOKIES.get('VER', None)

        sorted_request_dict = cache_sort(request.GET.copy())

        resp = get_filters(sorted_request_dict, filter_type, page_type, app_version)

        # pdb.set_trace()

        return self.send_response(1, resp)


class AnProducts(ZapView):

    def get(self, request, page, page_type=None, format=None):
        # pdb.set_trace()
        # if request.user.is_authenticated() and request.user.logged_device.name == 'ios':
        #     ios = True
        # else:

        perpage = request.GET.get('perpage', settings.CATALOGUE_PERPAGE)
        sorted_request_dict = cache_sort(request.GET.copy())
        try:
            sorted_request_dict.pop('perpage')
        except:
            pass

        if 'origin' in sorted_request_dict:
            origin = sorted_request_dict.pop('origin')
            # filter_type_resp_list = [d for d in filter_type_resp_list if d['value'] not in origin]
        if 'user_price' in sorted_request_dict:
            # user_price = sorted_request_dict['user_price']
            del sorted_request_dict['user_price']

        if page_type in ['zap_market', 'zap_curated', 'designer']:
            product_type = page_type
        else:
            product_type = None
        products = getProducts(sorted_request_dict, product_type=product_type)

        user = str(
            request.user.id) if request.user.is_authenticated() else "Guest"

        # page = request.GET.get('page', 1)

        paginator = Paginator(products, perpage)
        if page:
            page = int(page)
        if not paginator.num_pages >= page or page == 0:
            data = {
                'data': [],
                'page': page,
                'total_pages': paginator.num_pages,
                'next': True if page == 0 else False,
                'previous': False if page == 0 else True}
            return self.send_response(1, data)
        p = paginator.page(page)
        # track_filtered_feed(sorted_request_dict, request, products, page)
        srlzr = ApprovedProductSerializerAndroid(p, many=True,
                                                 context={'logged_user': request.user})
        data = {'data': srlzr.data, 'page': page, 'total_pages': paginator.num_pages,
                'next': p.has_next(), 'previous': p.has_previous()}

        if int(page) == 1 and ('collection' in sorted_request_dict or 'collection' in sorted_request_dict['initial_filters']):
            data.update({'collection_data': {}})
            try:
                collection_value = sorted_request_dict['collection'][0]
            except:
                collection_value = sorted_request_dict['initial_filters']['collection'][0]
            if str(collection_value).isdigit():
                banner_object = Banner.objects.get(id=int(collection_value))
            else:
                banner_object = Banner.objects.get(slug=str(collection_value))
            if banner_object:
                data['collection_data'].update({'title': banner_object.title})
                data['collection_data'].update({'description': banner_object.description if banner_object.description else ''})
                if request.PLATFORM in ['IOS', 'ANDROID'] or request.META.get('HTTP_MOBILE', 'false') == 'true':
                    data['collection_data'].update({'image': ('/zapmedia/'+str(banner_object.collection_image_mobile)) if banner_object.collection_image_mobile else None})
                    data['collection_data'].update({'image_resolution': {'width':banner_object.collection_image_width,'height':banner_object.collection_image_height}})
                else:
                    data['collection_data'].update({'image': ('/zapmedia/'+str(banner_object.collection_image_web)) if banner_object.collection_image_web else None})
                action_link = banner_object.action.collection_filter
                # argument_dict = cache_sort(action_link)
                filter_parameter = action_link.split('?')
                arguments = str(filter_parameter[1]).split('&')
                argument_dict = {}
                for argument in arguments:
                    keyvalues = str(argument).split('=')
                    argument_dict.update({keyvalues[0]:keyvalues[1].split(',')})
                if 'campaign' in argument_dict:
                    campaign = Campaign.objects.get(id=argument_dict['campaign'][0])
                    if campaign and campaign.is_running():
                        data['collection_data'].update({'title': campaign.name})
                        data['collection_data'].update({'description': campaign.description if campaign.description else ''})
                        data['collection_data'].update({'sale_info': 'NOW LIVE'})
                        timediff = campaign.offer.end_time.replace(tzinfo=None) - datetime.datetime.now().replace(tzinfo=None)
                        data['collection_data'].update({'end_time': timediff.days * 86400 + timediff.seconds})
                        data['collection_data'].update({'end_timestamp': timediff.total_seconds()})
                        data['collection_data'].update({'show_timer': campaign.offer.show_timer})
                    elif campaign and campaign.in_future():
                        data['collection_data'].update({'title': campaign.name})
                        data['collection_data'].update({'description': campaign.description if campaign.description else ''})
                        data['collection_data'].update({'sale_info': 'STAY TUNED'})
                        timediff = datetime.datetime.now().replace(tzinfo=None) - campaign.offer.start_time.replace(tzinfo=None)
                        data['collection_data'].update({'end_time': timediff.days * 86400 + timediff.seconds})
                        data['collection_data'].update({'end_timestamp': timediff.total_seconds()})
                        data['collection_data'].update({'show_timer': campaign.offer.show_timer})
        elif int(page) == 1 and page_type:
            if page_type == 'brand' and 'brand' in sorted_request_dict['initial_filters']:
                data.update({'collection_data': {}})
                brand_value = sorted_request_dict['initial_filters']['brand'][0]
                if unicode(brand_value).isdigit():
                    brand_object = Brand.objects.get(id=int(brand_value))
                else:
                    brand_object = Brand.objects.get(slug=str(brand_value))
                data['collection_data'].update({'image': str(brand_object.clearbit_logo)})
                data['collection_data'].update({'image_resolution': {'width': 800,
                                                                     'height': 400}})
                data['collection_data'].update({'title': brand_object.brand})
                data['collection_data'].update({'description': brand_object.description if brand_object.description else ''})
            elif page_type == 'category' and 'category' in sorted_request_dict['initial_filters']:
                data.update({'collection_data': {}})
                category_value = sorted_request_dict['initial_filters']['category'][0]
                if unicode(category_value).isdigit():
                    category_object = Category.objects.get(id=int(category_value))
                else:
                    category_object = Category.objects.get(slug=str(category_value))
                data['collection_data'].update({'image': settings.DOMAIN_NAME + '/zapmedia/' + str(category_object.mobile_cover)})
                data['collection_data'].update({'image_resolution': {'width': 800,
                                                                     'height': 400}})
                data['collection_data'].update({'title': category_object.name})
                data['collection_data'].update({'description': category_object.description if category_object.description else ''})
            elif page_type == 'sub-category' and 'product_category' in sorted_request_dict['initial_filters']:
                data.update({'collection_data': {}})
                category_value = sorted_request_dict['initial_filters']['product_category'][0]
                if unicode(category_value).isdigit():
                    category_object = SubCategory.objects.get(id=int(category_value))
                else:
                    category_object = SubCategory.objects.get(slug=str(category_value))
                data['collection_data'].update({'title': category_object.name})
                data['collection_data'].update({'description': category_object.description if category_object.description else ''})
        try:
            track_filtered_feed(
                sorted_request_dict, request, srlzr.data, page)
        except:
            pass
        result = data
        # cache.set(cache_key, result)
        return self.send_response(1, result)


class Products(ZapView):

    def get(self, request, page, page_type, format=None):
        # pdb.set_trace()
        # ios = False
        perpage = request.GET.get('perpage', settings.CATALOGUE_PERPAGE)
        sorted_request_dict = cache_sort(request.GET.copy())
        try:
            sorted_request_dict.pop('perpage')
        except:
            pass
        if 'origin' in sorted_request_dict:
            origin = sorted_request_dict.pop('origin')
        if 'user_price' in sorted_request_dict:
            # user_price = sorted_request_dict['user_price']
            del sorted_request_dict['user_price']

        user = str(
            request.user.id) if request.user.is_authenticated() else "Guest"

        products = getProducts(sorted_request_dict)

        paginator = Paginator(products, perpage)
        p = paginator.page(page)
        srlzr = ApprovedProductSerializer(p, many=True,
                                          context={'logged_user': request.user})
        data = {'data': srlzr.data, 'page': page, 'total_pages': paginator.num_pages,
                'next': p.has_next(), 'previous': p.has_previous()}

        if int(page) == 1 and ('collection' in sorted_request_dict or 'collection' in sorted_request_dict['initial_filters']):
            data.update({'collection_data': {}})
            try:
                collection_value = sorted_request_dict['collection'][0]
            except:
                collection_value = sorted_request_dict['initial_filters']['collection'][0]
            if str(collection_value).isdigit():
                banner_object = Banner.objects.get(id=int(collection_value))
            else:
                banner_object = Banner.objects.get(slug=str(collection_value))
            if banner_object:
                data['collection_data'].update({'title': banner_object.title})
                data['collection_data'].update({'description': banner_object.description})
                if request.PLATFORM in ['IOS', 'ANDROID'] or request.META.get('HTTP_MOBILE', 'false') == 'true':
                    data['collection_data'].update({'image': ('/zapmedia/'+str(banner_object.collection_image_mobile)) if banner_object.collection_image_mobile else None})
                    data['collection_data'].update({'image_resolution': {'width':banner_object.collection_image_width,'height':banner_object.collection_image_height}})
                else:
                    data['collection_data'].update({'image': ('/zapmedia/'+str(banner_object.collection_image_web)) if banner_object.collection_image_web else None})
                action_link = banner_object.action.collection_filter
                # argument_dict = cache_sort(action_link)
                filter_parameter = action_link.split('?')
                arguments = str(filter_parameter[1]).split('&')
                argument_dict = {}
                for argument in arguments:
                    keyvalues = str(argument).split('=')
                    argument_dict.update({keyvalues[0]:keyvalues[1].split(',')})
                if 'campaign' in argument_dict:
                    campaign = Campaign.objects.get(id=argument_dict['campaign'][0])
                    if campaign and campaign.is_running():
                        data['collection_data'].update({'title': campaign.name})
                        data['collection_data'].update({'description': campaign.description})
                        data['collection_data'].update({'sale_info': 'NOW LIVE'})
                        timediff = campaign.offer.end_time.replace(tzinfo=None) - datetime.datetime.now().replace(tzinfo=None)
                        data['collection_data'].update({'end_time': timediff.days * 86400 + timediff.seconds})
                        data['collection_data'].update({'end_timestamp': (campaign.offer.end_time.replace(tzinfo=None) - datetime.datetime(1970, 1, 1)).total_seconds()})
                        data['collection_data'].update({'show_timer': campaign.offer.show_timer})
                    elif campaign and campaign.in_future():
                        data['collection_data'].update({'title': campaign.name})
                        data['collection_data'].update({'description': campaign.description})
                        data['collection_data'].update({'sale_info': 'STAY TUNED'})
                        timediff = datetime.datetime.now().replace(tzinfo=None) - campaign.offer.start_time.replace(tzinfo=None)
                        data['collection_data'].update({'end_time': timediff.days * 86400 + timediff.seconds})
                        data['collection_data'].update({'end_timestamp': (campaign.offer.start_time.replace(tzinfo=None) - datetime.datetime(1970, 1, 1)).total_seconds()})
                        data['collection_data'].update({'show_timer': campaign.offer.show_timer})
        elif int(page) == 1 and page_type:
            if page_type == 'brand' and 'brand' in sorted_request_dict['initial_filters']:
                data.update({'collection_data': {}})
                brand_value = sorted_request_dict['initial_filters']['brand'][0]
                if unicode(brand_value).isdigit():
                    brand_object = Brand.objects.get(id=int(brand_value))
                else:
                    brand_object = Brand.objects.get(slug=str(brand_value))
                data['collection_data'].update({'title': brand_object.brand})
                data['collection_data'].update({'description': brand_object.description})
            elif page_type == 'category' and 'category' in sorted_request_dict['initial_filters']:
                data.update({'collection_data': {}})
                category_value = sorted_request_dict['initial_filters']['category'][0]
                if unicode(category_value).isdigit():
                    category_object = Category.objects.get(id=int(category_value))
                else:
                    category_object = Category.objects.get(slug=str(category_value))
                data['collection_data'].update({'title': category_object.name})
                data['collection_data'].update({'description': category_object.description})
            elif page_type == 'sub-category' and 'product_category' in sorted_request_dict['initial_filters']:
                data.update({'collection_data': {}})
                category_value = sorted_request_dict['initial_filters']['product_category'][0]
                if unicode(category_value).isdigit():
                    category_object = SubCategory.objects.get(id=int(category_value))
                else:
                    category_object = SubCategory.objects.get(slug=str(category_value))
                data['collection_data'].update({'title': category_object.name})
                data['collection_data'].update({'description': category_object.description})

        try:
            track_filtered_feed(
                sorted_request_dict, request, srlzr.data, page)
        except:
            pass
        result = data

        # cache.set(cache_key, result)
        return self.send_response(1, result)


class webFilterItems1(ZapView):

    def get(self, request, format=None):
        data = {
            'category': [{'title': c.name} for c in Category.objects.annotate(max_count=Count('subcategory__approvedproduct')).order_by('-max_count')],
            'occasion': [{'title': o.name} for o in Occasion.objects.annotate(max_count=Count('approvedproduct')).order_by('-max_count')[:9]],
            'style': [{'title': s.style_type} for s in Style.objects.annotate(max_count=Count('approvedproduct')).order_by('-max_count')],
            'brand': [{'title': b.brand} for b in Brand.objects.annotate(max_count=Count('approvedproduct')).order_by('-max_count')[:8]]
        }

        return self.send_response(1, data)


class webFilterItems(ZapView):
    def get(self, request, format=None):
        cache_key = request.get_full_path()+"_{}".format((request.user.id if request.user.is_authenticated() else ""))
        result = cache.get(cache_key)
        if not result:
            data = {
                'size': {'value' : [{'value' : [{'id':s.id,'name':s.size,'count':1} for s in Size.objects.filter(category_type='C').distinct('size')]}]},
                'disc' : {'value' : [{"count": 1,"id": 1,"value": "70% and higher"},{"count": 1,"id": 2,"value": "50% and higher"},{"count": 1,"id": 3,"value": "30% and higher"},{"count": 1,"id": 4,"value": "10% and higher"}]},
                'category' : {'value' : [{'name': c.name, 'value':[{'name':s.name,'id':s.id,'count':1} for s in SubCategory.objects.filter(parent=c) if s.approvedproduct_set.filter(sale='2',status='1').count()]} for c in Category.objects.all()]},
                'occasion' : {'value' : [{'name': o.name,'id':o.id,'count':1} for o in Occasion.objects.all()]},
                'style' : {'value' : [{'count':1,'name': s.style_type, 'id':s.id} for s in Style.objects.all()]},
                'brand' : {'value' : [{'count':1,'name': b.brand,'id':b.id} for b in Brand.objects.all()]},
                'color' : {'value' : [{'count':1,'name':c.name,'id':c.id,'code':c.code} for c in Color.objects.all()]},
                'age' : {'value' : [{"count": 1,"id": 0,"value": "0-3 months"},{"count": 1,"id": 1,"value": "3-6 months"},{"count": 1,"id": 2,"value": "6-12 months"},{"count": 1,"id": 3,"value": "1-2 years"}]},
                'condition' : {'value' : [{'count':1,'id':'0','value':'New with tags'},{'count':1,'id':'1','value':'Mint Condition'},{'count':1,'id':'2','value':'Gently loved'},{'count':1,'id':'3','value':'Worn out'}]},
                'campaign' : [{'name':c.name,'id':c.id} for c in Campaign.objects.all()],
                'collection':[{'name':b.slug} for b in Banner.objects.all()]
            }
            result = data
            cache.set(cache_key, result)
        return self.send_response(1, result)

import requests, json
from collections import defaultdict
from  zap_apps.marketing.models import CampaignProducts

class ElasticFilters(ZapView):

    def __init__(self):
        self.all_filters = ["occasion", "style", "brand","color","disc", "listing_price", "product_category", "shop","size"]
        self.clt_filters = ["occasion", "style", "brand","color","disc", "price", "size", "product_category","shop"]
        self.DISCOUNT_RULE = {4 : 10, 3:30, 2:50, 1:70}
        self.shop_filter = ['brand', 'designer', 'curated', 'market','highstreet']
        self.i_filter = None
        self.search_ids = ''
        self.i_brand = ''
        self.i_category = ''
        self.i_product_category = ''
        self.i_collection = ''
        self.initial_keys = {}
        self.search_ids = ''

    def get(self, request, filter_type, page_type, format=None):

        available_filters = cache.get('cache_filter_items')
        if not available_filters:
            available_filters = {
                'styles': [{"key": s.id,"name": s.style_type,"selected": False} for s in Style.objects.all()],
                'occasions': [{"key": o.id,"name": o.name,"selected": False} for o in Occasion.objects.all()],
                'brands': [{"key": b.id,"name": b.brand,"selected": False} for b in Brand.objects.all()],
                'colors': [{"key": c.id,"name": c.name,"code":c.code,"selected": False} for c in Color.objects.all()],
                'category': [{'c': s.parent.name, 'id': s.parent.id, 'key': s.id, 'name': s.name} for s in SubCategory.objects.all()],
                'sizes': [{"name" : s.size, "key":s.id, "ctype" : s.category_type, "display":"EU - "+s.eu_size, 'tooltip': "EU - "+s.eu_size + "  (US-" + s.us_size+"  |  UK-" + s.uk_size + ")"} for s in Size.objects.all()]
            }
            cache.set('cache_filter_items',available_filters)       
        discounts = [
            {"key": "1","name": "70% and higher","selected": False},
            {"key": "2","name": "50% and higher","selected": False},
            {"key": "3","name": "30% and higher","selected": False},
            {"key": "4","name": "10% and higher","selected": False},
        ]
        shops = [
            {"name": "Indian", "selected": False, "value": "designer", "disabled": False, "id": 1, "key":"designer"},
            {"name": "Curated", "selected": False, "value": "curated", "disabled": False, "id": 2, "key":"curated"},
            {"name": "Marketplace", "selected": False, "value": "market", "disabled": False, "id": 3, "key" : "market"},
            {"name": "International", "selected": False, "value": "brand", "disabled": False, "id": 4, "key":"brand"}
        ]
        filter_items = {
            "style":available_filters['styles'],
            "occasion":available_filters['occasions'],
            "brand":available_filters['brands'],
            "color":available_filters['colors'],
            "disc":discounts, 
            # "product_category":[], 
            "shop":shops, 
            # "size_type":available_filters['sizes']
        }
        uri = settings.ELASTIC_URL+'_search?'
        params = request.GET.copy()
        try:
            search_key = params.pop('search')
        except KeyError:
            search_key = ''
        applied_keys, initial_keys = self.get_keys(params)
        print applied_keys,' applied keys'
        print initial_keys,' initial_keys'
        if search_key:
            src = json.dumps({"_source":["id"]})
            response = requests.post(uri+'size=5000&q='+search_key[0], data=src)
            results = json.loads(response.text)
            self.search_ids = [i['_source']['id'] for i in results['hits']['hits']] or [0]
            print self.search_ids,' search idsssss'
        self.initial_keys = initial_keys
        if initial_keys:
            if 'shop' in initial_keys:
                if initial_keys['shop'][0] == 'pre-loved':
                    self.shop_filter = ['curated', 'market']
                elif initial_keys['shop'][0] == 'brand-new':
                    self.shop_filter = ['brand', 'designer']
                else:
                    self.shop_filter = initial_keys['shop']
            
            if 'i_shop' in initial_keys:
                if initial_keys['i_shop'] == 'designer':
                    self.shop_filter = ['designer']
                elif initial_keys['i_shop'] == 'curated':
                    self.shop_filter = ['curated']
                elif initial_keys['i_shop'] == 'brand':
                    self.shop_filter = ['brand']
                elif initial_keys['i_shop'] == 'market':
                    self.shop_filter = ['market']
                elif initial_keys['i_shop'] == 'high-street':
                    self.shop_filter = ['highstreet']
                elif initial_keys['i_shop'] == 'pre-loved':
                    self.shop_filter = ['curated', 'market']
                elif initial_keys['i_shop'] == 'brand-new':
                    self.shop_filter = ['brand', 'designer']            
        if applied_keys:
            e_args = {}
            for f in self.all_filters:
                if not f == 'disc':
                    aggr_query = {
                        "terms": {"field": f, "min_doc_count" : 1,"size":0}
                    }
                else:
                    aggr_query = {   
                        "range" : {
                            "field" : "discount",
                            "ranges" : [
                                { "key" : "4", "from" : 10 },
                                { "key" : "3", "from" : 30 },
                                { "key" : "2", "from" : 50},
                                { "key" : "1", "from" : 70}
                            ]
                        }
                    }
                e_args[f] = {            
                    "filter": {
                        "bool" : {
                              "must" : self.exclude_current_filter(f, applied_keys)
                           }},
                    "aggs": {
                    "names": aggr_query
                    }
                }
            q = json.dumps({"size":0, "aggs": e_args})
            # print q,'qqqqqqqqqqqqqqqqqqq'
            response = requests.get(uri, data=q)
            results = json.loads(response.text)
            # print results,' applied res'
            # output = {}
            first_res = results['aggregations']
            # print first_res['brand']['names']['buckets'],'applied brand rsults'

        e_args = {}
        for f in self.all_filters:
            if not f == 'disc':
                aggr_query = {
                    "terms": {"field": f, "min_doc_count" : 1,"size":0}
                }
            else:
                aggr_query = {   
                    "range" : {
                        "field" : "discount",
                        "ranges" : [
                            { "key" : "4", "from" : 10 },
                            { "key" : "3", "from" : 30 },
                            { "key" : "2", "from" : 50},
                            { "key" : "1", "from" : 70}
                        ]
                    }
                }
            e_args[f] = {            
                "filter": {
                    "bool" : {
                          "must" : self.include_shop_filter(f)
                       }},
                "aggs": {
                "names": aggr_query
                }
            }
        q = json.dumps({"size":0, "aggs": e_args})
        # print q,'initial filter query'
        response = requests.get(uri, data=q)
        results = json.loads(response.text)
        # print results,' shaaaaaaa'
        output = {}
        res = results['aggregations']
        for r in res:
            if r == 'disc':
                res[r]['names']['buckets'] = [disc_obj for disc_obj in res[r]['names']['buckets'] if disc_obj['doc_count']>0]
            if applied_keys:
                l1 = []
                for d in res[r]['names']['buckets']:
                    d.update({'doc_count':0})
                    l1.append(d)
                if len(l1):
                    l2 = first_res[r]['names']['buckets']

                    d = defaultdict(dict)
                    for l in (l1, l2):
                        for elem in l:
                            d[elem['key']].update(elem)
                    res_buckets = d.values()
                else:
                    res_buckets = []
            else:
                res_buckets = res[r]['names']['buckets']

            # print '----------------',r,'--------------'
            if r == 'product_category':
                response = []
                # pdb.set_trace()
                for sub in res_buckets:
                    for cat in available_filters['category']:
                        if cat['key'] == sub['key']:
                            selected = False
                            if "product_category" in applied_keys and cat['key'] in applied_keys["product_category"]:
                                selected = True
                            s1 = {"selected" : selected, "name": cat['name'], "disabled": False if sub['doc_count'] else True}
                            s1.update(sub)
                            flag = True
                            for rr in response:
                                if rr['id'] == cat['id'] and rr['name'] == cat['c']:
                                    rr['sub_cats'].append(s1)
                                    flag = False
                                    break
                            if flag:
                                response.append(
                                    {
                                        "id" : cat['id'],
                                        "name" : cat['c'],
                                        "sub_cats" : [s1],
                                        "value" : []
                                    })
                for k in response:
                    k['doc_count'] = sum(item['doc_count'] for item in k['sub_cats'])                
                output['category'] = response
            elif r == 'size':                
                resp = []
                for s in res_buckets:
                    for c in available_filters['sizes']:
                        if c['key'] == int(s['key']):
                            selected = False
                            if "size" in applied_keys and c['key'] in applied_keys["size"]:
                                selected = True
                            if c['ctype'] == 'C':
                                s2 = {"value":c['name'],"selected":selected}
                            elif c['ctype'] == 'FW':
                                s2 = {"value":c['name'],"selected":selected, "display":c['display'], 'tooltip':c['tooltip']}
                            else:
                                break
                            s2.update(s)
                            flag = True
                            for re in resp:
                                if re['name'] == "FOOTWEAR SIZE" and c['ctype'] == "FW":
                                    re['size'].append(s2)
                                    flag = False
                                    break
                                elif re['name'] == "CLOTHING SIZE" and c["ctype"] == "C":
                                    exists = False
                                    for c_size in re['size']:
                                        if c_size['value'] == s2['value']:
                                            exists = True
                                            c_size['key'] = str(c_size['key']) + ',' + str(s2['key'])
                                            c_size['doc_count'] += s2['doc_count']
                                    if not exists:
                                        re['size'].append(s2)
                                    flag = False
                                    break
                            if flag:
                                if c['ctype'] == "FW":
                                    resp.append({"name":"FOOTWEAR SIZE","size":[s2]})
                                elif c['ctype'] == "C":
                                    resp.append({"name":"CLOTHING SIZE","size":[s2]})
                output['size_type'] = [res_size for res_size in resp if len(res_size['size'])>1]
            elif r == 'listing_price':
                prices = [p['key'] for p in res_buckets]
                prices.sort()
                price_list = []
                length = len(prices)
                if length > 5:
                    bucket_size = max(5.0, math.ceil(length/5.0))
                    num_buckets = int(math.ceil(length/bucket_size))
                    bucket_size = int(bucket_size)
                    for i in range(0,num_buckets):
                        try:
                            price_list.append({
                                "start_value": prices[(i*bucket_size)],
                                "end_value": prices[(i+1)*bucket_size-1]
                            })
                        except IndexError:
                            price_list.append({
                                "start_value": prices[(i*bucket_size)],
                                "end_value": prices[length-1]
                            })
                    output["price"] = price_list
                else:
                    output["price"] = None
            elif r == 'shop':
                clt_resp = []
                for i in res_buckets:
                    for b in filter_items[r]:
                        if b['key'] == i['key']:
                            if r in applied_keys and i['key'] in applied_keys[r]:
                                b['selected'] = True
                            i.update(b)
                            clt_resp.append(i)
                if len(clt_resp) > 1:
                    output[r] = clt_resp        
                else:
                    output[r] = None
            else:
                clt_resp = []
                for i in res_buckets:
                    for b in filter_items[r]:
                        if b['key'] == i['key']:
                            if r in applied_keys and int(i['key']) in applied_keys[r]:
                                b['selected'] = True
                            i.update(b)
                            clt_resp.append(i)
                if len(clt_resp) > 1:
                    output[r] = clt_resp        
                else:
                    output[r] = None
                if r == 'brand':
                    alphas = list(set([x['name'][0:1].upper() if not unicode(x['name'][0:1]).isdigit() else '#' for x in clt_resp]))
                    alphas.sort()
                    output['brand_alphas'] = alphas
            # print output,' ------=========='
        return self.send_response(1, output)

    def exclude_current_filter(self,f, sorted_request_dict):
        f_list = []
        for i in self.clt_filters:
            # print i,'iiiiiiiiiiiii',f,' sorted', sorted_request_dict
            if not f==i and i in sorted_request_dict:
                if i == 'disc':
                    #{"range" : {"discount" : { "gte" : 50 }}}
                    f_list.insert(0, {"range" : {"discount" : { "gte": self.DISCOUNT_RULE[min(sorted_request_dict[i])] }}})
                elif i == 'price':
                    price_params = sorted_request_dict[i]
                    if price_params[0] and price_params[1]:
                        f_list.insert(0, {"range" : {"listing_price" : { "gte": price_params[0], "lte": price_params[1]}}})
                    elif price_params[0]:
                        f_list.insert(0, {"range" : {"listing_price" : { "gte": price_params[0]}}})
                    else:
                        f_list.insert(0, {"range" : {"listing_price" : { "lte": price_params[1]}}})
                else:
                    f_list.insert(0, { "terms" : {i :sorted_request_dict[i]}})
                    
        if self.shop_filter:
            f_list.insert(0, {"terms" : {"shop":self.shop_filter}})
        if 'color' in self.initial_keys:
            f_list.insert(0, {"terms" : {"color":self.initial_keys['color']}})
        if 'i_category' in self.initial_keys:
            f_list.insert(0, {"term" : {"i_category":self.initial_keys['i_category']}})
        if 'i_product_category' in self.initial_keys:
            f_list.insert(0, {"term" : {"i_product_category":self.initial_keys['i_product_category']}})
        if 'i_brand' in self.initial_keys:
            f_list.insert(0, {"term" : {"i_brand":self.initial_keys['i_brand']}})
        if 'brand' in self.initial_keys:
            f_list.insert(0, {"terms" : {"brand":self.initial_keys['brand']}})
        if 'i_style' in self.initial_keys:
            f_list.insert(0, {"term" : {"i_style":self.initial_keys['i_style']}})
        if self.search_ids:
            f_list.insert(0, {"terms" : {"id":self.search_ids}})
        return f_list

    def include_shop_filter(self, f):
        f_list = []
        if self.shop_filter:
            f_list.insert(0, {"terms" : {"shop":self.shop_filter}})
        if 'i_brand' in self.initial_keys:
            f_list.insert(0, {"term" : {"i_brand":self.initial_keys['i_brand']}})
        if 'brand' in self.initial_keys:
            f_list.insert(0, {"terms" : {"brand":self.initial_keys['brand']}})
        if 'i_color' in self.initial_keys:
            f_list.insert(0, {"term" : {"i_color":self.initial_keys['i_color']}})
        if 'color' in self.initial_keys:
            f_list.insert(0, {"terms" : {"color":self.initial_keys['color']}})
        if 'i_product_category' in self.initial_keys:
            f_list.insert(0, {"term" : {"i_product_category":self.initial_keys['i_product_category']}})
        if 'product_category' in self.initial_keys:
            f_list.insert(0, {"terms" : {"product_category":self.initial_keys['product_category']}})
        if 'i_category' in self.initial_keys:
            f_list.insert(0, {"term" : {"i_category":self.initial_keys['i_category']}})
        if 'category' in self.initial_keys:
            f_list.insert(0, {"terms" : {"category":self.initial_keys['category']}})
        if 'i_occasion' in self.initial_keys:
            f_list.insert(0, {"term" : {"i_occasion":self.initial_keys['i_occasion']}})
        if 'i_style' in self.initial_keys:
            f_list.insert(0, {"term" : {"i_style":self.initial_keys['i_style']}})
        if 'id' in self.initial_keys:
            f_list.insert(0, {"terms" : {"id":self.initial_keys['id']}})
        if self.search_ids:
            f_list.insert(0, {"terms" : {"id":self.search_ids}})   
        return f_list

    def get_keys(self, params):
        applied_keys = {}
        initial_keys = {}
        for key in params.iterkeys():
            if key.startswith('i_'):
                if key in ['i_collection', 'collection']:
                    banner_object = Banner.objects.get(slug=params[key])
                    action_link = banner_object.action.collection_filter
                    from django.http import QueryDict
                    collection_params = QueryDict(action_link[unicode(action_link).index('?')+1:])  #remove ? and the part before that - send only the query part
                    collection_keys, collection_initial_keys = self.get_keys(collection_params)
                    initial_keys.update(collection_initial_keys)
                    initial_keys.update(collection_keys)
                elif key == 'i_product_collection':
                    initial_keys['id'] = [p.id for p in ApprovedProduct.objects.filter(in_collection__in=params['i_product_collection'].split(','))]
                else:
                    if params[key].split(",")[0].isdigit():
                        initial_keys[key.split('i_')[1]] = params[key].split(',')
                    else:
                        initial_keys[key] = params[key]
            elif key == 'campaign':
                initial_keys['id'] = [p.products.id for p in CampaignProducts.objects.filter(campaign__in=params['campaign'].split(','))]
            elif key == 'product_collection':
                initial_keys['id'] = [p.id for p in ApprovedProduct.objects.filter(in_collection__in=params['product_collection'].split(','))]
            else:
                applied_keys[key] = [int(x) if x.isdigit() else x for x in params[key].split(",")]
        return applied_keys, initial_keys

class ElasticProducts(ZapView):
    def get(self, request, page, page_type):
        uri = settings.ELASTIC_URL+'_search?'
        params = request.GET.copy()
        try:
            search_key = params.pop('search')
        except KeyError:
            search_key = ''
        if search_key:
            src = json.dumps({"_source":["id"]})
            response = requests.post(uri+'size=5000&q='+search_key[0], data=src)
            results = json.loads(response.text)
            self.search_ids = [i['_source']['id'] for i in results['hits']['hits']] or [0]
        keys, initial_keys =  self.get_keys(params)
        perpage = keys.pop('perpage')
        try:
            sort_id = keys.pop('sort')[0]
        except KeyError:
            sort_id = 0
        if sort_id == 0:
            sort_option = { "score": { "order": "desc" }}
        elif sort_id == 1:
            sort_option = { "listing_price": { "order": "desc" }}
        elif sort_id == 2:
            sort_option = { "listing_price": { "order": "asc" }}
        elif sort_id == 3:
            sort_option = { "love_count": { "order": "desc" }}
        else:
            sort_option = { "discount": { "order": "desc" }}
        print keys,' keys'
        print initial_keys,'initial_keys'
        filter_terms = []
        if 'shop' in keys:
            filter_terms.append({"terms": {"shop": keys['shop']}})
        elif 'shop' in initial_keys:
            filter_terms.append({"terms": {"shop": ["curated","market"] if initial_keys['shop'][0] == "pre-loved" else ["brand","designer"] if initial_keys['shop'][0] == "brand-new" else initial_keys['shop']}})
        elif 'i_shop' in initial_keys:
            if initial_keys['i_shop'] == 'designer':
                filter_terms.append({ "terms" : {"shop" : ["designer"]}})
            elif initial_keys['i_shop'] == 'brand':
                filter_terms.append({ "terms" : {"shop" : ["brand"]}})
            elif initial_keys['i_shop'] == 'curated':
                filter_terms.append({ "terms" : {"shop" : ["curated"]}})
            elif initial_keys['i_shop'] == 'market':
                filter_terms.append({ "terms" : {"shop" : ["market"]}})
            elif initial_keys['i_shop'] == 'high-street':
                filter_terms.append({ "terms" : {"shop" : ["highstreet"]}})
            elif initial_keys['i_shop'] == 'brand-new':
                filter_terms.append({ "terms" : {"shop" : ["brand","designer"]}})
            elif initial_keys['i_shop'] == 'pre-loved':
                filter_terms.append({ "terms" : {"shop" : ["curated", "market"]}})
        elif not 'id' in keys:
            filter_terms.append({ "terms" : {"shop" : ["curated","market","brand","designer","highstreet"]}})
        if keys:
            for i in keys.iterkeys():
                if i == 'brand':
                    if 'brand' in keys:
                        filter_terms.append({"terms" : {"brand": keys['brand']}})
                    elif 'i_brand' in initial_keys:
                        filter_terms.append({"term" : {"i_brand": initial_keys['i_brand'].lower()}})
                elif i == 'disc':
                    filter_terms.append({"range" : {"discount" : { "gte": self.DISCOUNT_RULE[min(keys[i])] }}})
                elif i == 'price':
                    price_condition = {}
                    if not keys['price'][0] == '':
                        price_condition['gte'] = keys['price'][0]
                    if not keys['price'][1] == '':
                        price_condition['lte'] = keys['price'][1]
                    filter_terms.append({"range" : {"listing_price" : price_condition}})
                else:
                    filter_terms.append({"terms" : {i: keys[i]}})
        if 'i_occasion' in initial_keys:
            filter_terms.append({"term" : {"i_occasion":initial_keys['i_occasion'].lower()}})
        if 'i_product_category' in initial_keys:
            filter_terms.append({"term" : {"i_product_category": initial_keys['i_product_category'].lower()}})
        if 'i_category' in initial_keys:
            filter_terms.append({"term" : {"i_category": initial_keys['i_category'].lower()}})
        if 'product_category' in initial_keys:
            filter_terms.append({"terms" : {"product_category": initial_keys['product_category']}})
        if 'i_category' in initial_keys:
            filter_terms.append({"term" : {"i_category": initial_keys['i_category'].lower()}})
        if 'category' in initial_keys:
            filter_terms.append({"terms" : {"category": initial_keys['category']}})
        if 'i_campaign' in initial_keys:
            filter_terms.append({"terms" : {"id": initial_keys['i_campaign']}})
        if 'i_brand' in initial_keys and not 'brand' in keys:
            filter_terms.append({"term" : {"i_brand": initial_keys['i_brand']}})
        if 'brand' in initial_keys:
            filter_terms.append({"terms" : {"brand": initial_keys['brand']}})
        if 'color' in initial_keys:
            filter_terms.append({"term" : {"color": initial_keys['color']}})
        if 'i_color' in initial_keys:
            filter_terms.append({"term" : {"i_color": initial_keys['i_color']}})
        if 'i_style' in initial_keys:
            filter_terms.append({"term" : {"i_style": initial_keys['i_style']}})
        if 'id' in initial_keys:
            filter_terms.append({"terms" : {"id": initial_keys['id']}})
        if self.search_ids:
            filter_terms.append({"terms" : {"id": self.search_ids}})
        # print filter_terms,' filter_terms',perpage
        eQuery = {
            "from" : int(page)*perpage[0], "size" : perpage[0],
            "query": {
                "constant_score": {
                    "filter" : {
                        "bool" : {
                          "must" : filter_terms
                       }
                     }
                }
            },
            "sort": sort_option
        }

        q = json.dumps(eQuery)
        # print q,'products query'
        response = requests.get(uri, data=q)
        results = json.loads(response.text)
        # print results       
        return self.send_response(1, {"data":results['hits']['hits'],"total":results['hits']['total']})

    def get_keys(self, params):
        applied_keys = {}
        initial_keys = {}
        for key in params.iterkeys():
            if key.startswith('i_'):
                if key == 'i_collection':
                    banner_object = Banner.objects.get(slug=params[key])
                    action_link = banner_object.action.collection_filter
                    from django.http import QueryDict
                    collection_params = QueryDict(action_link[unicode(action_link).index('?')+1:])  #remove ? and the part before that - send only the query part
                    collection_keys, collection_initial_keys = self.get_keys(collection_params)
                    applied_keys.update(collection_initial_keys)
                    initial_keys.update(collection_keys)

                    # print collection_keys,' collection_keys',
                    # print collection_initial_keys,' collection_initial_keys',initial_keys
                elif key == 'i_product_collection':
                    initial_keys['id'] = [p.id for p in ApprovedProduct.objects.filter(in_collection__in=params['i_product_collection'].split(','))]
                else:

                    if params[key].split(",")[0].isdigit():
                        initial_keys[key.split('i_')[1]] = params[key].split(',')
                    else:
                        initial_keys[key] = params[key]
            elif key == 'campaign':
                initial_keys['id'] = [p.products.id for p in CampaignProducts.objects.filter(campaign__in=params['campaign'].split(','))]
            elif key == 'product_collection':
                initial_keys['id'] = [p.id for p in ApprovedProduct.objects.filter(in_collection__in=params['product_collection'].split(','))]
            else:
                applied_keys[key] = [int(x) if x.isdigit() else x for x in params[key].split(",")]
        return applied_keys, initial_keys

    def __init__(self):
        self.DISCOUNT_RULE = {4 : 10, 3:30, 2:50, 1:70}
        self.search_ids = ''

class GetLoveAndOffer(ZapView):

    def post(self, request, format=None):
        from zap_apps.blog.models import BlogPost
        ids = request.data.get('ids',[])
        u = request.user
        p = ApprovedProduct.objects.filter(id__in=ids)
        data = [{"id": obj.id,"offer": obj.get_flash_sale_data(), "liked_by_user": u in obj.loves.all(), 'has_look':
                 True if BlogPost.public_objects.filter(category__slug='look-book', blog_products__item=obj).count() > 0
                 else False} for obj in p]
        return self.send_response(1, data)

