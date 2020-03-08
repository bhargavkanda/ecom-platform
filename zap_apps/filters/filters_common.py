# -*- coding: utf-8 -*-
import collections
import pdb
from itertools import chain, imap

from django.conf import settings
from django.db.models import Q, Count, Sum
from psycopg2._range import NumericRange

from zap_apps.filters.models import DISCOUNT_RULE, SORT_RULE
from zap_apps.zap_catalogue.models import ApprovedProduct, Size, Category, SubCategory, Color, Brand, Occasion, Style
from zap_apps.zap_analytics.tasks import track_impressions, track_filter, track_sort
from zap_apps.discover.models import Banner, ProductCollection
from zap_apps.zap_commons.adapters import Int4NumericRange
from zap_apps.marketing.models import Campaign
from zap_apps.filters.elastic_filters import ElasticFilters

SHOPS = (
    (1, 'designer'),
    (2, 'curated'),
    (3, 'market'),
    (4, 'brand'),
    (5, 'brand-new'),
    (6, 'pre-loved'),
    (7, 'high-street'),
)

USER_TYPES = {
    'designer': ['designer'],
    'brand': ['designer'],
    'curated': ['zap_exclusive'],
    'market': ['zap_user', 'zap_dummy', 'zap_admin', 'store_front'],
    'brand-new': ['designer'],
    'pre-loved': ['zap_exclusive', 'zap_user', 'zap_dummy', 'zap_admin', 'store_front']
}

def get_sort_data(sort_option, user, platform):
    sort_data = {
        'sort_option': sort_option,
        'user': user,
        'platform': platform,
    }
    return sort_data

def get_collection_products(paramst, collection_products_o):
    # print collection_products_obj, 'collec new fn'
    # pdb.set_trace()
    print paramst, "get collection params"
    for param in paramst:
        print param
    return getProducts(params=paramst, collection_products_object=collection_products_o, is_filter=True)


def cache_sort(params):
    param_queryDict = collections.OrderedDict(sorted(params.items()))
    param_dict = dict(param_queryDict)
    new_param_dict = {'initial_filters': {}}
    for key in param_dict:
        if key.startswith('i_'):
            new_key = key[2:]
            if new_key == 'collection':
                if str(param_dict[key].split(",")[0]).isdigit():
                    banner_object = Banner.objects.get(id=int(param_dict[key].split(",")[0]))
                else:
                    banner_object = Banner.objects.get(slug=str(param_dict[key].split(",")[0]))
                action_link = banner_object.action.collection_filter
                from django.http import QueryDict
                collection_params = QueryDict(action_link[unicode(action_link).index('?')+1:])  #remove ? and the part before that - send only the query part
                collection_dict = cache_sort(collection_params)
                collection_dict.pop('initial_filters', None)
                new_param_dict['initial_filters'].update(collection_dict)
            else:
                new_param_dict['initial_filters'] \
                    .update({new_key: [(int(x.split('-')[0]), int(x.split('-')[1]))
                                       if new_key == 'user_price' or new_key == 'selected_price'
                                       else int(x) if x.isdigit()
                else x for x in param_dict[key].split(",")]})
                if new_key not in ['price']:
                    new_param_dict['initial_filters'][new_key].sort()
        else:
            if key == 'collection':
                if str(param_dict[key].split(",")[0]).isdigit():
                    banner_object = Banner.objects.get(id=int(param_dict[key].split(",")[0]))
                else:
                    banner_object = Banner.objects.get(slug=str(param_dict[key].split(",")[0]))
                action_link = banner_object.action.collection_filter
                from django.http import QueryDict
                collection_params = QueryDict(action_link[unicode(action_link).index(
                    '?') + 1:])  # remove ? and the part before that - send only the query part
                collection_dict = cache_sort(collection_params)
                collection_dict.pop('initial_filters', None)
                new_param_dict['initial_filters'].update(collection_dict)
            else:
                new_param_dict \
                    .update({key: [(int(x.split('-')[0]), int(x.split('-')[1]))
                                   if key == 'user_price' or key == 'selected_price'
                                   else int(x) if x.isdigit()
                else x for x in param_dict[key].split(",")]})
                if key not in ['price']:
                    new_param_dict[key].sort()
    # #####pdb.set_trace()
    return new_param_dict

