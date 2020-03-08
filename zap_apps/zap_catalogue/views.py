from django.shortcuts import render
from zap_apps.discover.models import ProductCollection, CustomCollection
from zap_apps.discover.models import Banner
from zap_apps.marketing.models import Message
from zap_apps.discover.models import ProductCollection, CustomCollection, Banner, Homefeed
from zap_apps.discover.discover_serializer import HomefeedSerializer
from django.http import HttpResponseRedirect

SHOPS = {
    'designer': 1,
    'curated': 2,
    'market': 3,
    'brand': 4,
    'brand-new': 5,
    'pre-loved': 6,
    'high-street': 7
}


def sell(request):
    return render(request, 'catalogue/sell.html',{'image_header':True,'ZAP_ENV_VERSION': settings.ZAP_ENV_VERSION})


def buy(request):
    return render(request, 'catalogue/buy.html',{'image_header':True,'ZAP_ENV_VERSION': settings.ZAP_ENV_VERSION})


def shops(request, filter=None, value=None, filter2=None, value2=None):
    data = {'image_header': True, 'ZAP_ENV_VERSION': settings.ZAP_ENV_VERSION}
    if filter:
        data.update({'filter':filter, 'value':value})
        filter_context = filter
        value_context = value
        if filter2:
            data.update({'filter2': filter2, 'value2': value2})
            filter_context = filter2
            value_context = value2
        filter_data = {}
        value_context = unicode(value_context).split('/')[0] #to ignore any following parts like right panel url
        if filter_context == 'shop':
            if value_context == 'designer':
                filter_data.update({'page_title':'Buy Designer Lehengas, Choli, Dresses, Sarees Online India'})
                filter_data.update({'header_title': ''})
                filter_data.update({'header_image_mobile': '/zapstatic/website/banners/designer_banner.jpg'})
                filter_data.update({'meta_description':'Top Designer Wear for Indian Wedding, Party and Festive Occassions. Shop from Varun Bahl, Manish Arora and all the best Indian Designers. Free Shipping, Easy Returns & Cash on Delivery.'})
            elif value_context == 'brand':
                filter_data.update({'page_title': "Buy International brands only on Zapyle"})
                filter_data.update({'header_title': ""})
                filter_data.update({'header_image_mobile': '/zapstatic/website/banners/designer_page_banner1.jpg'})
                filter_data.update({'meta_description': 'Shop from Brands like Louis Vuitton, Gucci, Michael Kors, Prada & more for Women. Free Shipping, Easy Returns & Cash on Delivery.'})
            elif value_context == 'curated':
                filter_data.update({'page_title': "Buy Luxury Handbags, Accessories, Shoes & more Online India"})
                filter_data.update({'header_title': "Pre-owned fashion hand-picked from India's most stylish closets"})
                filter_data.update({'header_image_mobile': '/zapstatic/website/banners/curated_page_banner.jpg'})
                filter_data.update({'meta_description': 'Shop from Brands like Louis Vuitton, Gucci, Michael Kors, Prada & more for Women at upto 90% off. Free Shipping, Easy Returns & Cash on Delivery.'})
            elif value_context == 'market':
                filter_data.update({'page_title': 'Buy Pre-owned Luxury Handbags, Accessories, Shoes & more at upto 90% off'})
                filter_data.update({'header_title': 'Shop high street fashion at upto 70% off!'})
                filter_data.update({'header_image_mobile': '/zapstatic/website/banners/buy_banner.jpg'})
                filter_data.update({'meta_description': 'Shop from the closets of women across India for Louis Vuitton, Gucci, Michael Kors, Prada & more at upto 90% off. Free Shipping, Easy Returns & Cash on Delivery.'})
            data.update({'filter_data': filter_data})
        elif filter_context == 'brand':
            if unicode(value_context).isdigit():
                selected_brand = B.objects.get(id=value_context)
            else:
                selected_brand = B.objects.get(slug=value_context)
            filter_data.update({'page_title':selected_brand.brand + ' on Sale Online India - Up to 70% off only at Zapyle'})
            filter_data.update({'meta_description': selected_brand.meta_description})
            filter_data.update({'header_image_mobile': '/zapmedia/' + str(
                selected_brand.mobile_cover) if selected_brand.mobile_cover else (selected_brand.clearbit_logo + '?s=600') if selected_brand.clearbit_logo != 'logo' else None})
            filter_data.update({'header_title' : selected_brand.brand})
            filter_data.update({'description': selected_brand.description if selected_brand.description else None})
            # filter_data.update({'full_description': selected_brand.description if selected_brand.description else None})
            product_ids = ApprovedProduct.objects.filter(brand=selected_brand).values_list('id', flat=True)
            top_categories_for_brand = SubCategory.objects.filter(approvedproduct__in=product_ids).annotate(count=Count('approvedproduct')).order_by('-count')[:4]
            filter_data.update({'meta_description':'Insane discounts on a beautiful collection of authentic '+ selected_brand.brand +' ' + ((top_categories_for_brand[0].name +', ') if len(top_categories_for_brand)>=1 else '') + ((top_categories_for_brand[1].name+', ') if len(top_categories_for_brand)>=2 else '')+((top_categories_for_brand[2].name+', ') if len(top_categories_for_brand)>=3 else '')+((top_categories_for_brand[3].name) if len(top_categories_for_brand)>=4 else '')+' and more for Women Online India. Safe shipping and easy returns. Limited quantity. COD available.'})
            data.update({'filter_data':filter_data})
        elif filter_context == 'sub-category':
            if unicode(value_context).isdigit():
                selected_category = SC.objects.get(id=value_context)
            else:
                selected_category = SC.objects.get(slug=value_context)
            filter_data.update({'page_title': 'Designer Luxury '+ selected_category.name +' on Sale'})
            filter_data.update({'meta_description': selected_category.meta_description})
            filter_data.update({'header_title': selected_category.name})
            filter_data.update({'description': 'Shop Luxury Brands on Sale Only on Zapyle'})
            filter_data.update({'meta_description':'Up to 70% off on a beautiful collection of authentic Luxury '+ selected_category.name +' for women online India. Safe shipping and easy returns. Limited quantity. COD available.'})
            data.update({'filter_data': filter_data})
        elif filter_context == 'category':
            if unicode(value_context).isdigit():
                selected_category = C.objects.get(id=value_context)
            else:
                selected_category = C.objects.get(slug=value_context)
            filter_data.update({'page_title': 'Designer Luxury '+ selected_category.name +' on Sale'})
            filter_data.update({'meta_description': selected_category.meta_description})
            filter_data.update({'header_title': selected_category.name})
            filter_data.update({'description': 'Shop Luxury Brands on Sale Only on Zapyle'})
            filter_data.update({'meta_description':'Up to 70% off on a beautiful collection of authentic Luxury '+ selected_category.name +' for women online India. Safe shipping and easy returns. Limited quantity. COD available.'})
            data.update({'filter_data': filter_data})
        elif filter_context == 'collection':
            if unicode(value_context).isdigit():
                selected_banner = Banner.objects.get(id=value_context)
            else:
                selected_banner = Banner.objects.get(slug=value_context)
            filter_data.update({'page_title': selected_banner.title})
            filter_data.update({'meta_description': selected_banner.meta_description})
            filter_data.update({'custom_collection': 1})
            filter_data.update({'header_title': selected_banner.title})
            filter_data.update({'description': selected_banner.description})
            filter_data.update({'header_image_mobile': '/zapmedia/' + str(selected_banner.collection_image_mobile) if selected_banner.collection_image_mobile else None})
            # filter_data.update({'header_image': '/zapmedia/' + str(selected_banner.collection_image_web) if selected_banner.collection_image_web else None})
            filter_data.update({'seo_description': selected_banner.seo_description})
            data.update({'filter_data': filter_data})
    return render(request, 'catalogue/shops.html', data)

def lists(request, list, filter=None, value=None):

    data = {}
    # pdb.set_trace()
    if filter:
        value = unicode(value).split('/')[0]
        if filter == 'category':
            if unicode(value).isdigit():
                selected_category = C.objects.get(id=value)
            else:
                selected_category = C.objects.get(slug=value)
            products = ApprovedProduct.ap_objects.filter(product_category__parent=selected_category)
        elif filter == 'sub-category':
            if unicode(value).isdigit():
                selected_category = SC.objects.get(id=value)
            else:
                selected_category = SC.objects.get(slug=value)
            products = ApprovedProduct.ap_objects.filter(product_category=selected_category)
        elif filter == 'brand':
            if unicode(value).isdigit():
                selected_brand = B.objects.get(id=value)
            else:
                selected_brand = B.objects.get(slug=value)
            products = ApprovedProduct.ap_objects.filter(brand=selected_brand)
        elif filter == 'shop':
            if unicode(value).isdigit():
                selected_shop = [value]
            else:
                selected_shop = [SHOPS[value]]
            if selected_shop == [5]:
                selected_shop = [1, 4]
            elif selected_shop == [6]:
                selected_shop = [2, 3]
            all_products = ApprovedProduct.ap_objects.all()
            product_ids = [product.id for product in all_products if product.shop in selected_shop]
            products = ApprovedProduct.ap_objects.filter(id__in=product_ids)
    else:
        products = ApprovedProduct.ap_objects.all()
    if list == 'shop':
        pass
    elif list == 'brand':
        brand_items = []
        brand_ids = products.values_list('brand', flat=True)
        brands = B.objects.filter(id__in=brand_ids).order_by('brand')
        index = 0
        current_letter = {}
        for brand in brands:
            try:
                if brand.brand[0].lower() != brands[index-1].brand[0].lower() and not unicode(brand.brand[0]).isdigit():
                    brand_items.append(current_letter)
                    current_letter = {'starts_with': brand.brand[0].upper(), 'brands': [{'name': brand.brand, 'url': brand.slug}]}
                else:
                    current_letter['brands'].append({'name': brand.brand, 'url': brand.slug})
            except:
                if unicode(brand.brand[0]).isdigit():
                    current_letter = {'starts_with': '#', 'brands': [{'name': brand.brand, 'url': brand.slug}]}
                else:
                    current_letter = {'starts_with': brand.brand[0].upper(), 'brands': [{'name': brand.brand, 'url': brand.slug}]}
            index = index + 1
        brand_items.append(current_letter)
        data.update({'brand_groups': brand_items})
    elif list == 'category':
        category_items = []
        subcategory_ids = products.values_list('product_category', flat=True)
        subcategorys = SC.objects.annotate(l_count=Count('approvedproduct')).filter(id__in=subcategory_ids).order_by('-l_count')
        categorys = {}
        for subcategory in subcategorys:
            try:
                categorys[subcategory.parent.slug].append({'name': subcategory.name, 'url': subcategory.slug})
            except:
                categorys[subcategory.parent.slug] = [{'name': subcategory.name, 'url': subcategory.slug}]
        for key in categorys:
            category = C.objects.get(slug=key)
            category_items.append({'name' : category.name, 'url' : key, 'subcategorys' : categorys[key]})
        data.update({'category_groups': category_items})
    if filter:
        data.update({'filter': filter, 'value': value, 'base_url': '/' + filter + '/' + value})
    return render(request, 'catalogue/lists.html', data)

def WebsiteProductView(request, title, id):
    p = ApprovedProduct.ap_objects.get(id=id)
    title_converted = p.title.lower().replace(' ','-')
    if not title_converted == title.split('/')[0]:
        return HttpResponseRedirect('/product/{}/{}'.format(id,title_converted))
    srlzr = WebsiteProductSerializer(p)
    data = srlzr.data
    # print data,'------------------'
    # data['h'] = WebsiteHeaderProducts()
    data['domain'] = settings.CURRENT_DOMAIN
    data['ZAP_ENV_VERSION'] = settings.ZAP_ENV_VERSION
    return render(request, 'catalogue/product.html', data)

def WebsiteProfileView(request, id, username):
    user = ZapUser.objects.get(id=id)
    data = {
            'id' : user.id,
            'zap_username' : user.zap_username,
            'profile_pic' : user.profile.profile_pic,
            'description' : user.profile.description,
            'full_name' : user.get_full_name(),
            'admirers_count' : user.profile.admiring.count(),
            'ZAP_ENV_VERSION': settings.ZAP_ENV_VERSION
        }
    return render(request, 'user/profile.html', data)


