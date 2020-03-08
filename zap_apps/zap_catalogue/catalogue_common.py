from django.conf import settings
from django.core.paginator import Paginator

from zap_apps.zap_catalogue.models import ApprovedProduct, SubCategory, Size
from zap_apps.zap_catalogue.product_serializer import ApprovedProductSerializer
import pdb
import collections
import math
from django.db.models import Q, Sum
from itertools import chain


def build_product_response(products, request):

    current_page = request.GET.get('page', 1)
    perpage = request.GET.get('perpage', settings.CATALOGUE_PERPAGE)
    paginator = Paginator(products, perpage)
    p = paginator.page(current_page)
    srlzr = ApprovedProductSerializer(p, many=True,
                                      context={'logged_user': request.user})
    data = {'data': srlzr.data, 'page': current_page, 'total_pages': paginator.num_pages,
            'next': p.has_next(), 'previous': p.has_previous()}
    result = data
    return result


def cache_key_sort(params):
    param_queryDict = collections.OrderedDict(sorted(params.items()))
    return param_queryDict

    # new_param_dict = {}
    # for key in param_dict:
    #     new_param_dict\
    #         .update({key:[(int(x.split('-')[0]),int(x.split('-')[1]))
    #                         if key == 'user_price' or key == 'selected_price'
    #                         else int(x) if x.isdigit()
    #                         else x for x in param_dict[key].split(",")]})
    #     new_param_dict[key].sort()
    # # #####pdb.set_trace()
    # return new_param_dict


def pr(params):
    price = float(params['pr'])
    lower_tolerance = int(params['plt']) if 'plt' in params else 5
    higher_tolerance = int(params['pht']) if 'pht' in params else 5
    price_range = (math.ceil(price-(price*lower_tolerance/100.0)),
                   math.floor(price + (price*higher_tolerance/100.0)))
    return Q(listing_price__range=price_range)


def di(params):
    discount = float(params['di'])
    lower_tolerance = int(params['dlt']) if 'dlt' in params else 5
    higher_tolerance = int(params['dht']) if 'dht' in params else 5
    discount_range = (
        (discount - lower_tolerance)/100.0, (discount + higher_tolerance)/100.0)
    return Q(discount__range=discount_range)
# def cat(params):
#     sub_category = SubCategory.objects.get(id=params['cat'])
#     related_sub_cat_id = sub_category.parent.subcategory_set.all()
#     return Q(product_category__in=related_sub_cat_id)


def cl(params):
    color = params['cl']
    return Q(color=color)


def oc(params):
    occasion = params['oc']
    return Q(occasion=occasion)


def st(params):
    style = params['st']
    return Q(style=style)


def br(params):
    brand = params['br']
    return Q(brand=brand)


def sz(params):
    SIZE_CHART = (
        ('XXS', 1),
        ('XS', 2),
        ('S', 3),
        ('M', 4),
        ('L', 5),
        ('XL', 6),
        ('XXL', 7),
    )
    size = Size.objects.get(id=params['sz'])
    size_list = [size.size]
    if size.category_type == 'C':
        size_chart = dict(SIZE_CHART)
        if size.size not in ['XXS', 'XXL']:
            size_list.append(
                size_chart.keys()[size_chart.values().index(size_chart.get(size.size)-1)])
            size_list.append(
                size_chart.keys()[size_chart.values().index(size_chart.get(size.size)+1)])
        elif size.size == 'XXS':
            size_list.append(
                size_chart.keys()[size_chart.values().index(size_chart.get(size.size)+1)])
        else:
            size_list.append(
                size_chart.keys()[size_chart.values().index(size_chart.get(size.size)-1)])
    elif size.category_type == 'FW':
        if int(size.size) not in [0, 13]:
            size_list.append(int(size.size)-1)
            size_list.append(int(size.size)+1)
        elif int(size.size) == 0:
            size_list.append(int(size.size)+1)
        else:
            size_list.append(int(size.size)-1)
    # pdb.set_trace()
    return Q(size__size__in=size_list)


def get_similiar_products(params):
    Q_obj = Q()
    Q_shop = Q(sum_count__lte=0)
    param_dict = {'pr': pr, 'di': di, 'cl': cl,
                  'oc': oc, 'st': st, 'br': br, 'sz': sz}
    for key in params:
        if key in param_dict:
            Q_obj &= param_dict.get(key)(params)
    if 'shop' in params:
        if params['shop'] == 'curated':
            Q_obj &= Q(user__user_type__name='zap_exclusive')
        else:
            Q_shop |= Q(user__user_type__name='zap_exclusive')
    if 'cat' not in params:
        return ApprovedProduct.ap_objects.annotate(sum_count=Sum(
            'product_count__quantity')).filter(Q_obj).exclude(Q_shop)

    sub_category = SubCategory.objects.get(id=params['cat'])
    sub_cat_products = ApprovedProduct.ap_objects.annotate(sum_count=Sum(
        'product_count__quantity')).filter(Q_obj & Q(product_category=params['cat'])).exclude(Q_shop)
    related_sub_cat_id = sub_category.parent.subcategory_set.all().exclude(
        id=sub_category.id)
    category_products = ApprovedProduct.ap_objects.annotate(sum_count= Sum('product_count__quantity')).filter(
        Q_obj & Q(product_category__in=related_sub_cat_id)).exclude(Q_shop)
    return list(chain(sub_cat_products, category_products))