def product_in_filter(filter, product):
    from django.http import QueryDict
    filter_params = QueryDict(filter[unicode(filter).index('?') + 1:])  # remove ? and the part before that - send only the query part
    filter_dict = cache_sort(filter_params)
    filter_dict.pop('initial_filters')
    verdict = True
    for key in filter_dict:
        if key=='size':
            size_exists = False
            sizes = product.size.all()
            for size in sizes:
                if size.size.id in filter_dict[key]:
                    size_exists = True
            if not size_exists:
                return False
        elif key == 'price':
            if not (product.listing_price > filter_dict['price'][0] and product.listing_price < filter_dict['price'][1]):
                return False
        elif key == 'disc':
            disc_dict = dict(DISCOUNT_RULE)
            if not product.discount*100 > disc_dict[filter_dict['disc']]:
                return False
        elif key == 'age':
            if not product.age in filter_dict['age']:
                return False
        elif key == 'category':
            if not (product.product_category.parent.id in filter_dict['category'] or product.product_category.parent.slug in filter_dict['category']):
                return False
        elif key == 'condition':
            if not product.condition in filter_dict['condition']:
                return False
        elif key == 'campaign':
            if not product in ApprovedProduct.objects.filter(products__campaign__in=filter_dict['campaign']):
                return False
        elif key == 'shop':
            shop_dict = dict(SHOPS)
            if 5 in filter_dict['shop'] or 'brand-new' in filter_dict['shop']:
                filter_dict['shop'] = [1, 4]
            elif 6 in filter_dict['shop'] or 'pre-loved' in filter_dict['shop']:
                filter_dict['shop'] = [2, 3]
            if not (product.shop in filter_dict['shop'] or shop_dict[product.shop] in filter_dict['shop']):
                return False
        elif key == 'collection':
            if unicode(filter_dict['collection']).isdigit():
                collection = Banner.objects.get(id=filter_dict['collection'])
            else:
                collection = Banner.objects.get(slug=filter_dict['collection'])
            action_link = collection.action.target
            if not product_in_filter(action_link, product):
                return False
        elif key == 'product_collection':
            if not product in ApprovedProduct.objects.filter(in_collection__in=filter_dict['product_collection']):
                return False
        elif key == 'product_category':
            if product.product_category.id not in filter_dict['product_category']:
                return False
        elif key == 'brand':
            if product.brand.id not in filter_dict['brand']:
                return False
        elif key == 'style':
            try:
                if product.style.id not in filter_dict['style']:
                    return False
            except Excemption:
                return False
        elif key == 'color':
            try:
                if product.color.id not in filter_dict['color']:
                    return False
            except Excemption:
                return False
        elif key == 'occasion':
            try:
                if product.occasion.id not in filter_dict['occasion']:
                    return False
            except Excemption:
                return False
    return verdict


