from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Sum, Count

from zap_apps.zap_analytics.tasks import track_impressions, track_search, track_filter, track_sort
from zap_apps.zap_catalogue.models import ApprovedProduct
from zap_apps.zap_catalogue.product_serializer import ApprovedProductSerializerAndroid, ApprovedProductSerializer
from zap_apps.zap_commons.commons import powerset_generator
from zap_apps.zap_search.search_commons import *
from zap_apps.zap_search.tasks import save_search_query
from zap_apps.filters.filters_common import get_sort_data

class FILTER_TYPE:
    APPLIED = 'applied'
    QUERY = 'query'


def get_search_results(request, result_type, product_type):
    result = {}
    user = request.user
    platform = request.PLATFORM
    # platform = request.PLATFORM
    applied_filter = request.data.get(REQUEST_OBJECT.applied_filter)
    query = request.data.get(REQUEST_OBJECT.query_string)
    req_stream = request.stream.GET.copy()
    page = int(req_stream.get('page', 1))
    perpage = int(req_stream.get('perpage', settings.CATALOGUE_PERPAGE))
    sort_option = int(req_stream.get('sort', 0))
    sort_type = dict(SORT_RULE).get(sort_option, SORT_OPTIONS.relevance)
    track_search_analytics(request, sort_option, query, applied_filter)
    if result_type == SEARCH_ITEMS.PRODUCT:
        result = get_product_search_results(applied_filter, query, page, perpage, user, sort_type, platform, product_type=product_type)
    return result

def get_products_for_search(applied_filter, query, sort_type, product_type):
    if product_type:
        if product_type == 'zap_market':
            all_products = ApprovedProduct.ap_objects.filter(user__user_type__name='zap_user')
        elif product_type == 'zap_curated':
            all_products = ApprovedProduct.ap_objects.exclude(user__user_type__name='zap_user')
        else:
            all_products = ApprovedProduct.ap_objects.all()
    else:
        all_products = ApprovedProduct.ap_objects.all()
    result_relevance_score_map = {product.id : 0 for product in all_products}
    if applied_filter:
        update_filter_relevance(all_products, result_relevance_score_map, applied_filter, FILTER_TYPE.APPLIED)
    if query:
        filters = process_query_string(query)
        for filter in filters:
            update_filter_relevance(all_products, result_relevance_score_map, filter['filter'], FILTER_TYPE.QUERY)
        update_string_relevance(all_products, result_relevance_score_map, query)
    if sort_type:
        if sort_type == SORT_OPTIONS.popularity:
            pass
        if sort_type != SORT_OPTIONS.relevance:
            if sort_type == SORT_OPTIONS.popularity:
                all_products = all_products.annotate(l_count=Count('loves', distinct=True)).order_by('-l_count').distinct()
            else:
                all_products = all_products.order_by(sort_type).distinct()
            products = [product for product in all_products if result_relevance_score_map[product.id] > MIN_RELEVANCE_SCORE]
        else:
            products = [product for product in all_products if result_relevance_score_map[product.id] > MIN_RELEVANCE_SCORE]
            products.sort(key=lambda product: result_relevance_score_map[product.id], reverse=True)
    else:
        products = [product for product in all_products if result_relevance_score_map[product.id] > MIN_RELEVANCE_SCORE]
        products.sort(key=lambda product: result_relevance_score_map[product.id], reverse=True)
    products = get_sale_ordered_products(products)
    return products

def get_product_search_results(applied_filter, query, page, perpage, user, sort_type, platform, product_type):
    products = get_products_for_search(applied_filter, query, sort_type, product_type)
    paginator = Paginator(products, perpage)
    if page:
        page = int(page)
    if not paginator.num_pages >= page or page == 0:
        data = {
            'data': [],
            'page': page,
            'total_pages': paginator.num_pages,
            'next': True if page == 0 else False,
            'previous': False if page == 0 else True
        }
        return data
    p = paginator.page(page)
    if platform == 'WEBSITE':
        srlzr = ApprovedProductSerializer(p, many=True, context={'logged_user': user})
    else:
        srlzr = ApprovedProductSerializerAndroid(p, many=True, context={'logged_user': user})
    data = {'data': srlzr.data, 'page': page, 'total_pages': paginator.num_pages,
            'next': p.has_next(), 'previous': p.has_previous()}
    if applied_filter:
        track_search_result_analytics(srlzr.data, applied_filter, platform, user, page)
    result = data
    return result


def get_filter_queries(filter, match_type):
    filter_queries_list = get_filter_queries_list(filter, match_type)
    filter_queries = list(itertools.chain.from_iterable(filter_queries_list))
    return filter_queries


