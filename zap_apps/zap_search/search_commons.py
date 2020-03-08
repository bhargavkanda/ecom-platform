import pdb
import re

from django.db.models import Q
from functools import reduce
from operator import __or__ as OR, __and__ as AND, mul as MUL
import itertools

from django.utils.datastructures import OrderedSet

from zap_apps.zap_catalogue.models import Category, Style, Color, Occasion, Brand, SubCategory, ApprovedProduct
from zap_apps.zap_commons.commons import powerset_generator


class SEARCH_ITEMS:
    PRODUCT = 'product'
    CLOSET = 'closet'


class ATTRIBUTE_KEYS:
    color_key = 'color__name'
    category_key = 'product_category__parent__name'
    subcategory_key = 'product_category__name'
    style_key = 'style__style_type'
    occasion_key = 'occasion__name'
    brand_key = 'brand__brand'


class PRODUCT_ATTRIBUTES:
    category = 'Category'
    subcategory = 'SubCategory'
    style = 'Style'
    color = 'Color'
    occasion = 'Occasion'
    brand = 'Brand'

class REQUEST_OBJECT:
    applied_filter = 'filter'
    query_string = 'query_string'


class ATTRIBUTE_MATCHES:
    exact = 'exact'
    sides = 'sides'
    middle = 'middle'
    partial = 'partial'

MATCH_TYPES = [ATTRIBUTE_MATCHES.exact, ATTRIBUTE_MATCHES.sides, ATTRIBUTE_MATCHES.middle, ATTRIBUTE_MATCHES.partial]


class STRING_MATCHES:
    exact = 'exact'
    start = 'start'
    partial = 'partial'


class STRING_LOOKUP:
    title = 'title'
    description = 'description'


class SORT_OPTIONS:
    relevance = 'relevance'
    price_ascending = 'listing_price'
    price_descending = '-listing_price'
    popularity = 'loves'
    discount = '-discount'


class FILTER_TYPE:
    APPLIED = 'applied'
    QUERY = 'query'


MAX_FILTER_SUGGESTIONS = 5
MAX_PRODUCT_SUGGESTIONS = 10
MAX_USER_SUGGESTIONS = 10

SORT_RULE = (
	(1, SORT_OPTIONS.price_descending),
	(2, SORT_OPTIONS.price_ascending ),
	(3, SORT_OPTIONS.popularity),
	(4, SORT_OPTIONS.discount),
    (5, SORT_OPTIONS.relevance),
)

TYPE_KEY_DICT = {
    PRODUCT_ATTRIBUTES.category: ATTRIBUTE_KEYS.category_key,
    PRODUCT_ATTRIBUTES.subcategory: ATTRIBUTE_KEYS.subcategory_key,
    PRODUCT_ATTRIBUTES.brand: ATTRIBUTE_KEYS.brand_key,
    PRODUCT_ATTRIBUTES.occasion: ATTRIBUTE_KEYS.occasion_key,
    PRODUCT_ATTRIBUTES.color: ATTRIBUTE_KEYS.color_key,
    PRODUCT_ATTRIBUTES.style: ATTRIBUTE_KEYS.style_key
}


ATTRIBUTES = [PRODUCT_ATTRIBUTES.style, PRODUCT_ATTRIBUTES.category, PRODUCT_ATTRIBUTES.subcategory,
           PRODUCT_ATTRIBUTES.color, PRODUCT_ATTRIBUTES.occasion, PRODUCT_ATTRIBUTES.brand]

KEYWORD_SET = [Category.objects.exclude(name='Tops and Bottoms'), SubCategory.objects.exclude(name='Dresses'), Style.objects.all(), Color.objects.all(),
               Occasion.objects.all(), Brand.objects.all()]

KEYWORD_PREPS = {
    PRODUCT_ATTRIBUTES.style: '',
    PRODUCT_ATTRIBUTES.category: '',
    PRODUCT_ATTRIBUTES.subcategory: '',
    PRODUCT_ATTRIBUTES.color: 'in ',
    PRODUCT_ATTRIBUTES.occasion: 'for ',
    PRODUCT_ATTRIBUTES.brand: 'from ',
}