def WebsiteLoveView(request):
    # user = ZapUser.objects.get(id=id)
    # data = {
    #         'zap_username' : user.zap_username,
    #         'profile_pic' : user.profile.profile_pic,
    #         'description' : user.profile.description,
    #         'full_name' : user.get_full_name()
    #     }
    return render(request, 'user/my_loves.html',{'ZAP_ENV_VERSION': settings.ZAP_ENV_VERSION})#, data)

from zap_apps.account.zapauth import ZapView, ZapAuthView

def AboutUs(request):
    return render(request, 'account/about_us.html',{'image_header':True,'ZAP_ENV_VERSION': settings.ZAP_ENV_VERSION})

def Authenticity(request):
    return render(request, 'account/authenticity.html',{'image_header':True,'ZAP_ENV_VERSION': settings.ZAP_ENV_VERSION})

class ContactUs(ZapView):
    def get(self, request, format=None):
        return render(request, 'account/contact_us.html',{'image_header':False,'ZAP_ENV_VERSION': settings.ZAP_ENV_VERSION})
    def post(self, request):
        print request.data
        params = request.data
        Message.objects.create(email_phone=params['email_phone'],note=params['notes'])
        return self.send_response(1, {'data':'tet'})

def Terms(request):
    return render(request, 'account/terms-conditions.html',{'image_header':False,'ZAP_ENV_VERSION': settings.ZAP_ENV_VERSION})
def WorldTour(request):
    return render(request, 'account/world_tour.html', {'image_header': False, 'ZAP_ENV_VERSION': settings.ZAP_ENV_VERSION})
def Subscribe(request):
    return render(request, 'account/subscription.html', {'image_header': True, 'ZAP_ENV_VERSION': settings.ZAP_ENV_VERSION})

####################new_updates ends here###############################

from django.template.loader import render_to_string
from rest_framework.response import Response

from zap_apps.filters.filters_common import get_sort_data, cache_sort, getProducts
from zap_apps.zap_analytics.tasks import track_impressions, track_product, track_filter, track_sort
from zap_apps.zap_catalogue.models import Hashtag, Comments, Size, Loves, Brand as B, Occasion as O, Category as C, Style as S, ZapCuratedEntryImages, SubCategory as SC
from zap_apps.zap_catalogue.product_serializer import *

# Create your views here.
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Count, Sum
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer

from zap_apps.zap_catalogue.tasks import product_view_tracker
from zap_apps.zap_commons.adapters import Int4NumericRange
from zap_apps.zap_notification.views import ZapEmail
from django.core.cache import cache
from zap_apps.zap_catalogue.catalogue_common import cache_key_sort, get_similiar_products, sz
from itertools import chain


import math

from zap_apps.zap_notification.tasks import zaplogging
import pdb


class JSONResponse(HttpResponse):

    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

class Browse(ZapView):

    def get(self, request, page_type, format=None):
        data = {}
        if page_type == 'brand-new':
            data.update({'categories': {
                'name': 'Products',
                'items':[{'name': c.name, 'target': 'category?i_shop=brand-new&i_category=' + unicode(c.id),
                                         'image': settings.DOMAIN_NAME + '/zapmedia/' + str(c.mobile_cover)} for c in C.objects.all().order_by('id')[:8]],
                'list_link': 'catalogue/lists/category/shop/brand-new',
                'target': '?i_shop=brand-new'
            }})
            indianBrands = B.objects.annotate(product_count=Count('brand_account__approved_product')).filter(designer_brand=True, brand_account__isnull=False, product_count__gt=0).order_by('-product_count')[:8]
            internationalBrands = B.objects.annotate(product_count=Count('brand_account__approved_product')).filter(designer_brand=False, brand_account__isnull=False, product_count__gt=0).order_by('-product_count')[:8]
            data.update({'brands1': {
                'name': 'International Brands',
                'items': [{'name': c.brand, 'target': 'brand?i_shop=brand-new&i_brand=' + unicode(c.id),
                           'image': str(c.clearbit_logo)} for c in internationalBrands],
                'list_link': 'catalogue/lists/brand/shop/brand',
                'target': '?i_shop=brand'
            }})
            data.update({'brands2': {
                'name': 'Indian Brands',
                'items': [{'name': c.brand, 'target': 'brand?i_shop=brand-new&i_brand=' + unicode(c.id),
                                         'image': str(c.clearbit_logo)} for c in indianBrands],
                'list_link': 'catalogue/lists/brand/shop/designer',
                'target': '?i_shop=designer'
            }})
            feed = Homefeed.objects.filter(active=True, start_time__lte=timezone.now(), end_time__gte=timezone.now(),
                                           platform__in=[0, 1], show_in__slug='brand-new').order_by('-importance')
            if feed:
                srlzr = HomefeedSerializer(feed, many=True, context={'current_user_id': request.user.id or 0})
                data.update({'collections': {
                    'name': 'Collections',
                    'items': srlzr.data
                }})
        elif page_type == 'pre-loved':
            data.update({'categories': {
                'name': 'Products',
                'items': [{'name': c.name, 'target': 'category?i_shop=pre-loved&i_category=' + unicode(c.id),
                                         'image': settings.DOMAIN_NAME + '/zapmedia/' + str(c.mobile_cover)} for c in C.objects.all().order_by('id')[:8]],
                'list_link': 'catalogue/lists/category/shop/pre-loved',
                'target': '?i_shop=pre-loved'
            }})
            # marketBrands = B.objects.filter(approvedproduct__user__user_type__name__in=['zap_user', 'zap_dummy', 'store_front']).exclude(id=132).distinct().annotate(c=Count('approvedproduct')).order_by('-c')[0:8]
            # curatedBrands = B.objects.filter(approvedproduct__user__user_type__name__in=['zap_exclusive']).exclude(id=132).distinct().annotate(c=Count('approvedproduct')).order_by('-c')[0:8]
            # data.update({'brands1': {
            #     'name': 'Luxury Brands',
            #     'list': [{'name': c.brand, 'target': '/brand?i_shop=pre-loved&i_brand=' + unicode(c.id),
            #                           'image': '/zapmedia/' + str(c.clearbit_logo)} for c in curatedBrands]
            # }})
            # data.update({'brands2': {
            #     'name': 'Premium Brands',
            #     'list': [{'name': c.brand, 'target': '/brand?i_shop=pre-loved&i_brand=' + unicode(c.id),
            #                           'image': '/zapmedia/' + str(c.clearbit_logo)} for c in marketBrands]
            # }})
            feed = Homefeed.objects.filter(active=True, start_time__lte=timezone.now(), end_time__gte=timezone.now(),
                                           platform__in=[0, 1], show_in__slug='pre-loved').order_by('-importance')
            if feed:
                srlzr = HomefeedSerializer(feed, many=True, context={'current_user_id': request.user.id or 0})
                data.update({'collections': {
                    'name': 'Collections',
                    'items': srlzr.data
                }})
        elif page_type == 'events':
            feed = Homefeed.objects.filter(active=True, start_time__lte=timezone.now(), end_time__gte=timezone.now(),
                                           platform__in=[0, 1], show_in__slug='events').order_by('-importance')
            if feed:
                srlzr = HomefeedSerializer(feed, many=True, context={'current_user_id': request.user.id or 0})
                data.update({'collections': {
                    'name': 'Collections',
                    'items': srlzr.data
                }})
        return self.send_response(1, data)

class List(ZapView):
    def get(self, request, list_type, filter=None, value=None, format=None):
        filter_in_target = ''
        filter_query = Q()
        if list_type == 'brand':
            if filter:
                if filter == 'shop':
                    if value == 'brand':
                        if request.PLATFORM == 'IOS':
                            filter_query = Q(brand_account__isnull=False, designer_brand=True)
                            filter_in_target = '&i_shop=designer'
                        else:
                            filter_query = Q(brand_account__isnull=False, designer_brand=False)
                    elif value == 'designer':
                        if request.PLATFORM == 'IOS':
                            filter_query = Q(brand_account__isnull=False, designer_brand=False)
                            filter_in_target = '&i_shop=brand'
                        else:
                            filter_query = Q(brand_account__isnull=False, designer_brand=True)
                    elif value == 'brand-new':
                        filter_query = Q(brand_account__isnull=False)
                    elif value == 'pre-loved':
                        filter_query = Q(approvedproduct__user__representing_brand__isnull=True)
                    if not request.PLATFORM == 'IOS':
                        filter_in_target = '&i_shop=' + value
            brands = B.objects.filter(filter_query).distinct().order_by('brand')
            data = []
            for brand in brands:
                data.extend([{'name':brand.brand, 'target':'brand?i_brand=' + brand.slug + filter_in_target}])
        elif list_type == 'category':
            filter_query = Q()
            if filter:
                if filter == 'shop':
                    if value == 'brand-new':
                        filter_query = Q(approvedproduct__user__representing_brand__isnull=False)
                    elif value == 'pre-loved':
                        filter_query = Q(approvedproduct__user__representing_brand__isnull=True)
                    filter_in_target = '&i_shop=' + value
            subcategorys = SubCategory.objects.annotate(count=Count('approvedproduct')).filter(filter_query).distinct().order_by('-count')
            category_items = []
            categorys = {}
            for subcategory in subcategorys:
                try:
                    categorys[subcategory.parent.slug].append({'name': subcategory.name, 'target':'sub-category?i_product_category=' + subcategory.slug + filter_in_target})
                except:
                    categorys[subcategory.parent.slug] = [{'name': subcategory.name, 'target':'sub-category?i_product_category=' + subcategory.slug + filter_in_target}]
            for key in categorys:
                category = C.objects.get(slug=key)
                category_items.append({'name': category.name, 'target':'category?i_category=' + category.slug + filter_in_target, 'subcategorys': categorys[key]})
            data = category_items
        return self.send_response(1, data)

class ProductView(ZapView):

    """
    Landing page\n
    Gives a page by page listing of products. Number of products per page can be specified - default 30\n

    **Context**

        ``data``
            An instance of :model:`zap_catalogue.ApprovedProduct`.

    **Template**
        :template: `frontend/buy.html`

    """

    def get(self, request, page, format=None):
        # pdb.set_trace()
        cache_key = request.get_full_path(
        )+"_{}".format((request.user.id if request.user.is_authenticated() else ""))
        result = cache.get(cache_key)
        if not result:

            q = request.GET.get('q')
            products = ApprovedProduct.ap_objects.filter(Q(title__icontains=q) | Q(description__icontains=q)).filter(sale=2) if \
                q and q != "undefined" else ApprovedProduct.ap_objects.filter(sale=2)
            current_page = request.GET.get('page', 1)
            # track_feed_impressions(products, current_page, request)
            perpage = request.GET.get('perpage', settings.CATALOGUE_PERPAGE)
            # perpage = settings.CATALOGUE_PERPAGE
            paginator = Paginator(products, perpage)
            pr = paginator.page(current_page)
            srlzr = ApprovedProductSerializer(pr, many=True,
                                              context={'logged_user': request.user})
            data = {'data': srlzr.data, 'page': current_page, 'total_pages': paginator.num_pages,
                    'next': pr.has_next(), 'previous': pr.has_previous()}
            track_feed_impressions(srlzr.data, current_page, request)
            result = data
            cache.set(cache_key, result)
        return self.send_response(1, result)


class AnProductView(ZapView):

    """
    Landing page for Android App \n
    Gives a page by page listing of products. Number of products per page can be specified - default 30\n

    **Context**

    ``data``
        An instance of :model:`zap_catalogue.ApprovedProduct`.


    """
    def get(self, request, page, format=None):
        cache_key = request.get_full_path(
        )+"_{}".format((request.user.id if request.user.is_authenticated() else ""))
        result = cache.get(cache_key)
        if not result:
            products = ApprovedProduct.ap_objects.all()
            current_page = request.GET.get('page', 1)
            # track_feed_impressions(products, current_page, request)
            perpage = request.GET.get('perpage', settings.CATALOGUE_PERPAGE)
            paginator = Paginator(products, perpage)
            if page:
                page = int(page)
            if not paginator.num_pages >= page or page == 0:
                data = {
                    'data': [],
                    'page': current_page,
                    'total_pages': paginator.num_pages,
                    'next': True if page == 0 else False,
                    'previous': False if page == 0 else True}
                return self.send_response(1, data)
            p = paginator.page(page)
            srlzr = ApprovedProductSerializerAndroid(p, many=True,
                                                     context={'logged_user': request.user})
            data = {'data': srlzr.data, 'page': current_page, 'total_pages': paginator.num_pages,
                    'next': p.has_next(), 'previous': p.has_previous()}
            track_feed_impressions(srlzr.data, current_page, request)
            result = data
            cache.set(cache_key, result)
        return self.send_response(1, result)