def get_filter_queries_list(filter, match_type):
    colors = filter[PRODUCT_ATTRIBUTES.color]
    categories = filter[PRODUCT_ATTRIBUTES.category]
    subcategories = filter[PRODUCT_ATTRIBUTES.subcategory]
    brands = filter[PRODUCT_ATTRIBUTES.brand]
    occasions = filter[PRODUCT_ATTRIBUTES.occasion]
    styles = filter[PRODUCT_ATTRIBUTES.style]

    filter_queries_list = [
        [] if not len(colors) > 0 else [
            reduce(OR, [get_type_filter(ATTRIBUTE_KEYS.color_key, color, match_type) for color in colors])],
        [] if not len(categories) > 0 else [reduce(OR, [
            get_type_filter(ATTRIBUTE_KEYS.category_key, category, match_type) for category in categories])],
        [] if not len(subcategories) > 0 else [reduce(OR, [
            get_type_filter(ATTRIBUTE_KEYS.subcategory_key, subcategory, match_type) for subcategory in
            subcategories])],
        [] if not len(brands) > 0 else [
            reduce(OR, [get_type_filter(ATTRIBUTE_KEYS.brand_key, brand, match_type) for brand in brands])],
        [] if not len(occasions) > 0 else [
            reduce(OR, [get_type_filter(ATTRIBUTE_KEYS.occasion_key, occasion, match_type) for occasion in occasions])],
        [] if not len(styles) > 0 else [
            reduce(OR, [get_type_filter(ATTRIBUTE_KEYS.style_key, style, match_type) for style in styles])]
    ]
    return filter_queries_list


def get_sale_ordered_products(products):
    sale_products = []
    non_sale_products = []
    for product in products:
        sold_out = product.product_count.all().aggregate(Sum('quantity'))['quantity__sum'] == 0 or product.sale == '1'
        if sold_out:
            non_sale_products.append(product)
        else:
            sale_products.append(product)
    return sale_products + non_sale_products


def update_filter_relevance(products, relevance_score_map, filter, filter_type):
    score = FILTER_ATTRIBUTE_SCORE if filter_type == FILTER_TYPE.APPLIED else ATTRIBUTE_SCORE
    for match_type in [k for k in dir(ATTRIBUTE_MATCHES) if not k.startswith('__')]:
        weight = get_attr_weight(match_type, filter_type)
        filter_queries = get_filter_queries(filter, match_type)
        for query_set in powerset_generator(filter_queries):
            multiplier = len(query_set)
            if multiplier == 0:
                continue
            query = reduce(AND, list(query_set))
            applied_filter_products = products.filter(query)
            for product in applied_filter_products:
                relevance_score_map[product.id] += multiplier * score * weight


def get_all_products(product_type):
    if product_type:
        if product_type == 'zap_market':
            all_products = ApprovedProduct.ap_objects.filter(user__user_type__name='zap_user')
        else:
            all_products = ApprovedProduct.ap_objects.exclude(user__user_type__name='zap_user')
    else:
        all_products = ApprovedProduct.ap_objects.all()
    return all_products


def get_attr_weight(match_type, filter_type):
    if filter_type == FILTER_TYPE.APPLIED:
        return 1
    weight = WEIGHT_L1 if match_type == ATTRIBUTE_MATCHES.exact else \
             WEIGHT_L2 if match_type == ATTRIBUTE_MATCHES.sides else \
             WEIGHT_L3 if match_type == ATTRIBUTE_MATCHES.middle else \
             WEIGHT_L4 if match_type == ATTRIBUTE_MATCHES.partial else 0
    return weight


def track_search_analytics(request, sort_option, query, applied_filter):
    if request.PLATFORM is None:
        return
    platform = request.PLATFORM
    serializer_data = get_serializer_data(query, SEARCH_ITEMS.PRODUCT, request.user, applied_filter, 'SR', platform)
    analytics_serializer_data = get_analytics_serializer_data(query, request.user, applied_filter, platform)

    if settings.CELERY_USE:
        track_sort.delay(get_sort_data(sort_option, request.user, platform))
        track_search.delay(analytics_serializer_data)
        save_search_query.delay(serializer_data)
    else:
        track_sort(get_sort_data(sort_option, request.user, platform))
        track_search(analytics_serializer_data)
        save_search_query(serializer_data)


def track_search_result_analytics(products, applied_filter, platform, user, page):
    if platform is None:
        return
    filter_data = get_filter_analytics_data(applied_filter, platform, user)
    if settings.CELERY_USE:
        track_impressions.delay([product['id'] for product in products], page, platform, 'S', user)
        track_filter.delay(filter_data)
    else:
        track_impressions([product['id'] for product in products], page, platform, 'S', user)
        track_filter(filter_data)