INIT_QUERY_STRING_FILTER = {
    'string' : '',
    PRODUCT_ATTRIBUTES.style: [],
    PRODUCT_ATTRIBUTES.category: [],
    PRODUCT_ATTRIBUTES.subcategory: [],
    PRODUCT_ATTRIBUTES.color: [],
    PRODUCT_ATTRIBUTES.occasion: [],
    PRODUCT_ATTRIBUTES.brand: [],
}

MIN_RELEVANCE_SCORE = 10

FILTER_ATTRIBUTE_SCORE = 50
ATTRIBUTE_SCORE = 5
TITLE_SCORE = 3
DESCRIPTION_SCORE = 2

WEIGHT_L1 = 4
WEIGHT_L2 = 3
WEIGHT_L3 = 2
WEIGHT_L4 = 1


def process_query_string(query):
    if not query:
        return []
    processed_query = re.sub('[^a-zA-Z0-9\n]', ' ', query)
    keywords = processed_query.split()
    keywords = list(OrderedSet(keywords))
    keyword_suggestion_relevance_map = {}
    keyword_types, keyword_suggestions = get_keyword_types_and_suggestions(keywords, keyword_suggestion_relevance_map)
    score_key = 'relevance_score'
    query_filters = []
    try:
        suggestion_combos = [[{types[i] : keyword_suggestions[i][types[i]]} for i in range(0, len(types))] for types in
                             list(itertools.product(*keyword_types))]
        for combo in suggestion_combos:
            types = list(itertools.chain.from_iterable([d.keys() for d in combo]))
            for attr_combo in list(itertools.product(*[d.values()[0] for d in combo])):
                query_filter = {
                    score_key: 0,
                    'string': '',
                    PRODUCT_ATTRIBUTES.style: [],
                    PRODUCT_ATTRIBUTES.category: [],
                    PRODUCT_ATTRIBUTES.subcategory: [],
                    PRODUCT_ATTRIBUTES.color: [],
                    PRODUCT_ATTRIBUTES.occasion: [],
                    PRODUCT_ATTRIBUTES.brand: [],
                }
                count = 0
                for attr in attr_combo:
                    query_filter[score_key] += keyword_suggestion_relevance_map[attr]
                    query_filter[types[count]].append(attr)
                    count += 1
                query_filters.append(query_filter)
    except Exception as e:
        raise e
    query_filters.sort(key = lambda query_filter: query_filter[score_key], reverse=True)
    for query_filter in query_filters:
        query_filter.pop(score_key, None)
        remove_string_filter_duplicates(query_filter)
    query_string_filters = [{'filter': query_filter} for query_filter in query_filters[:MAX_FILTER_SUGGESTIONS]]
    # print query_string_filters
    return query_string_filters


def remove_string_filter_duplicates(query_filter):
    for key in query_filter.keys():
        if key not in ('string', 'relevance_score'):
            query_filter[key] = list(set(query_filter[key]))


def get_keyword_types_and_suggestions(keywords, keyword_suggestion_relevance_map):
    keyword_types = [[None]] * len(keywords)
    keyword_suggestions = [[None]] * len(keywords)

    for keyword in keywords:
        num = keywords.index(keyword)
        keyword_suggestions[num] = {}
        keyword_types[num] = []

        for keyword_list in KEYWORD_SET:
            keyword_type = keyword_list[0].__class__.__name__
            name = 'brand' if keyword_type == PRODUCT_ATTRIBUTES.brand else \
                   'style_type' if keyword_type == PRODUCT_ATTRIBUTES.style else 'name'
            for match_type in MATCH_TYPES:
                score = ATTRIBUTE_SCORE
                weight = WEIGHT_L1 if match_type == ATTRIBUTE_MATCHES.exact else \
                         WEIGHT_L2 if match_type == ATTRIBUTE_MATCHES.sides else \
                         WEIGHT_L3 if match_type == ATTRIBUTE_MATCHES.middle else \
                         WEIGHT_L4 if match_type == ATTRIBUTE_MATCHES.partial else 0
                words = [word[0] for word in
                         keyword_list.filter(get_type_filter(name, keyword, match_type)).values_list(name)]
                closest_words = get_relevant_words(keyword_type, list(words))
                if not closest_words:
                    continue
                if keyword_type not in keyword_types[num]:
                    keyword_types[num].append(keyword_type)
                keyword_suggestions[num][keyword_type] = closest_words

                for word in closest_words:
                    if keyword_suggestion_relevance_map.get(word, -1) < 0:
                        keyword_suggestion_relevance_map[word] = 0
                    elif keyword_suggestion_relevance_map[word] > 0:
                        continue
                    keyword_suggestion_relevance_map[word] += score * weight
    return (keyword_types, keyword_suggestions)