class GetOffers(ZapView):

    def get(self, request, product_id, format=None):
        try:
            product = ApprovedProduct.objects.get(id=product_id)
            if request.user.is_authenticated():
                offers_data = product.get_offers(user_id=request.user.id)
            else:
                offers_data = product.get_offers()
            return self.send_response(1, offers_data)
        except Exception:
            return self.send_response(0, 'Cannot find a product with the ID')


class SellerView(ZapView):

    """

    """

    def get(self, request, page, format=None):
        cache_key = request.get_full_path(
        )+"_{}".format((request.user.id if request.user.is_authenticated() else ""))
        result = cache.get(cache_key)
        if not result:
            zuser = ZapUser.objects.annotate(num_products=Count(
                'approved_product')).filter(num_products__gt=0)
            current_page = request.GET.get('page', 1)
            perpage = request.GET.get(
                'perpage', settings.SELLERVIEW_PAGE_LINE_COUNT)
            # perpage = SELLERVIEW_PAGE_LINE_COUNT
            paginator = Paginator(zuser, perpage)
            p = paginator.page(current_page)
            srlzr = ZapUserProductsSerializer(p, many=True,
                                              context={'current_user': request.user})
            data = {'data': srlzr.data, 'page': current_page, 'total_pages': paginator.num_pages,
                    'next': p.has_next(), 'previous': p.has_previous()}
            result = data
            cache.set(cache_key, result)
        return self.send_response(1, result)


class ProductCRUD(ZapAuthView):

    """
    CRUD operations on products

    **Context**

    ``states``
        From :model: `address.State`

    ``categories``
        From :model: `zap_catalogue.Category`

    ``subc``
        From :model; `zap_catalogue.SubCategory`

    ``global_size``
        From :model: `zap_catalogue.Size`
    """

    def get(self, request, format=None):
        cache_key = request.get_full_path(
        )+"_{}".format((request.user.id if request.user.is_authenticated() else ""))
        result = cache.get(cache_key)
        if not result:
            states = State.objects.all()
            states_srlzr = StateSerializer(states, many=True)
            categories = C.objects.all()
            categories_srlzr = GetCategorySerializer(categories, many=True)
            subc = SubCategory.objects.all()
            subcat_srlzr = SubCategorySerializer(subc, many=True)
            global_size = Size.objects.all().exclude(category_type="FS")
            global_size_srlzr = SizeSerializer(global_size, many=True)
            brand_list = B.objects.all().order_by('brand')
            brand_srlzr = BrandSerializer(brand_list, many=True)
            occasion = O.objects.all()
            occasion_srlzr = OccasionSerializer(occasion, many=True)
            color = Color.objects.all()
            color_srlzr = ColorSerializer(color, many=True)
            styles = S.objects.all()
            style_srlzr = StyleSerializer(styles, many=True)
            data = {'brands': brand_srlzr.data,
                    'fashion_types': style_srlzr.data,
                    'category': categories_srlzr.data,
                    'global_product_list': global_size_srlzr.data,
                    'sub_category': subcat_srlzr.data,
                    'occasion': occasion_srlzr.data,
                    'color': color_srlzr.data,
                    'states': states_srlzr.data}
            result = data
            cache.set(cache_key, result)
        return self.send_response(1, result)

    def post(self, request, format=None):
        data = request.data.copy()
        print data
        data['user'] = request.user.id
        image_list = request.data['images']
        img_ids = []
        for i in image_list:
            if not i['img_url']:
                continue
            img_serializer = ProductImageSerializer(
                data={'image': i['img_url']})
            if img_serializer.is_valid():
                img_serializer.save()
                img_ids.append(img_serializer.data['id'])
            else:
                print img_serializer.errors
                return Response({'status': 'error', 'detail': img_serializer.errors})
        data['images'] = img_ids
        if 'original_price' in data:
            data['discount'] = (float(request.data['original_price']) - float(
                request.data['listing_price'])) / float(request.data['original_price'])
        if data.get('global_size') == "Free Size":
            data['size_type'] = 'FREESIZE'
        data['completed'] = True
        serlzr = ZapProductSerializer(data=data)
        #serlzr = ProductsToApproveSerializer(data=data)
        if serlzr.is_valid():
            words = re.findall('#\S', data['description'])
            if words:
                for i in words:
                    Hashtag.objects.get_or_create(tag=i)
            p_t_a = serlzr.save()
            # data_to_numofproducts = {
            #   'size': Size.objects.get(category_type="FS").id if data.get('global_size')=="Free Size" else data.get('global_size'),
            #   'product_to_approve': p_t_a.id}
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>."
            if data.get('global_size') == "Free Size":
                data_to_numofproducts = {
                    'size': Size.objects.get(category_type="FS").id,
                    'product': p_t_a.id,
                    #'product_to_approve': p_t_a.id,
                    'quantity': data.get('free_quantity', 1)}
                p_t_a_srlzr = NumberOfProductSrlzr(data=data_to_numofproducts)
                if p_t_a_srlzr.is_valid():
                    p_t_a_srlzr.save()
                else:
                    print p_t_a_srlzr.errors
            else:
                for size_selected in request.data['global_size']:
                    size_selected['product'] = p_t_a.id
                    p_t_a_srlzr = NumberOfProductSrlzr(data=size_selected)
                    if p_t_a_srlzr.is_valid():
                        p_t_a_srlzr.save()

            # p_t_a_srlzr = NumberOfProductSrlzr(data=data_to_numofproducts)
            # if not p_t_a_srlzr.is_valid():
            #   return self.send_response(0, srlzr.errors)
            # p_t_a_srlzr.save()

            zapemail = ZapEmail()
            internal_html = settings.UPLOAD_ALBUM_INTERNAL_HTML
            html = settings.UPLOAD_ALBUM_HTML
            # import pdb; #######pdb.set_trace()
            internal_email_vars = {
                'user': request.user.get_full_name(),
                'type': p_t_a.get_sale_display(),
                'album_name': p_t_a.title
            }

            internal_html_body = render_to_string(
                internal_html['html'], internal_email_vars)

            zapemail.send_email_alternative(internal_html[
                'subject'], settings.FROM_EMAIL, "zapyle@googlegroups.com", internal_html_body)

            # zapemail.send_email(internal_html['html'], internal_html[
            # 'subject'], email_vars, settings.FROM_EMAIL, "zapyle@googlegroups.com")
            email_vars = {
                'user': request.user.get_full_name()
            }

            html_body = render_to_string(
                html['html'], email_vars)

            zapemail.send_email_alternative(html[
                'subject'], settings.FROM_EMAIL, request.user.email, html_body)
            # zapemail.send_email(html['html'], html[
            #                     'subject'], email_vars, settings.FROM_EMAIL, request.user.email)
            return Response({'status': 'success', 'data': serlzr.data})
        return Response({'status': 'error', 'detail': serlzr.errors})

    # def put(self, request, format=None):
    #   data = request.data
    #   data['user'] = request.user.id
    #   address = Address.objects.get(id=data['address_id'], user=request.user)
    #   srlzr = AddressSerializer(address, data=data)
    #   if srlzr.is_valid():
    #       srlzr.save()
    #       return self.send_response(1, "Address successfully updated")
    #   return self.send_response(0, srlzr.errors)

    # def delete(self, request, format=None):
    #   data = request.data
    #   Address.objects.filter(id=data['address_id'], user=request.user).delete()
    #   return self.send_response(1, "Address successfully deleted")


class GETSizes(ZapView):

    def get(self, request, c_type=None, format=None):
        cache_key = request.get_full_path()
        result = cache.get(cache_key)
        if not result:
            if c_type:
                sizes = Size.objects.filter(category_type=c_type)
            else:
                sizes = Size.objects.all()
            result = sizes.values()
            cache.set(cache_key, result)
        return self.send_response(1, result)


class SingleProduct(ZapView):

    """
    Product page for one product

    User authentication - not required

    **Context**

        ``pk``
            Product key of the product requested

        ``Response``
            Product data and Seller from models `zap_catalogue.ApprovedProduct` and `zapuser.ZapUser`
    """
    def get(self, request, pk, format=None):
        cache_key = request.get_full_path(
        )+"_{}".format((request.user.id if request.user.is_authenticated() else ""))
        result = cache.get(cache_key)
        if not result:
            # pdb.set_trace()
            data = request.GET.copy()
            try:
                product = ApprovedProduct.objects.get(id=pk)
            except ApprovedProduct.DoesNotExist:
                return self.send_response(0, 'product not found.')
            serlzr = SingleApprovedProducSerializer(product,
                                                    context={'current_user': request.user, 'version':data})
            result = serlzr.data

            user = str(
                request.user.id) if request.user.is_authenticated() else "Guest"
            request.PLATFORM = 'WEBSITE'
            track_single_product_endpoints(product, request, user)
            cache.set(cache_key, result)
        return self.send_response(1, result)


class AndroidSingleProduct(ZapView):

    """
    Product page for one product for Android App

    User authentication - not required

    **Context**

        ``pk``
            Product key of the product requested
    """

    def get(self, request, pk, format=None):
        cache_key = request.get_full_path(
        )+"_{}".format((request.user.id if request.user.is_authenticated() else ""))
        result = cache.get(cache_key)
        if not result:
            # if request.GET.get('action') == 'p_t_a':
            #     product = ProductsToApprove.objects.get(id=pk, user=request.user)
            #     serlzr = AndroidSinglePTApproveProductSerializer(product,
            #                                                context={'current_user': request.user, 'request': request})
            # else:
            # pdb.set_trace()
            data = request.GET.copy()
            try:
                product = ApprovedProduct.objects.get(id=pk)
            except ApprovedProduct.DoesNotExist:
                return self.send_response(0, 'product not found')
            serlzr = AndroidSingleApprovedProducSerializer(product,
                                                           context={'current_user': request.user, 'request': request, 'version':data})
            result = serlzr.data
            user = str(
                request.user.id) if request.user.is_authenticated() else "Guest"
            track_single_product_endpoints(product, request, user)

            cache.set(cache_key, result)
        return self.send_response(1, result)


class Comment(ZapAuthView):

    def post(self, request, qk=None, format=None):
        data = request.data
        data['commented_by'] = request.user
        serlzr = CommentSerializer(data=request.data)
        if serlzr.is_valid():
            serlzr.save()
            sdata = serlzr.data
            sdata['profile_pic'] = request.user.profile.profile_pic
            sdata['zap_username'] = request.user.zap_username
            if data.get('web',False):
                for i in ZapUser.objects.filter(zap_username__in=[s.replace('@', '') for s in re.findall('@\w+', sdata['comment'])]):
                    sdata['comment'] = sdata['comment'].replace("@"+i.zap_username, '<a href="{}/profile/{}/{}">@{}</a>'.format(settings.CURRENT_DOMAIN,i.id,i.zap_username,i.zap_username))
                    # sdata['comment'] = 'comment from web'
            return self.send_response(1, sdata)
        else:
            return self.send_response(0, serlzr.errors)

    def delete(self, request, qk, format=None):
        try:
            c = Comments.objects.get(id=qk)
        except Comments.DoesNotExist:
            return self.send_response(0, 'No such comment')
        if c.commented_by == request.user or c.product.user == request.user:
            c.delete()
            return self.send_response(1, 'Comment Successfully deleted')
        return self.send_response(0, 'No permission')