def buildQObject(params, ignoreExclude=False):
    # annotate_dict = {}
    Q_obj = Q()
    Q_disc = Q()
    Q_price = Q()
    annotate_dict = {'sum_count': Sum('product_count__quantity')}
    Q_exclude = Q(sale='1')
    if ignoreExclude:
        Q_exclude = Q()

    popularity = False
    sort_by = '-score'
    exclude = False
    for key in params:
        if key == 'size':
            print "sizes"
            # handle it differently
            clothes_size_list = Size.objects.filter(size__in=params[key], category_type='C')
            footwear_size_list = Size.objects.filter(size__in=params[key], category_type='FW')

            if clothes_size_list.count():
                clothes_id_list = clothes_size_list.values_list('id', flat=True)
            else:
                clothes_id_list = Size.objects.filter(category_type='C').values_list('id', flat=True)
            if footwear_size_list.count():
                footwear_id_list = footwear_size_list.values_list('id', flat=True)
            else:
                footwear_id_list = Size.objects.filter(category_type='FW').values_list('id', flat=True)

            accessories_id_list = Size.objects.filter(category_type='FS').values_list('id', flat=True)
            size_id_list = list(chain(clothes_id_list, footwear_id_list, accessories_id_list))
            # size_id_list = Size.objects.filter(size__in=params[key]).values_list('id',flat=True)
            Q_obj &= Q(size__in=size_id_list)
            # exclude = True
        elif key == 'selected_price':
            for i in params[key]:
                Q_price |= Q(listing_price__range=i)
            Q_obj &= Q_price
            # Q_obj &= Q(listing_price__lte=params[key][1])
            # exclude = True
        elif key == 'price':
            # pdb.set_trace()
            if params[key][0]:
                Q_obj &= Q(listing_price__gte=params[key][0])
            if params[key][1]:
                Q_obj &= Q(listing_price__lte=params[key][1])

        elif key == 'disc':
            # #pdb.set_trace()
            disc_rule_dict = dict(DISCOUNT_RULE)
            for i in params[key]:
                Q_disc |= Q(discount__gte=(disc_rule_dict[int(i)] / 100.0))
            Q_obj &= Q_disc
            # exclude = True
        elif key == 'age':
            Q_obj &= Q(age__in=list(imap(str, params[key])))
        elif key == 'category':
            if unicode(params[key][0]).isdigit():
                new_key = 'product_category__parent__in'
            else:
                new_key = 'product_category__parent__slug__in'
            kwargs = {new_key: params[key]}
            Q_obj &= Q(**kwargs)
            # sub_categories = list(SubCategory.objects.filter(parent__in=list(imap(str, params[key]))).values_list('id', flat=True))
            # Q_obj &= Q(product_category__in=sub_categories)
        elif key == 'condition':
            Q_obj &= Q(condition__in=list(imap(str, params[key])))
        elif key == 'campaign':
            # pdb.set_trace()
            campaigns = Campaign.objects.filter(id__in=params[key])
            product_id_list = []
            for campaign in campaigns:
                product_id_list.extend(list(campaign.campaign_product.all().values_list('products__id', flat=True)))
            Q_obj &= Q(id__in=product_id_list)
        elif key == 'store_front':
            # pdb.set_trace()
            if int(params[key][0]) == 1:
                Q_obj &= Q(user__user_type__name='store_front')
            else:
                Q_exclude |= Q(user__user_type__name='store_front')
        elif key == 'shop':
            shops = params[key]
            seller_types = []
            Q_shop = Q()
            Q_shops = Q()
            # pdb.set_trace()
            for shop in shops:
                if shop == SHOPS[0][0] or shop == SHOPS[0][1]:  # Designer
                    Q_shop = Q(user__representing_brand__designer_brand=True, user__user_type__name__in=USER_TYPES[SHOPS[0][1]])
                elif shop == SHOPS[1][0] or shop == SHOPS[1][1]:  # Curated
                    Q_shop = Q(user__user_type__name__in=USER_TYPES[SHOPS[1][1]])
                elif shop == SHOPS[2][0] or shop == SHOPS[2][1]:  # Market
                    Q_shop = Q(user__user_type__name__in=USER_TYPES[SHOPS[2][1]])
                elif shop == SHOPS[3][0] or shop == SHOPS[3][1]:  # Brand
                    seller_types.extend(USER_TYPES[SHOPS[3][1]])
                    Q_shop = Q(user__representing_brand__designer_brand=False, user__user_type__name__in=USER_TYPES[SHOPS[3][1]])
                elif shop == SHOPS[4][0] or shop == SHOPS[4][1]:  # Brand New
                    Q_shop = Q(user__user_type__name__in=USER_TYPES[SHOPS[4][1]])
                elif shop == SHOPS[5][0] or shop == SHOPS[5][1]:  # Pre Loved
                    Q_shop = Q(user__user_type__name__in=USER_TYPES[SHOPS[5][1]])
                Q_shops |= Q_shop
            Q_obj &= Q_shops
        elif key == 'collection':
            try:
                if unicode(params[key][0]).isdigit():
                    banner_object = Banner.objects.get(id=int(params[key][0]))
                else:
                    banner_object = Banner.objects.get(slug=unicode(params[key][0]))
                # print banner_object
                action_link = banner_object.action.collection_filter
                filter_parameter = action_link.split('?')
                arguments = unicode(filter_parameter[1]).split('&')
                filter_params = {}
                for argument in arguments:
                    members = argument.split('=')
                    if members[0] == 'collection':
                        pass
                    else:
                        filter_params[members[0]] = members[1].split(',')
                print filter_params, "Banner filter params"

                import itertools as it
                merge = lambda *args: dict(it.chain.from_iterable(it.imap(dict.iteritems, args)))

                collection_object = buildQObject(filter_params, True)
                Q_obj &= collection_object['filter']
                Q_exclude |= collection_object['exclude']
                sort_by = collection_object['sort_by']
                annotate_dict = merge(collection_object['annotate_dict'], annotate_dict)
            except Banner.DoesNotExist:
                print "Does not exist"
                pass

        elif key == 'product_collection':
            try:
                product_collection_object = ProductCollection.objects.filter(id__in=params[key]).values_list(
                    'product', flat=True)

                # l = product_collection_object.product.all().prefetch_related('product')
                # print l[0]
                # print product_collection_object[0]

                Q_obj &= Q(id__in=list(product_collection_object))

            except ProductCollection.DoesNotExist:
                print "No such Product collection exists"
                pass
        elif key == 'initial_filters':
            import itertools as it
            merge = lambda *args: dict(it.chain.from_iterable(it.imap(dict.iteritems, args)))

            initial_filters = buildQObject(params['initial_filters'], True)
            Q_obj &= initial_filters['filter']
            Q_exclude |= initial_filters['exclude']
            annotate_dict = merge(initial_filters['annotate_dict'], annotate_dict)
        elif key == 'product_category':
            if unicode(params[key][0]).isdigit():
                new_key = 'product_category__in'
            else:
                new_key = 'product_category__slug__in'
            kwargs = {new_key: params[key]}
            Q_obj &= Q(**kwargs)
        # elif key == 'main_category':
        #     if unicode(params[key][0]).isdigit():
        #         new_key = 'product_category__parent__in'
        #     else:
        #         new_key = 'product_category__parent__slug__in'
        #     kwargs = {new_key: params[key]}
        #     Q_obj &= Q(**kwargs)
        elif key == 'brand':
            if unicode(params[key][0]).isdigit():
                new_key = 'brand__in'
            else:
                new_key = 'brand__slug__in'
            kwargs = {new_key: params[key]}
            Q_obj &= Q(**kwargs)
        elif key in ('style', 'color', 'occasion'):
            if unicode(params[key][0]).isdigit():
                new_key = ''.join([key, '__in']) if not key.endswith('__in') else key
            else:
                new_key = ''.join([key, '__slug__in']) if not key.endswith('__slug__in') else key
            kwargs = {new_key: params[key]}
            Q_obj &= Q(**kwargs)
        elif key == 'search':
            from zap_apps.zap_search.search_result_helpers import get_products_for_search
            products = get_products_for_search(None, params[key][0], None, None)
            product_ids = [product.id for product in products]
            # pdb.set_trace()
            Q_obj &= Q(id__in=product_ids)
        elif key == 'sort':
            # pdb.set_trace()
            sort_rule_dict = dict(SORT_RULE)
            sort_by = sort_rule_dict.get(params[key][0])
            if params[key][0] in (1, 2, 4):
                # exclude = True
                pass
            else:
                # popularity = True
                annotate_dict.update({'l_count': Count('loves', distinct=True)})
                sort_by = '-l_count'
                Q_exclude = Q()
    Q_objects = {'filter': Q_obj, 'exclude': Q_exclude, 'annotate_dict': annotate_dict, 'sort_by': sort_by}

    return Q_objects