def get_type_filter(match_key, string, match_type):
    exact_match_query_dict = {
        match_key  + '__iexact': string,
        match_key + '__istartswith': string + ' '
    }
    sides_match_query_dict = {
        match_key + '__iendswith' : ' ' + string,
        match_key + '__istartswith' : string
    }
    middle_match_query_dict = {
        match_key + '__icontains': ' ' + string,
        match_key + '__icontains': ' ' + string + ' ',
    }
    partial_match_query_dict = {
        match_key + '__icontains': string
    }
    query = reduce(OR, [Q(**{key: exact_match_query_dict[key]}) for key in
                        exact_match_query_dict]) if match_type == ATTRIBUTE_MATCHES.exact else reduce(OR, [
        Q(**{key: sides_match_query_dict[key]}) for key in
        sides_match_query_dict]) if match_type == ATTRIBUTE_MATCHES.sides else reduce(OR, [
        Q(**{key: middle_match_query_dict[key]}) for key in
        middle_match_query_dict]) if match_type == ATTRIBUTE_MATCHES.middle else reduce(OR, [
        Q(**{key: partial_match_query_dict[key]}) for key in
        partial_match_query_dict]) if match_type == ATTRIBUTE_MATCHES.partial else Q()
    return query


def get_string_queries(string, string_lookup_type, match_type):

    exact_match_query_dict = {
        string_lookup_type  + '__iexact': string,
        string_lookup_type + '__icontains' : ' ' + string + ' ',
        string_lookup_type + '__istartswith' : string + ' ',
        string_lookup_type + '__iendswith' : ' ' + string
    }
    start_match_query_dict = {
        string_lookup_type + '__icontains' : ' ' + string,
        string_lookup_type + '__istartswith' : string,
    }
    partial_match_query_dict = {
        string_lookup_type + '__icontains' : string
    }
    return {
        STRING_MATCHES.exact: reduce(OR, [Q(**{key: exact_match_query_dict[key]}) for key in exact_match_query_dict]),
        STRING_MATCHES.start: reduce(OR, [Q(**{key: start_match_query_dict[key]}) for key in start_match_query_dict]),
        STRING_MATCHES.partial: reduce(OR, [Q(**{key: partial_match_query_dict[key]}) for key in partial_match_query_dict])
    }.get(match_type, Q())


def string_weighted_score(string_lookup_type, match_type):
    score = TITLE_SCORE if string_lookup_type == STRING_LOOKUP.title else \
        DESCRIPTION_SCORE if string_lookup_type == STRING_LOOKUP.description else 0
    weight = WEIGHT_L1 if match_type == STRING_MATCHES.exact else \
        WEIGHT_L3 if match_type == STRING_MATCHES.start else \
        WEIGHT_L4 if match_type == STRING_MATCHES.partial else 0
    return score * weight


def update_string_relevance(products, relevance_map, query):
    query = ' '.join(list(OrderedSet(query.split())))
    for string_lookup_type in [k for k in dir(STRING_LOOKUP) if not k.startswith('__')]:
        for match_type in [k for k in dir(STRING_MATCHES) if not k.startswith('__')]:
            product_matches = products.filter(get_string_queries(query, string_lookup_type, match_type))
            for product in product_matches:
                relevance_map[product.id] += string_weighted_score(string_lookup_type, match_type)


def get_relevant_words(keyword_type, words):
    attr_key = TYPE_KEY_DICT[keyword_type]
    closest_words = [word for word in words if ApprovedProduct.ap_objects.filter(**{attr_key : word}).count() > 0]
    return closest_words