class GetComment(ZapView):

    def get(self, request, format=None):
        data = request.GET.copy()
        srlzr = GetDataCommentSerializer(data=data)
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        comments = Comments.objects.filter(product__id=data['product_id']).order_by('id')
        if data.get('web'):
            comments = GetCommentSerializerWeb(comments, many=True)
        else:
            comments = GetCommentSerializer(comments, many=True)
        title = ApprovedProduct.objects.get(id=data['product_id'])
        return Response({'status': 'success', 'data': comments.data, 'product_title': title.title})
        # return self.send_response(1, comments.data)


class GetLike(ZapView):

    def get(self, request, format=None):
        data = request.GET.copy()
        srlzr = GetDataCommentSerializer(data=data)
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        likes = Loves.objects.filter(product__id=data['product_id'])
        if data.get('web'):
            likes = GetLikeSerializerWeb(likes, many=True, context={'current_user': request.user})
        else:
            likes = GetLikeSerializer(likes, many=True)
        title = ApprovedProduct.objects.get(id=data['product_id'])
        return Response({'status': 'success', 'data': likes.data, 'product_title': title.title})
        # return self.send_response(1, likes.data)


class ZapFashionCalculator(ZapView):

    def get(self, request, format=None):
        if request.GET.get('p_id'):
            # if request.GET.get('action') == 'p_t_a':
            #     p = ProductsToApprove.objects.get(id=request.GET['p_id'])
            # else:
            #
            p = ApprovedProduct.objects.get(id=request.GET['p_id'])
            calculator = {
                0: {0: .2, 1: .3, 2: .4, 3: .6},
                1: {0: .25, 1: .35, 2: .45, 3: .7},
                2: {0: .3, 1: .45, 2: .6, 3: .8},
                3: {0: .35, 1: .5, 2: .7, 3: .85}
            }
            data = {'ages': [{'id': '0', 'name': '0-3 months'},
                             {'id': '1', 'name': '3-6 months'},
                             {'id': '2', 'name': '6-12 months'},
                             {'id': '3', 'name': '1-2 years'}],
                    'conditions': [{'id': '0', 'name': 'New with tags'},
                                   {'id': '1', 'name': 'Mint Condition'},
                                   {'id': '2', 'name': 'Gently loved'},
                                   {'id': '3', 'name': 'Worn out'}]}
            percentage_commission = p.percentage_commission
            return self.send_response(1,
                                      {'calculator': calculator,
                                       'metrics_data': data,
                                       'percentage_commission': percentage_commission})
        data = {'ages': [{'id': '0', 'name': '0-3 months'},
                         {'id': '1', 'name': '3-6 months'},
                         {'id': '2', 'name': '6-12 months'},
                         {'id': '3', 'name': '1-2 years'}],
                'conditions': [{'id': '0', 'name': 'New with tags'},
                               {'id': '1', 'name': 'Mint Condition'},
                               {'id': '2', 'name': 'Gently loved'},
                               {'id': '3', 'name': 'Worn out'}]}
        return self.send_response(1, data)

    def post(self, request, format=None):
        d = {
            0: {0: .2, 1: .3, 2: .4, 3: .6},
            1: {0: .25, 1: .35, 2: .45, 3: .7},
            2: {0: .3, 1: .45, 2: .6, 3: .8},
            3: {0: .35, 1: .5, 2: .7, 3: .85}
        }
        data = request.POST.copy()
        msg = "fashion-calc-{}".format(request.user.id)+str(
            data) if request.user.is_authenticated() else "fashion-calc"+str(data)
        zaplogging.delay(msg) if settings.CELERY_USE else zaplogging(msg)
        try:
            age = request.data['age']
            condition = request.data['condition']
            original_price = request.data['original_price']
        except:
            return self.send_response(0, 'missing age/condition/original_price')
        percent = d[int(age)][int(condition)]
        max_listing_price = float(original_price) - \
            (float(original_price) * float(percent))
        return self.send_response(1, {"max_listing_price": max_listing_price})


class EditProduct(ZapAuthView):

    def get(self, request, pk, format=None):
        cache_key = request.get_full_path(
        )+"_{}".format((request.user.id if request.user.is_authenticated() else ""))
        result = cache.get(cache_key)
        if not result:
            try:
                product = ApprovedProduct.objects.get(id=pk, user=request.user)
            except ApprovedProduct.DoesNotExist:
                pass
            return self.send_response(0, 'no permission')
            if product.user != request.user or product.ordered_product.count() > 0:
                return self.send_response(0, 'no permission')
            serlzr = EditProducSerializer(product,
                                          context={'current_user': request.user})
            result = serlzr.data
            cache.set(cache_key, result)
        return self.send_response(1, result)

    def put(self, request, pk, format=None):
        try:
            product = ApprovedProduct.objects.get(id=pk, user=request.user)
        except ApprovedProduct.DoesNotExist:
            return self.send_response(0, 'no permission')
        if product.user != request.user or product.ordered_product.count() > 0:
            return self.send_response(0, 'no permission')
        data = request.data
        image_list = data['images']
        img_ids = []
        for i in image_list:
            img_serializer = ProductImageSerializer(
                data={'image': i['img_url']})
            if img_serializer.is_valid():
                img_serializer.save()
                img_ids.append(img_serializer.data['id'])
            else:
                Response({'status': 'error', 'detail': img_serializer.errors})
        data['images'] = img_ids + data['old_images']
        print data['old_images'], '---', product.images.all().values_list('id', flat=True)
        srlzr = UpdateApprovedProductSerializer(product, data=data)
        if not srlzr.is_valid():
            print srlzr.errors, 'errors'
        else:
            u_a_p_s = srlzr.save()
        NumberOfProducts.objects.filter(product=product).delete()
        if data.get('global_size') == "Free Size":
            data_to_numofproducts = {
                'size': Size.objects.get(category_type="FS").id,
                'product': product.id,
                'quantity': data.get('free_quantity', 1)}
            p_t_a_srlzr = NumberOfProductSrlzr(data=data_to_numofproducts)
            if p_t_a_srlzr.is_valid():
                p_t_a_srlzr.save()
        else:
            for size_selected in request.data['global_size']:
                size_selected['product'] = product.id
                p_t_a_srlzr = NumberOfProductSrlzr(data=size_selected)
                if p_t_a_srlzr.is_valid():
                    p_t_a_srlzr.save()
                else:
                    print p_t_a_srlzr.errors, '****'
        return self.send_response(1, 'success')

    def delete(self, request, pk, format=None):
        # if request.GET.get('action') == 'p_t_a':
        #     try:
        #         product = ProductsToApprove.objects.get(id=pk, user=request.user)
        #         product.delete()
        #         return self.send_response(1, 'success')
        #     except ProductsToApprove.DoesNotExist:
        #         return self.send_response(0, 'no such product')
        # else:
        try:
            product = ApprovedProduct.objects.get(id=pk, user=request.user)
        except ApprovedProduct.DoesNotExist:
            return self.send_response(0, 'no permission')
        if product.product.count() > 0:
            return self.send_response(0, "This product is sold already.")
        product.status = '3'
        product.save()
        return self.send_response(1, 'success')


class Brand(ZapView):

    def get(self, request, brand_name, page, format=None):
        # import pdb; pdb.set_trace()
        cache_key = request.get_full_path(
        ) + "_{}".format((request.user.id if request.user.is_authenticated() else ""))
        result = cache.get(cache_key)
        result = ''

        size = price = discount = condition = age = color = ''

        try:
            size = request.GET['size']
        except KeyError:
            print "Size Key not their"

        try:
            price = request.GET['price']
        except KeyError:
            print "Price Key not their"

        try:
            discount = request.GET['discount']
        except KeyError:
            print "Discount Key not their"

        try:
            condition = request.GET['condition']
        except KeyError:
            print "Condition Key not their"

        try:
            age = request.GET['age']
        except KeyError:
            print "Age key not their"

        try:
            color = request.GET['color']
        except KeyError:
            print "Color key not their"


        if not result:
            brands = brand_name.split('&')

            products = ApprovedProduct.ap_objects.filter(Q(brand__brand__in=brands)) \
               .annotate(Sum('product_count__quantity')).filter(product_count__quantity__sum__gte=1)

            print brands, ' are the brands requested for'


            always_true = ~Q(pk=None)

            price_q = discount_q = condition_q = age_q = color_q = always_true

            print price

            if price:
                price_min_max = price.split(',')
                low_limit = price_min_max[0]
                up_limit = price_min_max[1]
                price_q = Q(listing_price__gte=low_limit) & Q(listing_price__lte=up_limit)
            if discount:
                discount_codes = {
                    '1': '0.70',
                    '2': '0.50',
                    '3': '0.30',
                    '4': '0.10',
                }
                print discount_codes.get(discount, '0.70'), "Discount"
                discount_q = Q(discount__gte=discount_codes.get(discount, '0.70'))
            if condition:
                condition_q = Q(condition=condition)
            if age:
                age_q = Q(age=age)
            if color:
                color_q = Q(color=color)
            if size:
                product_id_list = []
                all_products = NumberOfProducts.objects.filter(size=size).select_related('product')
                if all_products.count() > 0:
                    for s in all_products:
                        if s.product != None and s.product.id != "":
                            product_id_list.append(s.product.id)
                        else:
                            pass

                    product_sizes = ApprovedProduct.ap_objects.filter(Q(id__in=product_id_list)) \
                         .annotate(Sum('product_count__quantity')).filter(product_count__quantity__sum__gte=1)

                    products = products.filter(price_q & discount_q & condition_q & age_q & color_q) & product_sizes
            else:
                products = products.filter(price_q & discount_q & condition_q & age_q & color_q)

            print products.count(), "Count of products"

            sorted_request_dict = {}
            # args = request.GET.copy()
            # sorted_request_dict = cache_sort(args)
            # # products = getProducts(sorted_request_dict)
            # products.filter(**sorted_request_dict)

            if not products:
                return self.send_response(0, 'product not found')

            # if not 'brand' in sorted_request_dict:
            #     sorted_request_dict['brand'] = brands
            # else:
            #     sorted_request_dict['brand'] += brands

            current_page = page
            # track_attribute_endpoints(sorted_request_dict, products, current_page, request)

            perpage = request.GET.get('perpage', settings.CATALOGUE_PERPAGE)
            paginator = Paginator(products, perpage)
            if page:
                page = int(page)
            if not paginator.num_pages >= page or page == 0:
                data = {
                    'data': [],
                    'page': current_page,
                    'total_pages': paginator.num_pages,
                    'next': True if page == 0 else False,
                    'previous': False if page == 0 else True}
                return self.send_response(1, data)

            p = paginator.page(page)

            srlzr = ApprovedProductSerializer(
                p, many=True,  context={'logged_user': request.user})
            data = {'data': srlzr.data, 'page': current_page, 'total_pages': paginator.num_pages,
                    'next': p.has_next(), 'previous': p.has_previous()}
            track_attribute_endpoints(
                sorted_request_dict, srlzr.data, current_page, request)
            result = data
            cache.set(cache_key, result)
        return self.send_response(1, result)

class FollowBrand(ZapAuthView):
    def get(self, request, brand_id, format=None):
        try:
            user = ZapUser.objects.get(id=request.user.id)
            if str(brand_id).isdigit():
                brand = B.objects.get(id=int(brand_id))
            else:
                brand = B.objects.get(slug=str(brand_id))
            brand.following_users.add(user)
            return self.send_response(1, {'message': 'Sucessfully added follower'})
        except Exception as e:
            return self.send_response(0, {'error': "Couldn't retrieve user or brand"})

    def post(self, request, brand_id, format=None):
        info = request.POST.get('info', '')
        phone=email=None
        if unicode(info).isdigit():
            phone = info
            Q = Q(phone_numer=phone)
        else:
            email = info
            Q = Q(email=email)

        referral_user = referring_user = referral_email = referral_phone = None
        if str(brand_id).isdigit():
            brand = B.objects.get(id=int(brand_id))
        else:
            brand = B.objects.get(slug=str(brand_id))
        try:
            if Lead.objects.filter(Q).count() > 0:
                lead = Lead.objects.filter(Q)[0]
                brand.following_leads.add(lead)
                message = 'Lead added to the Brand'
                return self.send_response(1, {'message': message})
        except Lead.DoesNotExist:
            if email:
                lead_generated = Lead(email=email)
            elif phone:
                lead_generated = Lead(phone_number=email)

            lead_generated.save()

            # Add user to follow in Campaign
            brand.following_leads.add(lead_generated)

            # Check if coresponding zap user exists
            try:
                if phone:
                    zapuser = ZapUser.objects.get(phone_number=phone)
                    brand.following_users.add(zapuser)
                elif email:
                    zapuser = ZapUser.objects.get(email=email)
                    brand.following_users.add(zapuser)
            except ZapUser.DoesNotExist:
                pass