def getProducts(params, is_filter=False, product_type=None, collection_products_object=None):
    # print collection_products_object, 'collection top'
    # pdb.set_trace()
    if not params:
        # sold_products = ApprovedProduct.objects.all().annotate(s=Sum('product_count__quantity')).filter(s=0)
        # available_products = ApprovedProduct.objects.all().annotate(s=Sum('product_count__quantity')).filter(s__gte=1)
        # return list(itertools.chain(available_products, available_products))
        if not is_filter:
            if product_type:
                if product_type == 'zap_curated':
                    # sold_products = ApprovedProduct.ap_objects.annotate(sum_count=Sum('product_count__quantity')).filter(user__user_type__name='zap_exclusive', sum_count__lte=0)
                    available_products = ApprovedProduct.ap_objects.annotate(
                        sum_count=Sum('product_count__quantity')).filter(user__user_type__name='zap_exclusive')
                elif product_type == 'zap_market':
                    # sold_products = ApprovedProduct.ap_objects.annotate(sum_count=Sum('product_count__quantity')).filter(user__user_type__name__in=['zap_user', 'zap_dummy', 'store_front'], sum_count__lte=0)
                    available_products = ApprovedProduct.ap_objects.annotate(
                        sum_count=Sum('product_count__quantity')).filter(
                        user__user_type__name__in=['zap_user', 'zap_dummy', 'store_front'])
                elif product_type == 'designer':
                    # sold_products = ApprovedProduct.ap_objects.annotate(sum_count=Sum('product_count__quantity')).filter(user__user_type__name='designer', sum_count__lte=0)
                    available_products = ApprovedProduct.ap_objects.annotate(
                        sum_count=Sum('product_count__quantity')).filter(user__user_type__name='designer')
                elif product_type == 'brand':
                    # sold_products = ApprovedProduct.ap_objects.annotate(sum_count=Sum('product_count__quantity')).filter(user__user_type__name='designer', sum_count__lte=0)
                    available_products = ApprovedProduct.ap_objects.annotate(
                        sum_count=Sum('product_count__quantity')).filter(user__user_type__name='designer',
                                                                         user__representing_brand__designer_brand=False)
            else:
                # sold_products = ApprovedProduct.ap_objects.annotate(sum_count=Sum('product_count__quantity')).filter(sum_count__lte=0)
                available_products = ApprovedProduct.ap_objects.annotate(sum_count=Sum('product_count__quantity'))
            # return list(chain(available_products, sold_products))
            return list(available_products)
        else:
            if product_type:
                if product_type == 'zap_curated':
                    products = ApprovedProduct.ap_objects.filter(user__user_type__name='zap_exclusive')
                elif product_type == 'zap_market':
                    products = ApprovedProduct.ap_objects.filter(
                        user__user_type__name__in=['zap_user', 'zap_dummy', 'store_front'])
                elif product_type == 'designer':
                    products = ApprovedProduct.ap_objects.filter(user__user_type__name='designer')
                elif product_type == 'brand':
                    products = ApprovedProduct.ap_objects.filter(user__user_type__name='designer',
                                                                 user__representing_brand__designer_brand=False)
            else:
                products = ApprovedProduct.ap_objects.all()
            return products

    # print params, 'All params received'
    # annotate_dict = {}
    filter_object = buildQObject(params)
    Q_obj = filter_object['filter']
    Q_exclude = filter_object['exclude']
    annotate_dict = filter_object['annotate_dict']
    sort_by = filter_object['sort_by']

    # pdb.set_trace()
    # if 'sum_count' in annotate_dict:
    #     Q1 = Q(sale='1')
    #     Q2 = Q(sum_count=0)
    #     # if popularity:

    # pdb.set_trace()
    # Q2 = Q()
    # products = ApprovedProduct.objects.filter(Q_obj).exclude(Q1 | Q2).annotate(l_count=Count('loves')).order_by('-l_count')
    # pdb.set_trace()
    if product_type:
        if product_type == 'zap_market':
            Q_obj &= Q(user__user_type__name__in=['zap_user', 'zap_dummy', 'store_front'])
        elif product_type == 'zap_curated':
            Q_obj &= Q(user__user_type__name='zap_exclusive')
        elif product_type == 'designer':
            Q_obj &= Q(user__user_type__name='designer')
        elif product_type == 'brand':
            Q_obj &= Q(user__user_type__name='designer', user__representing_brand__designer_brand=False)

    if not is_filter:
        annotate_dict.update({'s': Sum('product_count__quantity')})
        # sold_products = ApprovedProduct.ap_objects.filter(Q_obj).annotate(**annotate_dict).exclude(Q_exclude).order_by(sort_by).filter(s=0).distinct()
        available_products = ApprovedProduct.ap_objects.filter(Q_obj).annotate(**annotate_dict).exclude(
            Q_exclude).order_by(sort_by).distinct()
        # return list(chain(available_products, sold_products))
        return list(available_products)

    products = ApprovedProduct.ap_objects.filter(Q_obj).annotate(**annotate_dict).exclude(Q_exclude).order_by(
        sort_by).distinct()

    return products


