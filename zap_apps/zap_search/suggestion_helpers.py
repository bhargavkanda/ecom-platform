import string

from django.conf import settings
from django.db.models import Sum

from zap_apps.zap_analytics.tasks import track_impressions
from zap_apps.zap_catalogue.models import ApprovedProduct
from zap_apps.zap_search.search_commons import *
from zap_apps.zap_search.tasks import save_search_query
from zap_apps.zapuser.models import UserProfile


EXCERPT_LENGTH = 7
EXCERPT_TRAIL = '...'

QUERY_TYPES = ['iexact', 'istartswith', 'icontains']



CATEGORY_SUBCATEGORY_CONJUNCTION = 'and '

def get_filter_suggestions(applied_filter, query):
    search_suggestions = process_query_string(query)
    append_applied_filter(search_suggestions, applied_filter)
    for search_suggestion in search_suggestions:
        query_filter = search_suggestion['filter']
        remove_string_filter_duplicates(query_filter)
    generate_strings(search_suggestions, applied_filter)
    search_suggestions = get_unique_filters(search_suggestions)
    return search_suggestions


def append_applied_filter(search_suggestions, applied_filter):
    for search_suggestion in search_suggestions:
        suggestion_string = search_suggestion['filter']
        for k in suggestion_string.keys():
            if k == 'string':
                continue
            if not applied_filter[k]:
                continue
            suggestion_string[k] = applied_filter[k] + suggestion_string[k]
            search_suggestion['filter'] = suggestion_string


def generate_strings(search_suggestions, applied_filter):
    for search_suggestion in search_suggestions:
        suggestion_filter = search_suggestion['filter']
        suggestion_filter_attributes = [attr for attr in ATTRIBUTES if suggestion_filter[attr]]
        for attr in suggestion_filter_attributes:
            string = ' or '.join(suggestion_filter[attr])
            string = KEYWORD_PREPS[attr] + string
            if attr == PRODUCT_ATTRIBUTES.subcategory and PRODUCT_ATTRIBUTES.category in suggestion_filter_attributes:
                string = CATEGORY_SUBCATEGORY_CONJUNCTION + string
            if not 'string' in suggestion_filter:
                suggestion_filter['string'] = ''
            suggestion_filter['string'] = suggestion_filter['string'] + string + ' '
            search_suggestion['filter'] = suggestion_filter
        # print('Search Suggestion : ' + str(search_suggestion))


def get_unique_filters(search_suggestions):
    suggestion_dict = {}
    suggestions = []
    for suggestion in search_suggestions:
        s = suggestion['filter']['string']
        if s not in suggestion_dict:
            suggestion_dict[s] = True
            suggestions.append(suggestion)
    return suggestions


def get_user_suggestions(applied_filter, query, current_user):
    user_suggestions = []
    if not query:
        return user_suggestions
    user_profiles = []
    user_ids = set()
    for query_type in QUERY_TYPES:
        if len(user_profiles) >= MAX_USER_SUGGESTIONS:
            break
        for user_profile in UserProfile.objects.filter(get_closet_query(query, query_type)):
            if len(user_profiles) >= MAX_USER_SUGGESTIONS:
                break
            if user_profile.user_id not in user_ids:
                user_profiles.append(user_profile)
                user_ids.add(user_profile.user_id)

    for user_profile in user_profiles:
        user_data = {}
        user_data.update({'user_id': user_profile.user_id})
        user_data.update({'zap_username': user_profile.user.zap_username})
        user_data.update({'full_name': user_profile.user.get_full_name()})
        user_data.update({'profile_pic': user_profile.profile_pic})
        user_data.update({'verified': user_profile.verified})
        user_data.update({'admirers' : len(user_profile.admiring.all())})
        user_data.update({'closet_size' : len(ApprovedProduct.ap_objects.filter(user_id=user_profile.user_id))})
        user_data.update({'admired' : current_user in user_profile.admiring.distinct()})
        user_suggestions.append(user_data)
    return user_suggestions


def get_closet_query(query, query_type):

    closet_query_dict = {
        'user__first_name__' + query_type : query,
        'user__last_name__' + query_type : query,
        'user__zap_username__' + query_type : query,
        'user__username__' + query_type : query
    }
    return reduce(OR, [Q(**{key: closet_query_dict[key]}) for key in closet_query_dict])