# Serves the page based on product category
class Category(ZapView):

    def get(self, request, category_name, page, format=None):
        cache_key = request.get_full_path(
        ) + "_{}".format((request.user.id if request.user.is_authenticated() else ""))
        result = cache.get(cache_key)
        result = ''

        size = price = discount = condition = age = color = ''

        try:
            size = request.GET['size']
        except KeyError:
            print "Size Key not their"

        try:
            price = request.GET['price']
        except KeyError:
            print "Price Key not their"

        try:
            discount = request.GET['discount']
        except KeyError:
            print "Discount Key not their"

        try:
            condition = request.GET['condition']
        except KeyError:
            print "Condition Key not their"

        try:
            age = request.GET['age']
        except KeyError:
            print "Age key not their"

        try:
            color = request.GET['color']
        except KeyError:
            print "Color key not their"

        if not result:
            categories = category_name.split('&')
            products = ApprovedProduct.ap_objects.filter(product_category__parent__name__in=categories)\
                .annotate(Sum('product_count__quantity')).filter(product_count__quantity__sum__gte=1)

            print categories, ' are the categories requested for'

            always_true = ~Q(pk=None)

            price_q = discount_q = condition_q = age_q = color_q = always_true

            print price

            if price:
                price_min_max = price.split(',')
                low_limit = price_min_max[0]
                up_limit = price_min_max[1]
                price_q = Q(listing_price__gte=low_limit) & Q(listing_price__lte=up_limit)
            if discount:
                discount_codes = {
                    '1': '0.70',
                    '2': '0.50',
                    '3': '0.30',
                    '4': '0.10',
                }
                print discount_codes.get(discount, '0.70'), "Discount"
                discount_q = Q(discount__gte=discount_codes.get(discount, '0.70'))
            if condition:
                condition_q = Q(condition=condition)
            if age:
                age_q = Q(age=age)
            if color:
                color_q = Q(color=color)
            if size:
                product_id_list = []
                all_products = NumberOfProducts.objects.filter(size=size).select_related('product')
                if all_products.count() > 0:
                    for s in all_products:
                        if s.product != None and s.product.id != "":
                            product_id_list.append(s.product.id)
                        else:
                            pass

                    product_sizes = ApprovedProduct.ap_objects.filter(Q(id__in=product_id_list)) \
                        .annotate(Sum('product_count__quantity')).filter(product_count__quantity__sum__gte=1)

                    products = products.filter(price_q & discount_q & condition_q & age_q & color_q) & product_sizes
            else:
                products = products.filter(price_q & discount_q & condition_q & age_q & color_q)

            print products.count(), "Count of products"

            sorted_request_dict = {}
            # args = request.GET.copy()
            # sorted_request_dict = cache_sort(args)
            # # products = getProducts(sorted_request_dict)
            # products.filter(**sorted_request_dict)

            if not products:
                return self.send_response(0, 'product not found')

            # if not 'category' in sorted_request_dict:
            #     sorted_request_dict['category'] = categories
            # else:
            #     sorted_request_dict['category'] += categories

            current_page = page
            perpage = request.GET.get('perpage', settings.CATALOGUE_PERPAGE)
            paginator = Paginator(products, perpage)
            if page:
                page = int(page)
            if not paginator.num_pages >= page or page == 0:
                data = {
                    'data': [],
                    'page': current_page,
                    'total_pages': paginator.num_pages,
                    'next': True if page == 0 else False,
                    'previous': False if page == 0 else True}
                return self.send_response(1, data)

            p = paginator.page(page)

            srlzr = ApprovedProductSerializer(
                p, many=True, context={'logged_user': request.user})
            data = {'data': srlzr.data, 'page': current_page, 'total_pages': paginator.num_pages,
                    'next': p.has_next(), 'previous': p.has_previous()}
            track_attribute_endpoints(
                sorted_request_dict, srlzr.data, current_page, request)
            result = data
            cache.set(cache_key, result)
        return self.send_response(1, result)


class Occasion(ZapView):

    def get(self, request, occasion_name, page, format=None):
        cache_key = request.get_full_path(
        ) + "_{}".format((request.user.id if request.user.is_authenticated() else ""))
        result = cache.get(cache_key)
        result = ''

        size = price = discount = condition = age = color = ''

        try:
            size = request.GET['size']
        except KeyError:
            print "Size Key not their"

        try:
            price = request.GET['price']
        except KeyError:
            print "Price Key not their"

        try:
            discount = request.GET['discount']
        except KeyError:
            print "Discount Key not their"

        try:
            condition = request.GET['condition']
        except KeyError:
            print "Condition Key not their"

        try:
            age = request.GET['age']
        except KeyError:
            print "Age key not their"

        try:
            color = request.GET['color']
        except KeyError:
            print "Color key not their"

        if not result:

            occasions = occasion_name.split('&')
            occasion = O.objects.filter(name__in=occasions).values()
            if not occasion:
                return self.send_response(0, 'occasion not found')
            oid = occasion[0]['id']
            products = ApprovedProduct.ap_objects.filter(occasion_id=oid) \
                .annotate(Sum('product_count__quantity')).filter(product_count__quantity__sum__gte=1)

            print oid, ' are the occassion requested for'

            always_true = ~Q(pk=None)

            price_q = discount_q = condition_q = age_q = color_q = always_true

            print price

            if price:
                price_min_max = price.split(',')
                low_limit = price_min_max[0]
                up_limit = price_min_max[1]
                price_q = Q(listing_price__gte=low_limit) & Q(listing_price__lte=up_limit)
            if discount:
                discount_codes = {
                    '1': '0.70',
                    '2': '0.50',
                    '3': '0.30',
                    '4': '0.10',
                }
                print discount_codes.get(discount, '0.70'), "Discount"
                discount_q = Q(discount__gte=discount_codes.get(discount, '0.70'))
            if condition:
                condition_q = Q(condition=condition)
            if age:
                age_q = Q(age=age)
            if color:
                color_q = Q(color=color)
            if size:
                product_id_list = []
                all_products = NumberOfProducts.objects.filter(size=size).select_related('product')
                if all_products.count() > 0:
                    for s in all_products:
                        if s.product != None and s.product.id != "":
                            product_id_list.append(s.product.id)
                        else:
                            pass

                    product_sizes = ApprovedProduct.ap_objects.filter(Q(id__in=product_id_list)) \
                        .annotate(Sum('product_count__quantity')).filter(product_count__quantity__sum__gte=1)

                    products = products.filter(price_q & discount_q & condition_q & age_q & color_q) & product_sizes
            else:
                products = products.filter(price_q & discount_q & condition_q & age_q & color_q)

            print products.count(), "Count of products"


            sorted_request_dict = {}
            # args = request.GET.copy()
            # sorted_request_dict = cache_sort(args)
            # # products = getProducts(sorted_request_dict)
            # products.filter(**sorted_request_dict)

            if not products:
                return self.send_response(0, 'product not found')

            # if not 'occasion' in sorted_request_dict:
            #     sorted_request_dict['occasion'] = occasions
            # else:
            #     sorted_request_dict['occasion'] += occasions

            current_page = page
            # track_attribute_endpoints(sorted_request_dict, products, current_page, request)

            perpage = request.GET.get('perpage', settings.CATALOGUE_PERPAGE)
            paginator = Paginator(products, perpage)
            if page:
                page = int(page)
            if not paginator.num_pages >= page or page == 0:
                data = {
                    'data': [],
                    'page': current_page,
                    'total_pages': paginator.num_pages,
                    'next': True if page == 0 else False,
                    'previous': False if page == 0 else True}
                return self.send_response(1, data)

            p = paginator.page(page)

            srlzr = ApprovedProductSerializer(
                p, many=True, context={'logged_user': request.user})
            data = {'data': srlzr.data, 'page': current_page, 'total_pages': paginator.num_pages,
                    'next': p.has_next(), 'previous': p.has_previous()}
            track_attribute_endpoints(
                sorted_request_dict, srlzr.data, current_page, request)
            result = data
            cache.set(cache_key, result)
        return self.send_response(1, result)


class Style(ZapView):

    def get(self, request, style_name, page, format=None):
        cache_key = request.get_full_path(
        ) + "_{}".format((request.user.id if request.user.is_authenticated() else ""))
        result = cache.get(cache_key)
        result = ''

        size = price = discount = condition = age = color = ''

        try:
            size = request.GET['size']
        except KeyError:
            print "Size Key not their"

        try:
            price = request.GET['price']
        except KeyError:
            print "Price Key not their"

        try:
            discount = request.GET['discount']
        except KeyError:
            print "Discount Key not their"

        try:
            condition = request.GET['condition']
        except KeyError:
            print "Condition Key not their"

        try:
            age = request.GET['age']
        except KeyError:
            print "Age key not their"

        try:
            color = request.GET['color']
        except KeyError:
            print "Color key not their"

        if not result:
            style = S.objects.filter(style_type=style_name.title()).values()
            if not style:
                return self.send_response(0, 'style not found')
            sid = style[0]['id']
            products = ApprovedProduct.ap_objects.filter(style_id=sid) \
                .annotate(Sum('product_count__quantity')).filter(product_count__quantity__sum__gte=1)

            print sid, ' are the styles requested for'

            always_true = ~Q(pk=None)

            price_q = discount_q = condition_q = age_q = color_q = always_true

            print price

            if price:
                price_min_max = price.split(',')
                low_limit = price_min_max[0]
                up_limit = price_min_max[1]
                price_q = Q(listing_price__gte=low_limit) & Q(listing_price__lte=up_limit)
            if discount:
                discount_codes = {
                    '1': '0.70',
                    '2': '0.50',
                    '3': '0.30',
                    '4': '0.10',
                }
                print discount_codes.get(discount, '0.70'), "Discount"
                discount_q = Q(discount__gte=discount_codes.get(discount, '0.70'))
            if condition:
                condition_q = Q(condition=condition)
            if age:
                age_q = Q(age=age)
            if color:
                color_q = Q(color=color)
            if size:
                product_id_list = []
                all_products = NumberOfProducts.objects.filter(size=size).select_related('product')
                if all_products.count() > 0:
                    for s in all_products:
                        if s.product != None and s.product.id != "":
                            product_id_list.append(s.product.id)
                        else:
                            pass

                    product_sizes = ApprovedProduct.ap_objects.filter(Q(id__in=product_id_list)) \
                        .annotate(Sum('product_count__quantity')).filter(product_count__quantity__sum__gte=1)

                    products = products.filter(price_q & discount_q & condition_q & age_q & color_q) & product_sizes
            else:
                products = products.filter(price_q & discount_q & condition_q & age_q & color_q)

            print products.count(), "Count of products"

            sorted_request_dict = {}

            # args = request.GET.copy()
            # sorted_request_dict = cache_sort(args)
            # # products = getProducts(sorted_request_dict)
            # products.filter(**sorted_request_dict)

            if not products:
                return self.send_response(0, 'product not found')

            # if not 'style' in sorted_request_dict:
            #     sorted_request_dict['style'] = [style_name.title()]
            # else:
            #     sorted_request_dict['style'] += [style_name.title()]

            current_page = page
            # track_attribute_endpoints(sorted_request_dict, products, current_page, request)

            perpage = request.GET.get('perpage', settings.CATALOGUE_PERPAGE)
            paginator = Paginator(products, perpage)
            if page:
                page = int(page)
            if not paginator.num_pages >= page or page == 0:
                data = {
                    'data': [],
                    'page': current_page,
                    'total_pages': paginator.num_pages,
                    'next': True if page == 0 else False,
                    'previous': False if page == 0 else True}
                return self.send_response(1, data)

            p = paginator.page(page)

            srlzr = ApprovedProductSerializer(
                p, many=True, context={'logged_user': request.user})
            data = {'data': srlzr.data, 'page': current_page, 'total_pages': paginator.num_pages,
                    'next': p.has_next(), 'previous': p.has_previous()}
            track_attribute_endpoints(
                sorted_request_dict, srlzr.data, current_page, request)
            result = data
            cache.set(cache_key, result)
        return self.send_response(1, result)