def get_attr_weight(match_type, filter_type):
    if filter_type == FILTER_TYPE.APPLIED:
        return 1
    weight = WEIGHT_L1 if match_type == ATTRIBUTE_MATCHES.exact else \
             WEIGHT_L2 if match_type == ATTRIBUTE_MATCHES.sides else \
             WEIGHT_L3 if match_type == ATTRIBUTE_MATCHES.middle else \
             WEIGHT_L4 if match_type == ATTRIBUTE_MATCHES.partial else 0
    return weight


def get_serializer_data(query, suggestion_tab, user, applied_filter, endpoint_type, platform):
    tab = 'P' if suggestion_tab == SEARCH_ITEMS.PRODUCT else 'C' if suggestion_tab == SEARCH_ITEMS.CLOSET else 'X'
    search_data = {
        'search_query': query,
        'platform' : platform,
        'endpoint_type': endpoint_type,
        'tab': tab,
        'user' : user.id,
    }
    if applied_filter:
        search_data.update({
            'category': [Category.objects.get(name=category_name).id for category_name in applied_filter[PRODUCT_ATTRIBUTES.category]],
            'subcategory': [SubCategory.objects.get(name=subcategory_name).id for subcategory_name in applied_filter[PRODUCT_ATTRIBUTES.subcategory]],
            'color': [Color.objects.get(name=color_name).id for color_name in applied_filter[PRODUCT_ATTRIBUTES.color]],
            'brand': [Brand.objects.get(brand=brand_name).id for brand_name in applied_filter[PRODUCT_ATTRIBUTES.brand]],
            'occasion': [Occasion.objects.get(name=occasion_name).id for occasion_name in applied_filter[PRODUCT_ATTRIBUTES.occasion]],
            'style': [Style.objects.get(style_type=style_type).id for style_type in applied_filter[PRODUCT_ATTRIBUTES.style]],
        })
    return search_data


def get_analytics_serializer_data(query, user, applied_filter, platform):
    search_data = {
        'search_query': query,
        'platform': platform,
        'user': user.id,
    }
    if applied_filter:
        search_data.update({
            'category': [Category.objects.get(name=category_name).id for category_name in applied_filter[PRODUCT_ATTRIBUTES.category]],
            'subcategory': [SubCategory.objects.get(name=subcategory_name).id for subcategory_name in applied_filter[PRODUCT_ATTRIBUTES.subcategory]],
            'color': [Color.objects.get(name=color_name).id for color_name in applied_filter[PRODUCT_ATTRIBUTES.color]],
            'brand': [Brand.objects.get(brand=brand_name).id for brand_name in applied_filter[PRODUCT_ATTRIBUTES.brand]],
            'occasion': [Occasion.objects.get(name=occasion_name).id for occasion_name in applied_filter[PRODUCT_ATTRIBUTES.occasion]],
            'style': [Style.objects.get(style_type=style_type).id for style_type in applied_filter[PRODUCT_ATTRIBUTES.style]],
        })
    return search_data

def get_filter_analytics_data(applied_filter, platform, user):
    filter_data = {
        'category': [Category.objects.get(name=category_name).id for category_name in applied_filter[PRODUCT_ATTRIBUTES.category]],
        'subcategory': [SubCategory.objects.get(name=subcategory_name).id for subcategory_name in applied_filter[PRODUCT_ATTRIBUTES.subcategory]],
        'color': [Color.objects.get(name=color_name).id for color_name in applied_filter[PRODUCT_ATTRIBUTES.color]],
        'brand': [Brand.objects.get(brand=brand_name).id for brand_name in applied_filter[PRODUCT_ATTRIBUTES.brand]],
        'occasion': [Occasion.objects.get(name=occasion_name).id for occasion_name in applied_filter[PRODUCT_ATTRIBUTES.occasion]],
        'style': [Style.objects.get(style_type=style_type).id for style_type in applied_filter[PRODUCT_ATTRIBUTES.style]],
        'platform' : platform,
        'user' : user.id,
        'size': [],
        'price': [],
    }
    return filter_data