def get_filter_data(sorted_request_dict, platform, user):
    # pdb.set_trace()
    user_price_list = [] if not 'user_price' in sorted_request_dict else sorted_request_dict['user_price']
    selected_price_list = [] if not 'selected_price' in sorted_request_dict else sorted_request_dict['selected_price']
    price_list = user_price_list + selected_price_list
    filter_data = {
        'category': [] if not 'category' in sorted_request_dict else [Category.objects.get(name=category_name).id for
                                                                      category_name in sorted_request_dict['category']],
        'subcategory': [] if not 'subcategory' in sorted_request_dict else [
            SubCategory.objects.get(name=subcategory_name).id for subcategory_name in
            sorted_request_dict['subcategory']],
        'color': [] if not 'color' in sorted_request_dict else [Color.objects.get(name=color_name).id for
                                                                color_name in sorted_request_dict['color']],
        'brand': [] if not 'brand' in sorted_request_dict else [Brand.objects.get(brand=brand_name).id for brand_name in
                                                                sorted_request_dict['brand']],
        'occasion': [] if not 'occasion' in sorted_request_dict else [Occasion.objects.get(id=occasion_id).id for
                                                                      occasion_id in sorted_request_dict['occasion']],
        'style': [] if not 'style' in sorted_request_dict else [Style.objects.get(style_type=style_type).id for
                                                                style_type in sorted_request_dict['style']],
        'size': [] if not 'size' in sorted_request_dict else chain.from_iterable(
            [[obj.id for obj in Size.objects.filter(size=size)] for size in sorted_request_dict['size']]),
        'price': [Int4NumericRange(price[0], price[1]) for price in price_list],
        'platform': platform,
        'user': user.id,
    }
    return filter_data


def track_filtered_feed(sorted_request_dict, request, products, current_page):
    if request.PLATFORM is None:
        print('Cannot track impressions on filtered feed! Platform not defined!')
        return
    platform = request.PLATFORM
    filter_data = get_filter_data(sorted_request_dict, platform, request.user)
    sort_option = sorted_request_dict.get('sort', [0])[0]
    if settings.CELERY_USE:
        track_filter.delay(filter_data)
        track_impressions.delay([product['id'] for product in products], current_page, platform, 'F', request.user)
        track_sort.delay(get_sort_data(sort_option, request.user, platform))
    else:
        track_filter(filter_data)
        track_impressions([product['id'] for product in products], current_page, platform, 'F', request.user)
        track_sort(get_sort_data(sort_option, request.user, platform))