def get_filter_data(sorted_request_dict, platform, user):
    user_price_list = [
    ] if not 'user_price' in sorted_request_dict else sorted_request_dict['user_price']
    selected_price_list = [
    ] if not 'selected_price' in sorted_request_dict else sorted_request_dict['selected_price']
    price_list = user_price_list + selected_price_list
    filter_data = {
        'category': [] if not 'category' in sorted_request_dict else [C.objects.get(name=category_name).id for
                                                                      category_name in sorted_request_dict['category']],
        'subcategory': [] if not 'subcategory' in sorted_request_dict else [
            SubCategory.objects.get(name=subcategory_name).id for subcategory_name in
            sorted_request_dict['subcategory']],
        'color': [] if not 'subcategory' in sorted_request_dict else [C.objects.get(name=color_name).id for color_name in sorted_request_dict['color']],
        'brand': [] if not 'brand' in sorted_request_dict else [B.objects.get(brand=brand_name).id for brand_name in sorted_request_dict['brand']],
        'occasion': [] if not 'occasion' in sorted_request_dict else [O.objects.get(name=occasion_name).id for occasion_name in sorted_request_dict['occasion']],
        'style': [] if not 'style' in sorted_request_dict else [S.objects.get(style_type=style_type).id for style_type in sorted_request_dict['style']],
        'size': [] if not 'size' in sorted_request_dict else [Size.objects.get(size=size).id for size in sorted_request_dict['size']],
        'price': [Int4NumericRange(price[0], price[1]) for price in price_list],
        'platform': platform,
        'user': user.id,
    }
    return filter_data


def track_feed_impressions(products, current_page, request):
    if request.PLATFORM is None:
        print('Cannot track impressions on feed! Platform not defined!')
        return
    platform = request.PLATFORM
    if settings.CELERY_USE:
        track_impressions.delay(
            [product['id'] for product in products], current_page, platform, 'B', request.user)
    else:
        track_impressions(
            [product['id'] for product in products], current_page, platform, 'B', request.user)


def track_attribute_endpoints(sorted_request_dict, products, current_page, request):
    if request.PLATFORM is None:
        print(
            'Cannot track impressions on filtered feed! Platform not defined!')
        return
    platform = request.PLATFORM
    filter_data = get_filter_data(sorted_request_dict, platform, request.user)
    if settings.CELERY_USE:
        track_filter.delay(filter_data)
        track_impressions.delay(
            [product['id'] for product in products], current_page, platform, 'F', request.user)
    else:
        track_filter(filter_data)
        track_impressions(
            [product['id'] for product in products], current_page, platform, 'F', request.user)


def track_single_product_endpoints(product, request, user):
    if request.PLATFORM is None:
        print('Cannot track product! Platform not defined!')
        return
    platform = request.PLATFORM
    product_data = {
        'product': product.id,
        'platform': platform,
        'user': user,
    }
    if settings.CELERY_USE:
        track_product.delay(product_data)
    else:
        track_product(product_data)

class UserSearch(ZapView):
    def get(self, request, q):
        users = ZapUser.objects.filter(zap_username__istartswith=q,profile__isnull=False)[0:4]
        data = [{'profile_pic' : u.profile.profile_pic, 'zap_username':u.zap_username} for u in users]
        return self.send_response(1, data)
import ast
class SchedulePickup(ZapView):
    def post(self, request):
        data = request.data
        d = data.get('data')
        if not 'product_category' in d:
            return self.send_response(0, 'Select a Category.')
        if not 'age' in d:
            return self.send_response(0, 'Select an Age.')
        if not 'brand' in d:
            return self.send_response(0, 'Select a Brand.')
        if not 'condition' in d:
            return self.send_response(0, 'Select a Condition.')
        if not 'name' in d:
            return self.send_response(0, 'Enter your Name.')
        if not 'phone' in d:
            return self.send_response(0, 'Enter your Phone Number.')
        if not request.FILES:
            return self.send_response(0, 'Upload Image.')
        images = [ZapCuratedEntryImages.objects.create(image = img) for img in request.FILES]
        d = ast.literal_eval(d)
        d['images'] = [i.id for i in images]
        srlzr = ZapCuratedEntrySerializer(data = d)
        if srlzr.is_valid():
            srlzr.save()
        else:
            return self.send_response(0, srlzr.errors)
        return self.send_response(1, 'success')

class WebFilterItems(ZapView):
    def get(self, request):
        params = request.GET.copy()
        data = {}
        if(params.get('catalogue')):
            data['catalogues'] = [{'title': c.name, 'sub_cats':[{'title':s.name,'id':s.id} for s in SubCategory.objects.filter(parent=c)]} for c in C.objects.all()]
        if(params.get('brand')):
            data['brands'] = [{'title':b.brand,'id':b.id} for b in B.objects.order_by('brand')]
        return self.send_response(1, data)

class SimilarProducts(ZapView):

    def get(self, request, page, format=None):
        sorted_data = cache_key_sort(request.GET.copy())
        products = get_similiar_products(sorted_data)
        # pdb.set_trace()
        current_page = page or 1
        perpage = request.GET.get('perpage', settings.CATALOGUE_PERPAGE)
        # perpage = settings.CATALOGUE_PERPAGE
        paginator = Paginator(products, perpage)
        p = paginator.page(current_page)
        # track_filtered_feed(sorted_request_dict, request, products, current_page)
        srlzr = ApprovedProductSerializer(p, many=True,
                                          context={'logged_user': request.user})
        resp = {'data': srlzr.data, 'page': current_page, 'total_pages': paginator.num_pages,
                'next': p.has_next(), 'previous': p.has_previous()}

        # cache.set(cache_key, result)
        return self.send_response(1, resp)


class SimilarProductsWithProducts(ZapView):

    def get(self, request, format=None):
        # pdb.set_trace()
        data = request.GET.copy()
        product = ApprovedProduct.ap_objects.get(id=data['pro'])
        # exclude_list = []
        # Q_exclude = Q(sum_count__lte=0) or Q(pk=product.id)
        # Q_size = Q()
        # removal_list = ['brand', 'style', 'occasion', 'age',
        #                 'listing_price__range', 'user__user_type__name', 'size__in']

        filter_kwargs = {'brand': product.brand,
                         'style': product.style,
                         'occasion': product.occasion,
                         'age': product.age,
                         'condition': product.condition,
                         'listing_price__range': range(int(math.ceil(product.listing_price-(product.listing_price*0.1))),
                                                                                                      int(math.floor(product.listing_price + (product.listing_price*0.1)))),
                         'size__in': product.size.all(), 'color': product.color,
                         'product_category': product.product_category,
                         'user_type': product.user.user_type.name}

        # -----------------------------------------------------------

        """
        To find similar products, we assign a score of 1 to each of the parameters of the product.
        _________________________________
        Parameter               Score
        Brand                   1
        Style                   1
        Occasion                1
        Age                     1
        listing_price__range    1
        user__user_type__name   1
        size__in                1

        If any of the parameters matches to the original product score, score is 1 else 0
        Total score of the products is sum of all the above score.
        Sort all the products based on this score
        """

        products = ApprovedProduct.ap_objects.filter(product_category=filter_kwargs['product_category'])

        similar_products = {}

        for p in products:
            product_score = 0
            product_id = p.id
            if p.brand == filter_kwargs['brand']:
                product_score += 1
            if p.style == filter_kwargs['style']:
                product_score += 1
            if p.occasion == filter_kwargs['occasion']:
                product_score += 1
            if p.age == filter_kwargs['age']:
                product_score += 1
            if p.condition == filter_kwargs['condition']:
                product_score += 1
            if p.listing_price in filter_kwargs['listing_price__range']:
                product_score += 1
            if p.user.user_type.name == filter_kwargs['user_type']:
                product_score += 1
            if p.size.all() in filter_kwargs['size__in']:
                product_score += 1

            similar_products[product_id] = product_score

        # Sort the dictionary based on scores of every product id
        product_id_list = []
        import operator
        sorted_product_ids = sorted(similar_products.items(), key=operator.itemgetter(1))

        number_of_products = len(sorted_product_ids)

        i = 0
        while i < number_of_products:
            product_id_list.append(sorted_product_ids[i][0])
            i += 1

        all_products = ApprovedProduct.ap_objects.filter(pk__in=product_id_list).exclude(pk=product.id)
        srlzr = ApprovedProductSerializer(list(all_products), many=True,
                                          context={'logged_user': request.user})

        return self.send_response(1, srlzr.data)

        # --------------------------------------------------------------------------
        #
        # if product.user.user_type.name == 'zap_exclusive':
        #     filter_kwargs.update({'user__user_type__name': 'zap_exclusive'})
        # else:
        #     exclude_list = [Q(user__user_type__name='zap_exclusive')]
        #     Q_exclude |= Q(user__user_type__name='zap_exclusive')
        #
        # # get Products matching the exact criteria
        # result = ApprovedProduct.ap_objects.annotate(sum_count= Sum('product_count__quantity')).filter(
        #     Q(**filter_kwargs)).exclude(Q_exclude)
        #
        # for attr in removal_list:
        #     # pdb.set_trace()
        #     if attr not in ['age', 'size__in']:
        #         try:
        #             attr_value = filter_kwargs.pop(attr)
        #             exclude_list.append(Q(**{attr: attr_value}))
        #             Q_exclude |= Q(**{attr: attr_value})
        #         except KeyError:
        #             exclude_list.pop(0)
        #             Q_exclude = Q()
        #             for item in exclude_list:
        #                 Q_exclude |= item
        #             filter_kwargs.update(
        #                 {'user__user_type__name': 'zap_exclusive'})
        #     elif attr == 'age':
        #         age_val = filter_kwargs.pop('age')
        #         cond_val = filter_kwargs.pop('condition')
        #         exclude_list.append(Q(age=product.age))
        #         Q_exclude |= Q(age=product.age)
        #         exclude_list.append(Q(condition=product.condition))
        #         Q_exclude |= Q(condition=product.condition)
        #     else:
        #         attr_val = filter_kwargs.pop(attr)
        #         for size in attr_val:
        #             Q_size &= sz({'sz': size.id})
        #     new_result = ApprovedProduct.ap_objects.annotate(sum_count= Sum('product_count__quantity')).filter(
        #         Q(**filter_kwargs) & Q_size).exclude(Q_exclude).distinct()
        #
        #     result = list(chain(result, new_result))
        #
        # # current_page = page or 1
        # # perpage = request.GET.get('perpage', settings.CATALOGUE_PERPAGE)
        # # # perpage = settings.CATALOGUE_PERPAGE
        # # paginator = Paginator(result, perpage)
        # # p = paginator.page(current_page)
        # # track_filtered_feed(sorted_request_dict, request, products, current_page)
        # srlzr = ApprovedProductSerializer(result, many=True,
        #                                   context={'logged_user': request.user})
        # # resp = {'data': srlzr.data, 'page': current_page, 'total_pages': paginator.num_pages,
        # # 'next': p.has_next(), 'previous': p.has_previous()}
        #
        # # cache.set(cache_key, result)
        # return self.send_response(1, srlzr.data)