def get_product_suggestions(applied_filter, query, platform, user):
    if not query:
        return []
    product_suggestions = []
    products = ApprovedProduct.ap_objects.all()
    product_suggestion_relevance_map = {product.id : 0 for product in products}
    update_string_relevance(products, product_suggestion_relevance_map, query)
    products = [product for product in products if product_suggestion_relevance_map[product.id] > 0]
    products.sort(key=lambda product: product_suggestion_relevance_map[product.id], reverse=True)
    track_product_suggestion_impressions(products[:MAX_PRODUCT_SUGGESTIONS], platform, user)

    for product in products[:MAX_PRODUCT_SUGGESTIONS]:
        sold_out = product.product_count.all().aggregate(Sum('quantity'))['quantity__sum'] == 0 or product.sale == '1'
        style_inspiration = product.listing_price is None
        listing_price = int(product.listing_price) if not style_inspiration else None
        original_price = int(product.original_price) if not style_inspiration else None
        product_data = {}
        product_data.update({'product_id': product.id})
        product_data.update({'product_user_id': product.user_id})
        product_data.update({'product_name': product.title})
        product_data.update({'description_excerpt': get_description_excerpt(query, product.description)})
        product_data.update({'product_image_url': product.images.first().image.url_100x100})
        product_data.update({'product_listing_price' : listing_price})
        product_data.update({'product_original_price' : original_price})
        product_data.update({'sold_out' : sold_out})
        product_data.update({'style_inspiration' : style_inspiration})
        # print('Product Data : ' + str(product_data))
        product_suggestions.append(product_data)
    return product_suggestions


def get_description_excerpt(query, desc):
    desc_words = desc.split()
    desc_words_lower = [word.lower() for word in desc_words]
    if query.lower() not in desc_words_lower:
        exc_words = desc_words[: EXCERPT_LENGTH] + [EXCERPT_TRAIL]
    else:
        index = desc_words_lower.index(query.lower())
        prefix = index - (EXCERPT_LENGTH / 2)
        suffix = index + (EXCERPT_LENGTH / 2) + 1
        exc_words = desc_words[: EXCERPT_LENGTH] + [EXCERPT_TRAIL] if prefix < 0 else \
            desc_words[-EXCERPT_LENGTH:] + [EXCERPT_TRAIL ]if suffix >= len(desc_words) else \
            [EXCERPT_TRAIL] + desc_words[prefix: suffix] + [EXCERPT_TRAIL]
    exc_text = ' '.join(exc_words)
    return exc_text


def get_suggestions(request, suggestion_tab):
    data = request.data.copy()
    current_user = request.user
    platform = request.PLATFORM
    applied_filter = data.get(REQUEST_OBJECT.applied_filter)
    query = data.get(REQUEST_OBJECT.query_string)
    save_query(query, suggestion_tab, current_user, applied_filter, platform)
    all_suggestions = {}

    if suggestion_tab == SEARCH_ITEMS.PRODUCT:
        filter_suggestions = get_filter_suggestions(applied_filter, query)
        product_suggestions = get_product_suggestions(applied_filter, query, request.PLATFORM, current_user)
        all_suggestions.update({'filters': filter_suggestions})
        all_suggestions.update({'products': product_suggestions})

    elif suggestion_tab == SEARCH_ITEMS.CLOSET:
        user_suggestions = get_user_suggestions(applied_filter, query, current_user)
        all_suggestions.update({'users': user_suggestions})
    return all_suggestions


def track_product_suggestion_impressions(products, platform, user):
    if platform is None:
        return
    if settings.CELERY_USE:
        track_impressions.delay([product.id for product in products], 1, platform, 'S', user)
    else:
        track_impressions([product.id for product in products], 1, platform, 'S', user)


def save_query(query, suggestion_tab, current_user, applied_filter, platform):
    if platform is None:
        return
    serializer_data = get_serializer_data(query, suggestion_tab, current_user, applied_filter, 'SS', platform)
    if settings.CELERY_USE:
        save_search_query.delay(serializer_data)
    else:
        save_search_query(serializer_data)