class GetProductSizes(ZapView):
    def get(self, request, format=None):
        try:
            obj = ApprovedProduct.objects.get(id=request.GET.get('product_id'))
            size_type = obj.size_type or (
                "UK" if obj.product_category.parent.category_type == 'C' else
                "US" if obj.product_category.parent.category_type == 'FW' else "FREESIZE")
            if size_type == 'UK':
                data = [{'size':size_type+s.uk_size, 'qty':obj.product_count.get(size=s).quantity, 'id':s.id} for s in obj.size.all().extra(select={'i':'CAST(uk_size AS FLOAT)'}).order_by('i')]# if obj.product_count.get(size=s).quantity>0]
            elif size_type == 'US':
                data = [{'size':size_type+s.us_size, 'qty':obj.product_count.get(size=s).quantity, 'id':s.id} for s in obj.size.all().extra(select={'i':'CAST(uk_size AS FLOAT)'}).order_by('i')]# if obj.product_count.get(size=s).quantity>0]
            elif size_type == 'EU':
                data = [{'size':size_type+s.eu_size, 'qty':obj.product_count.get(size=s).quantity, 'id':s.id} for s in obj.size.all().extra(select={'i':'CAST(uk_size AS FLOAT)'}).order_by('i')]# if obj.product_count.get(size=s).quantity>0]
            else:
                data = [{'size':'FREESIZE','qty':obj.product_count.get(size=s).quantity, 'id':s.id} for s in obj.size.all().extra(select={'i':'CAST(uk_size AS FLOAT)'}).order_by('i') if obj.product_count.get(size=s).quantity>0]
            return self.send_response(1, data)
        except:
            return self.send_response(0, 'invalid product id')


class SellerClosetView(ZapView):
    def get(self, request, page, format=None):
        from zap_apps.zapuser.models import USER_TYPES
        data = request.GET.copy()
        Q_obj = Q(approved_product__status='1')
        user_types_dict = dict(USER_TYPES)
        Q_obj &= Q(
            **{'user_type__name__in': user_types_dict.get(data['closet'], [])})
        if data['closet'] == 'designer':
            Q_obj &= Q(representing_brand__designer_brand=True)
        elif data['closet'] == 'brand':
            Q_obj &= Q(representing_brand__designer_brand=False)
        users = ZapUser.objects.annotate(
            l_count=Count('approved_product')).filter(Q_obj).filter(l_count__gte=3).order_by('-l_count')

        perpage = request.GET.get('perpage', settings.SELLER_CLOSET_PERPAGE)
        paginator = Paginator(users, perpage)
        p = paginator.page(page)
        srlzr = SellerClosetViewSerializer(
            p, many=True, context={'current_user_id': request.user.id or 0})
        result = {'data': srlzr.data, 'page': page, 'total_pages': paginator.num_pages,
                  'next': p.has_next(), 'previous': p.has_previous()}
        return self.send_response(1, result)
from random import randint


class Header(ZapView):

    def get(self, request):
        international_categories = []
        for c in C.objects.filter(subcategory__approvedproduct__status='1',
                                  subcategory__approvedproduct__user__user_type__name__in=['designer'],
                                  subcategory__approvedproduct__user__representing_brand__designer_brand=False).annotate(c=Count('subcategory__approvedproduct')).order_by('-c'):
            international_categories.append({'name': c.name, 'url': '/shop/brand/category/{}/'.format(c.slug), 'parent': True})
            for sc in SC.objects.annotate(count=Count('approvedproduct')).filter(parent__id=c.id, approvedproduct__status='1',
                        approvedproduct__user__user_type__name__in=['designer'],
                        approvedproduct__user__representing_brand__designer_brand=False,
                        count__gt=0).order_by('-count'):
                international_categories.append({'name': sc.name, 'url': '/shop/brand/sub-category/{}/'.format(sc.slug), 'parent': False})
        if len(international_categories) > 36:
            international_categories = international_categories[0:35]
        designer_categories = []
        for c in C.objects.filter(subcategory__approvedproduct__status='1',
                                  subcategory__approvedproduct__user__user_type__name__in=['designer'],
                                  subcategory__approvedproduct__user__representing_brand__designer_brand=True).annotate(c=Count('subcategory__approvedproduct')).order_by('-c'):
            designer_categories.append({'name': c.name, 'url': '/shop/designer/category/{}/'.format(c.slug), 'parent': True})
            for sc in SC.objects.annotate(count=Count('approvedproduct')).filter(parent__id=c.id, approvedproduct__status='1',
                        approvedproduct__user__user_type__name__in=['designer'],
                        approvedproduct__user__representing_brand__designer_brand=True,
                        count__gt=0).order_by('-count'):
                designer_categories.append({'name': sc.name, 'url': '/shop/designer/sub-category/{}/'.format(sc.slug), 'parent': False})
        if len(designer_categories) > 36:
            designer_categories = designer_categories[0:35]
        curatedbrands = B.objects.filter(approvedproduct__user__user_type__name__in=['zap_exclusive']).exclude(
            id=132).distinct().annotate(c=Count('approvedproduct')).order_by('-c')[0:8]
        marketbrands = B.objects.filter(
            approvedproduct__user__user_type__name__in=['zap_user', 'zap_dummy', 'store_front']).exclude(
            id=132).distinct().annotate(c=Count('approvedproduct')).order_by('-c')[0:8]
        designerbrands = B.objects.filter(approvedproduct__user__user_type__name__in=['designer'], designer_brand=True,
                                          brand_account__isnull=False).exclude(id=132).distinct().annotate(
            c=Count('approvedproduct')).order_by('-c')[0:16]
        internationalbrands = B.objects.filter(approvedproduct__user__user_type__name__in=['designer'],
                                               designer_brand=False, brand_account__isnull=False).exclude(
            id=132).distinct().annotate(c=Count('approvedproduct')).order_by('-c')[0:16]

        #open
        internationalMenu = '<div id="international_menu" data-activates="#international_menu" class="hover_trigger inline hide_on_leave"><div class="inline full_width">'
        #add categories
        internationalMenu += '<div class="inline_block categories size7of12 inline">'
        index = 0
        for cat in international_categories:
            if index % 12 == 0:
                internationalMenu += '<div class="inline_block column">'
            internationalMenu += '<div><a href="' + cat['url'] + '"' + (' class="bold"' if cat['parent'] else '') + '>' + cat['name'] + '</a></div>'
            if (index+1) % 12 == 0:
                internationalMenu += '</div>'
            index += 1
        if (index-1) % 12 != 0:
            internationalMenu += '</div>'
        #close
        internationalMenu += '</div><div class="separator"></div>'
        # add brands
        internationalMenu += '<div class="inline brands inline_block size5of12 no_margin">'
        index = 0
        for brand in internationalbrands:
            if index % 8 == 0:
                internationalMenu += '<div class="inline_block size6of12">'
            internationalMenu += '<div class="menu_option_item"><a href="/shop/brand/brand/'+brand.slug+'/">'+brand.brand+'</a></div>'
            index += 1
            if index % 8 == 0:
                internationalMenu += '</div>'
        if index % 8 != 0:
            internationalMenu += '</div><div><a href="/shop/brand/brand/" style="font-weight: bold;padding: 20px 0;display: inline-block;">List Brands - A to Z</a></div>'
        else:
            internationalMenu += '<div><a href="/shop/brand/brand/" style="font-weight: bold;padding: 20px 0;display: inline-block;">List Brands - A to Z</a></div>'
        # close
        internationalMenu += '</div>'
        #open
        designerMenu = '<div id="designer_menu" data-activates="#designer_menu" class="hover_trigger inline hide_on_leave"><div class="inline full_width">'
        # add categories
        designerMenu += '<div class="inline_block categories size7of12 inline">'
        index = 0
        for cat in designer_categories:
            if index % 12 == 0:
                designerMenu += '<div class="inline_block column">'
            designerMenu += '<div><a href="' + cat['url'] + '"' + (' class="bold"' if cat['parent'] else '') + '>' + cat['name'] + '</a></div>'
            if (index+1) % 12 == 0:
                designerMenu += '</div>'
            index += 1
        if (index-1) % 12 != 0:
            designerMenu += '</div>'
        # close
        designerMenu += '</div><div class="separator"></div>'
        # add brands
        designerMenu += '<div class="inline brands inline_block size5of12 no_margin">'
        index = 0
        for brand in designerbrands:
            if index % 8 == 0:
                designerMenu += '<div class="inline_block size6of12">'
            designerMenu += '<div class="menu_option_item"><a href="/shop/designer/brand/' + brand.slug + '/">' + brand.brand + '</a></div>'
            index += 1
            if index % 8 == 0:
                designerMenu += '</div>'
        if index % 8 != 0:
            designerMenu += '</div><div><a href="/shop/designer/brand/" style="font-weight: bold;padding: 20px 0;display: inline-block;">List Brands - A to Z</a></div>'
        else:
            designerMenu += '<div><a href="/shop/designer/brand/" style="font-weight: bold;padding: 20px 0;display: inline-block;">List Brands - A to Z</a></div>'
        # close
        designerMenu += '</div>'

        curatedNav = '<div id="preloved_menu" data-activates="#preloved_menu" class="hover_trigger inline hide_on_leave"><div class="inline inline_block"><div class="header block"><h1><a href="/shop/curated" class="block left">Curated</a><a class="pink underline uppercase" href="/shop/curated" style="margin-left: 20px; font-size: 16px ! important;">Shop Now</a></h1><p class="intro">Pre-owned fashion hand-picked from India&rsquo;s most stylish closets</p></div><div class="categories inline"><h6 class="uppercase block">Shop by Category</h6><ul class="categories_list menu_options_list"><li><a href="/shop/curated/category/indian-wear/">Indian Wear</a></li><li><a href="/shop/curated/category/tops/">Tops</a></li><li><a href="/shop/curated/category/bottoms/">Bottoms</a></li><li><a href="/shop/curated/category/dresses/">Dresses</a></li><li><a href="/shop/curated/category/tops-and-bottoms/">Tops and Bottoms</a></li><li><a href="/shop/curated/category/handbags/">Handbags</a></li><li><a href="/shop/curated/category/accessories/">Accessories</a></li><li><a href="/shop/curated/category/foot-wear/">Footwear</a></li></ul><a class="block pink underline" href="/shop/curated/category/">View All</a></div><div class="brands"><h6 class="uppercase block">Shop by Brand</h6><div class="inline"><ul class="menu_options_list">'
        for brand in curatedbrands:
            curatedNav += '<li class="menu_option_item"><a ng-href="/shop/curated/brand/'+ brand.slug +'/">'+ brand.brand +'</a></li>'
        curatedNav += '</ul><a class="block pink underline" href="/shop/curated/brand/">View All</a></div></div></div>'
        marketNav = '<div class="inline inline_block"><div class="header block"><h1><a href="/shop/market" class="block left">Marketplace</a><a class="pink underline uppercase" href="/shop/market" style="margin-left: 20px; font-size: 16px ! important;">Shop Now</a></h1><p class="intro">Marketplace for fashionistas to buy and sell preowned fashion</p></div><div class="categories inline web_only"><h6 class="uppercase block">Shop by Category</h6><ul class="categories_list menu_options_list"><li><a href="/shop/market/category/indian-wear/">Indian Wear</a></li><li><a href="/shop/market/category/tops/">Tops</a></li><li><a href="/shop/market/category/bottoms/">Bottoms</a></li><li><a href="/shop/market/category/dresses/">Dresses</a></li><li><a href="/shop/market/category/tops-and-bottoms/">Tops and Bottoms</a></li><li><a href="/shop/market/category/handbags/">Handbags</a></li><li><a href="/shop/market/category/accessories/">Accessories</a></li><li><a href="/shop/market/category/foot-wear/">Footwear</a></li></ul><a class="block pink underline" href="/shop/market/category/">View All</a></div><div class="brands"><h6 class="uppercase block">Shop by Brand</h6><div class="inline"><ul class="menu_options_list">'
        for brand in marketbrands:
            marketNav += '<li class="menu_option_item"><a ng-href="/shop/market/brand/'+ brand.slug +'/">'+ brand.brand +'</a></li>'
        marketNav += '</ul><a class="block pink underline" href="/shop/market/brand/">View All</a></div></div></div></div>'
        prelovedNav = curatedNav + marketNav

        return self.send_response(1, {
            'international_categories': international_categories,
            'designer_categories': designer_categories,
            'internationalMenu': internationalMenu,
            'designerMenu': designerMenu,
            'prelovedNav': prelovedNav
        })


class Footer(ZapView):

    def get(self, request):
        with open(settings.BASE_DIR + '/../zap_apps/account/templates/account/footer.html', 'r') as myfile:
            footerhtml = myfile.read()
        return self.send_response(1, {'html': footerhtml})



def WebsiteHeaderProducts(request):
    data = cache.get('cache_website_header_products')
    if not data:
        # new_arrival = [{'discount':get_discount(p),'eye':randint(1,10),'id': p.id, 'title':p.title, 'brand':p.brand.brand,'listing_price':p.listing_price,'original_price':p.original_price,'image': p.images.first().image.url_500x500} for p in ApprovedProduct.ap_objects.all()[0:10]]
        # pdb.set_trace()
        # steal_deals = [{'discount':get_discount(t),'eye':randint(1,10),'id': t.id, 'image': settings.CURRENT_DOMAIN + t.images.all().order_by('id')[0].image.url_500x500, 'title':t.title, 'brand':t.brand.brand, 'original_price':t.original_price, 'listing_price':t.listing_price, 'size':get_size(t)} for t in ProductCollection.objects.filter(title__iexact='steal deals')[0].product.filter(status='1')]
        # editors_pics = [{'discount':get_discount(t),'eye':randint(1,10),'id': t.id, 'image': settings.CURRENT_DOMAIN + t.images.all().order_by('id')[0].image.url_500x500, 'title':t.title, 'brand':t.brand.brand, 'original_price':t.original_price, 'listing_price':t.listing_price, 'size':get_size(t)} for t in ProductCollection.objects.filter(title__iexact="editor's picks")[0].product.filter(status='1')]
        # collections = [{'image':b.image.url,'title':b.title, 'target':b.action.website_target} for b in CustomCollection.objects.all()[0].collection.all()]
        curatedbrands = [{'title':b.brand,'id':b.id, 'slug':b.slug} for b in B.objects.filter(approvedproduct__user__user_type__name__in=['zap_exclusive']).exclude(id=132).distinct().annotate(c=Count('approvedproduct')).order_by('-c')[0:20]]
        designerbrands = [{'title':b.brand,'id':b.id, 'slug':b.slug} for b in B.objects.filter(approvedproduct__user__user_type__name__in=['designer'], designer_brand=True, brand_account__isnull=False).exclude(id=132).distinct().annotate(c=Count('approvedproduct')).order_by('-c')[0:20]]
        internationalbrands = [{'title': b.brand, 'id': b.id, 'slug':b.slug} for b in
                          B.objects.filter(approvedproduct__user__user_type__name__in=['designer'],
                                           designer_brand=False, brand_account__isnull=False).exclude(id=132).distinct().annotate(
                              c=Count('approvedproduct')).order_by('-c')[0:20]]
        marketbrands = [{'title':b.brand,'id':b.id, 'slug':b.slug} for b in B.objects.filter(approvedproduct__user__user_type__name__in=['zap_user', 'zap_dummy', 'store_front']).exclude(id=132).distinct().annotate(c=Count('approvedproduct')).order_by('-c')[0:20]]
        data = {
                # 'new_arrival':new_arrival,
                # 'steal_deals':steal_deals,
                # 'editors_pics':editors_pics,
                # 'collections':collections,
                'marketbrands':marketbrands,'curatedbrands':curatedbrands,'designerbrands':designerbrands,'internationalbrands':internationalbrands}
        cache.set(
                'cache_website_header_products',
                data,
                600)
    return {'h': data}

def get_discount(obj):
    if obj.discount != '' and obj.discount != None and obj.discount != 0:
        return str(int(obj.discount*100))+'% off' if obj.sale=='2' else 'Inspiration'
    else:
        return None

def get_size(product):
    size_type = product.size_type
    size = ''
    if size_type == 'EU':
        for s in product.product_count.all():
            size+=' EU'+s.size.eu_size
    elif size_type == 'US':
        for s in product.product_count.all():
            size+=' US'+s.size.us_size
    elif size_type == 'UK':
        for s in product.product_count.all():
            size+=' UK'+s.size.uk_size
    else:
        size = 'FREESIZE'
    return size

def elastic_shops(request, filter=None, value=None, filter2=None, value2=None):
    data = {'image_header': True, 'ZAP_ENV_VERSION': settings.ZAP_ENV_VERSION}
    if filter:
        data.update({'filter':filter, 'value':value})
        filter_context = filter
        value_context = value
        if filter2:
            data.update({'filter2': filter2, 'value2': value2})
            filter_context = filter2
            value_context = value2
        filter_data = {}
        value_context = unicode(value_context).split('/')[0] #to ignore any following parts like right panel url
        if filter_context == 'shop':
            if value_context == 'designer':
                filter_data.update({'page_title':'Buy Designer Lehengas, Choli, Dresses, Sarees Online India'})
                filter_data.update({'header_title': ''})
                filter_data.update({'header_image_mobile': '/zapstatic/website/banners/designer_banner.jpg'})
                filter_data.update({'meta_description':'Top Designer Wear for Indian Wedding, Party and Festive Occassions. Shop from Varun Bahl, Manish Arora and all the best Indian Designers. Free Shipping, Easy Returns & Cash on Delivery.'})
            elif value_context == 'brand':
                filter_data.update({'page_title': "Buy International brands only on Zapyle"})
                filter_data.update({'header_title': ""})
                filter_data.update({'header_image_mobile': '/zapstatic/website/banners/designer_page_banner1.jpg'})
                filter_data.update({'meta_description': 'Shop from Brands like Louis Vuitton, Gucci, Michael Kors, Prada & more for Women. Free Shipping, Easy Returns & Cash on Delivery.'})
            elif value_context == 'curated':
                filter_data.update({'page_title': "Buy Luxury Handbags, Accessories, Shoes & more Online India"})
                filter_data.update({'header_title': "Pre-owned fashion hand-picked from India's most stylish closets"})
                filter_data.update({'header_image_mobile': '/zapstatic/website/banners/curated_page_banner.jpg'})
                filter_data.update({'meta_description': 'Shop from Brands like Louis Vuitton, Gucci, Michael Kors, Prada & more for Women at upto 90% off. Free Shipping, Easy Returns & Cash on Delivery.'})
            elif value_context == 'market':
                filter_data.update({'page_title': 'Buy Pre-owned Luxury Handbags, Accessories, Shoes & more at upto 90% off'})
                filter_data.update({'header_title': 'Shop high street fashion at upto 70% off!'})
                filter_data.update({'header_image_mobile': '/zapstatic/website/banners/buy_banner.jpg'})
                filter_data.update({'meta_description': 'Shop from the closets of women across India for Louis Vuitton, Gucci, Michael Kors, Prada & more at upto 90% off. Free Shipping, Easy Returns & Cash on Delivery.'})
            data.update({'filter_data': filter_data})
        elif filter_context == 'brand':
            if unicode(value_context).isdigit():
                selected_brand = B.objects.get(id=value_context)
            else:
                selected_brand = B.objects.get(slug=value_context)
            filter_data.update({'page_title':selected_brand.brand + ' on Sale Online India - Up to 70% off only at Zapyle'})
            filter_data.update({'meta_description': selected_brand.meta_description})
            filter_data.update({'header_image_mobile': '/zapmedia/' + str(
                selected_brand.mobile_cover) if selected_brand.mobile_cover else (selected_brand.clearbit_logo + '?s=600') if selected_brand.clearbit_logo != 'logo' else None})
            filter_data.update({'header_title' : selected_brand.brand})
            filter_data.update({'description': selected_brand.description if selected_brand.description else None})
            # filter_data.update({'full_description': selected_brand.description if selected_brand.description else None})
            product_ids = ApprovedProduct.objects.filter(brand=selected_brand).values_list('id', flat=True)
            top_categories_for_brand = SubCategory.objects.filter(approvedproduct__in=product_ids).annotate(count=Count('approvedproduct')).order_by('-count')[:4]
            filter_data.update({'meta_description':'Insane discounts on a beautiful collection of authentic '+ selected_brand.brand +' ' + ((top_categories_for_brand[0].name +', ') if len(top_categories_for_brand)>=1 else '') + ((top_categories_for_brand[1].name+', ') if len(top_categories_for_brand)>=2 else '')+((top_categories_for_brand[2].name+', ') if len(top_categories_for_brand)>=3 else '')+((top_categories_for_brand[3].name) if len(top_categories_for_brand)>=4 else '')+' and more for Women Online India. Safe shipping and easy returns. Limited quantity. COD available.'})
            data.update({'filter_data':filter_data})
        elif filter_context == 'sub-category':
            if unicode(value_context).isdigit():
                selected_category = SC.objects.get(id=value_context)
            else:
                selected_category = SC.objects.get(slug=value_context)
            filter_data.update({'page_title': 'Designer Luxury '+ selected_category.name +' on Sale'})
            filter_data.update({'meta_description': selected_category.meta_description})
            filter_data.update({'header_title': selected_category.name})
            filter_data.update({'description': 'Shop Luxury Brands on Sale Only on Zapyle'})
            filter_data.update({'meta_description':'Up to 70% off on a beautiful collection of authentic Luxury '+ selected_category.name +' for women online India. Safe shipping and easy returns. Limited quantity. COD available.'})
            data.update({'filter_data': filter_data})
        elif filter_context == 'category':
            if unicode(value_context).isdigit():
                selected_category = C.objects.get(id=value_context)
            else:
                selected_category = C.objects.get(slug=value_context)
            filter_data.update({'page_title': 'Designer Luxury '+ selected_category.name +' on Sale'})
            filter_data.update({'meta_description': selected_category.meta_description})
            filter_data.update({'header_title': selected_category.name})
            filter_data.update({'description': 'Shop Luxury Brands on Sale Only on Zapyle'})
            filter_data.update({'meta_description':'Up to 70% off on a beautiful collection of authentic Luxury '+ selected_category.name +' for women online India. Safe shipping and easy returns. Limited quantity. COD available.'})
            data.update({'filter_data': filter_data})
        elif filter_context == 'collection':
            if unicode(value_context).isdigit():
                selected_banner = Banner.objects.get(id=value_context)
            else:
                selected_banner = Banner.objects.get(slug=value_context)
            filter_data.update({'page_title': selected_banner.title})
            filter_data.update({'meta_description': selected_banner.meta_description})
            filter_data.update({'custom_collection': 1})
            filter_data.update({'header_title': selected_banner.title})
            filter_data.update({'description': selected_banner.description})
            filter_data.update({'header_image_mobile': '/zapmedia/' + str(selected_banner.collection_image_mobile) if selected_banner.collection_image_mobile else None})
            # filter_data.update({'header_image': '/zapmedia/' + str(selected_banner.collection_image_web) if selected_banner.collection_image_web else None})
            filter_data.update({'seo_description': selected_banner.seo_description})
            data.update({'filter_data': filter_data})
    return render(request, 'catalogue/elastic_shops.html', data)


class LookItems(ZapView):

    def get(self, request, format=None):
        params = request.GET.copy()
        if 'ids' in params:
            ids = params['ids'].split(',')
            products = ApprovedProduct.ap_objects.filter(id__in=ids)
            if products.count() > 0:
                serializer = LookProductSerializer(products, many=True)
                data = serializer.data
                return self.send_response(1, data)
            else:
                return self.send_response(0, {'error': 'No valid products with those IDs'})
        else:
            return self.send_response(0, {'error': 'Please pass some product IDs'})


class ProductLooks(ZapView):

    def get(self, request, product, format=None):
        from zap_apps.blog.models import BlogPost
        from zap_apps.blog.blog_serializers import SingleBlogPostSrlzr
        try:
            product = ApprovedProduct.ap_objects.get(id=product)
        except Exception:
            self.send_repsonse(0, {'error': 'Product does not exist'})
        looks = BlogPost.public_objects.filter(blog_products__item=product, category__slug='look-book')
        data = {}
        data.update({'look_count': looks.count()})
        data.update({'all_looks': None})
        if looks.count() > 1:
            data['all_looks'] = [{'id': look.id, 'pic': look.cover_pic_thumb} for look in looks]
        first_look = looks.first()
        if request.user.is_authenticated():
            srlzr = SingleBlogPostSrlzr(first_look, context={'user': request.user})
        else:
            srlzr = SingleBlogPostSrlzr(first_look, context={})
        data.update({'look_data': srlzr.data})
        return self.send_response(1, data)

