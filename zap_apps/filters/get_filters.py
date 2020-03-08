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
import math, copy
# from zap_apps.filters.views import create_buckets

SHOPS = (
    (1, 'designer'),
    (2, 'curated'),
    (3, 'market'),
    (4, 'brand'),
    (7, 'high-street'),
)

SHOP_NAMES = (
    (1, 'Designer'),
    (2, 'Curated'),
    (3, 'Marketplace'),
    (4, 'Brands'),
    (7, 'High Street'),
)


def roundup(x):
    return int(math.ceil(x / 10.0)) * 10


def rounddown(x):
    return int(math.floor(x / 10.0)) * 10


def get_discounts(all_products, products, selected_discount):
    disc_rule_dict = dict(DISCOUNT_RULE)
    disc_list = products.exclude(sale='1').values_list('discount', flat=True)
    all_disc_list = list(all_products.exclude(sale='1').values_list('discount', flat=True))
    # pdb.set_trace()
    disc = [disc_range[i] for i in disc_list if i and disc_range[i]]
    all_disc = [disc_range[i] for i in all_disc_list if i and disc_range[i]]
    if len(set(all_disc)) > 1:
        disc_count_list = Counter(disc)
        resp_disc = [{'id': x, 'value': str(disc_rule_dict[x]) + "% and higher", 'count':disc_count_list[
            x], 'selected': x in selected_discount, 'disabled': not x in set(disc)} for x in set(all_disc)]
        return resp_disc
    else:
        return []


def get_tolerance(price_range):
    # pdb.set_trace()
    tolerance = round(
        (price_range[1] - price_range[0]) * FILTER_PRICE_TOLERANCE)
    if tolerance > 3000:
        tolerance = 3000
    # elif tolerance == 0:
    #     tolerance = 50
    return (price_range[0] - tolerance, price_range[1] + tolerance)


def create_buckets(product_list):
    # price_list = price_list.sort()
    # ##pdb.set_trace()
    bucket_size = product_list.count() / 5.0

    result_list = []
    ind = 0
    if bucket_size <= 2.0:
        bucket_size = 2
    else:
        bucket_size = int(round(bucket_size))
    # pdb.set_trace()
    for i in xrange(0, 4):
        result_dict = {}
        try:
            prod_list = product_list[ind:ind + bucket_size]
            result_dict.update({'start_value': rounddown(int(prod_list[0].listing_price)), 'end_value': roundup(int(prod_list[bucket_size - 1].listing_price)), 'range_tuple': (
                rounddown(int(prod_list[0].listing_price)), roundup(int(prod_list[bucket_size - 1].listing_price))), 'prod_list': prod_list, 'prod_ids': [x.id for x in prod_list]})
            result_list.append(result_dict)
            ind += bucket_size
        except:
            if product_list.count() > ind:
                prod_list = product_list[ind:]
                result_dict.update({'start_value': rounddown(int(prod_list[0].listing_price)), 'end_value': roundup(int(prod_list[len(prod_list) - 1].listing_price)), 'range_tuple': (
                    rounddown(int(prod_list[0].listing_price)), roundup(int(prod_list[len(prod_list) - 1].listing_price))), 'prod_list': prod_list, 'prod_ids': [x.id for x in prod_list]})
                result_list.append(result_dict)
                # result_dict.update({str(int(prod_list[0].listing_price))+" to "+str(int(prod_list[len(prod_list)-1].listing_price)):prod_list})
                ind += bucket_size
                break
    try:
        result_dict = {}
        prod_list = product_list[ind:]
        result_dict.update({'start_value': rounddown(int(prod_list[0].listing_price)), 'end_value': roundup(int(prod_list[len(prod_list) - 1].listing_price)), 'range_tuple': (
            rounddown(int(prod_list[0].listing_price)), roundup(int(prod_list[len(prod_list) - 1].listing_price))), 'prod_list': prod_list, 'prod_ids': [x.id for x in prod_list]})
        result_list.append(result_dict)
        # result_dict.update({str(int(prod_list[0].listing_price))+" to "+str(int(prod_list[len(prod_list)-1].listing_price)):prod_list})

    except:
        print 'Already filled'

    return result_list

def get_products_without_filter(sorted_request_dict, filter_name):
    Q_pr_1 = Q(sale='1')
    Q_pr_2 = Q()
    # Q_pr_2 = Q(sum_count=0)
    selected_filters = []
    # pdb.set_trace()
    annotate_dict = {'sum_count': Sum('product_count__quantity')}
    if filter_name in sorted_request_dict:
        selected_filters = sorted_request_dict.pop(filter_name)
    products = getProducts(sorted_request_dict, is_filter=True, product_type=None).annotate(
        **annotate_dict).exclude(Q_pr_1 | Q_pr_2)
    return {'products': products, 'selected_filters': selected_filters}

def get_filters(sorted_request_dict, filter_type, product_type, app_version):
    filter_type_resp_list = [{'title': 'Category', 'value': 'product_category', 'grid_type': 2},
                             {'title': 'Price', 'value': 'price', 'grid_type': 0},
                             {'title': 'Size', 'value': 'size', 'grid_type': 2},
                             {'title': 'Condition', 'value': 'condition', 'grid_type': 1},
                             {'title': 'Discount', 'value': 'disc', 'grid_type': 1}]
    version = 1
    if 'version' in sorted_request_dict:
        version = int(sorted_request_dict.pop('version')[0])

    if 'origin' in sorted_request_dict:
        origin = sorted_request_dict.pop('origin')
        filter_type_resp_list = [
            d for d in filter_type_resp_list if d['value'] not in origin]
    if filter_type in ('price', 'all'):
        selected_price = []
        user_price = []
        if 'selected_price' in sorted_request_dict:
            # selected_price = sorted_request_dict['selected_price']
            del sorted_request_dict['selected_price']
    selected_discount = []
    if 'disc' in sorted_request_dict:
        selected_discount = sorted_request_dict['disc']

    resp = {'filter_types': filter_type_resp_list}

        # del sorted_request_dict['disc']
    # else:
    selected_filters = []
    applied_filters = sorted_request_dict.keys()
    # pdb.set_trace()
    # if filter_type in sorted_request_dict:
    #     selected_filters = sorted_request_dict.pop(filter_type)
        # del sorted_request_dict[filter_type]
    if 'user_price' in sorted_request_dict:
        user_price = sorted_request_dict['user_price']
        del sorted_request_dict['user_price']
    annotate_dict = {'sum_count': Sum('product_count__quantity')}
    Q_pr_1 = Q(sale='1')
    Q_pr_2 = Q()
    # Q_pr_2 = Q(sum_count=0)
    # if product_type:
    # pdb.set_trace()
    try:
        if sorted_request_dict['search']:
            sorted_request_dict['initial_filters'].update({'search':sorted_request_dict['search']})
    except:
        pass
    if sorted_request_dict['initial_filters']:
        all_products = getProducts(sorted_request_dict['initial_filters'], is_filter=True, product_type=None).annotate(
        **annotate_dict).exclude(Q_pr_1 | Q_pr_2)
    else:
        all_products = ApprovedProduct.ap_objects.all()
    # get all product under sale (including sold out)
    filtered_products = getProducts(sorted_request_dict, is_filter=True, product_type=None).annotate(**annotate_dict).exclude(Q_pr_1 | Q_pr_2)

    # filter_types = ['category', 'size', 'price']
    # if :
    # pdb.set_trace()
    if version > 1:
        size_name_key = 'name'
        size_value_key = 'value'
        size_inside_value_key = 'value'
        category_value_key = 'value'
        brand_value_key = 'value'
        style_value_key = 'value'
        colors_value_key = 'value'
        occasions_value_key = 'value'
        age_value_key = 'value'
        condition_value_key = 'value'
        disc_value_key = 'value'
        shops_value_key = 'value'
        srlzr_change_cond = True
    else:
        size_name_key = 'value'
        size_value_key = 'size_type'
        size_inside_value_key = 'size'
        category_value_key = 'category'
        brand_value_key = 'brands'
        style_value_key = 'styles'
        colors_value_key = 'colors'
        occasions_value_key = 'occasions'
        age_value_key = 'age'
        condition_value_key = 'condition'
        disc_value_key = 'disc'
        shops_value_key = 'shops'
        srlzr_change_cond = False

    if filter_type in ('size', 'all'):
        # pdb.set_trace()
        # pdb.set_trace()
        # clothes_size_list = Size.objects.filter(category_type='C').values_list('size', flat=True)
        # footwear_size_list = Size.objects.filter(category_type='FW')
        selected_filters = []
        products = filtered_products
        if 'size' in applied_filters:
            local_sorted_request_dict = copy.deepcopy(sorted_request_dict)
            prod_and_filters = get_products_without_filter(local_sorted_request_dict, 'size')
            products = prod_and_filters['products']
            selected_filters = prod_and_filters['selected_filters']
        size_id_list = products.values_list('size', flat=True)

        filtered_clothes_size = Size.objects.filter(
            id__in=size_id_list, category_type='C').values_list('size', flat=True)

        # filtered_footwear_size =

        filtered_footwear_size = Size.objects.filter(
            id__in=size_id_list, category_type='FW')
        # pdb.set_trace()
        all_size_id_list = all_products.values_list(
            'size', flat=True).order_by().distinct()
        # if all_size_id_list.count()>1:

        all_clothes_size = Size.objects.filter(
            id__in=all_size_id_list, category_type='C').distinct('size')
        all_footwear_size = Size.objects.filter(
            id__in=all_size_id_list, category_type='FW').distinct('size')
        # .values_list('size', flat=True)
        if len(all_size_id_list) > 0:
            if not (filtered_clothes_size or filtered_footwear_size):
                free_size_list = Size.objects.filter(
                    id__in=size_id_list, category_type="FS").values_list('size', )
                free_size_count_dict = Counter(free_size_list)

                size = [{size_name_key: 'Free Size', 'count': free_size_count_dict[
                    i], 'selected': True} for i in set(free_size_list)]
                if size:
                    resp.update({size_value_key: [{'name': 'FREE SIZE', size_inside_value_key: size}]})
                else:
                    clothes_size_count_dict = Counter(filtered_clothes_size)
                    footwear_size_count_dict = Counter(filtered_footwear_size)
                    # pdb.set_trace()
                    clothes_size = [{'id': i.id, size_name_key: i.size, 'count': clothes_size_count_dict[
                                                                                     i.size] or 0,
                                     'selected': i.size in selected_filters,
                                     'disabled': not i.size in filtered_clothes_size} for i in set(all_clothes_size)]
                    footwear_size = [{'id': i.id, size_name_key: i.size, 'display': 'EU ' + str(i.eu_size), 'tooltip':"EU-{}  (US-{}   |   UK-{})".format(i.eu_size,i.us_size,i.uk_size),
                                      'count': footwear_size_count_dict[i] or 0, 'selected': int(
                            i.size) in selected_filters, 'disabled': not i in filtered_footwear_size} for i in set(all_footwear_size)]
                    clothes_size.sort(clothes_size.sort(
                        key=lambda x: x['id']), key=lambda y: y['disabled'])
                    footwear_size.sort(footwear_size.sort(
                        key=lambda x: x['id']), key=lambda y: y['disabled'])
                    resp.update({size_value_key: [
                        {'name': 'CLOTHING SIZE', size_inside_value_key: clothes_size},
                        {'name': 'FOOTWEAR SIZE', size_inside_value_key: footwear_size}]})
            else:
                # if (filtered_clothes_size and filtered_footwear_size):
                clothes_size = []
                footwear_size = []
                if len(all_clothes_size) > 1:
                    clothes_size_count_dict = Counter(filtered_clothes_size)
                    clothes_size = [{'id': i.id, size_name_key: i.size, 'count': clothes_size_count_dict[
                                                                                     i.size] or 0,
                                     'selected': i.size in selected_filters, 'disabled': not i.size in filtered_clothes_size}
                                    for i in set(all_clothes_size)]
                    clothes_size.sort(clothes_size.sort(
                        key=lambda x: x['id']), key=lambda y: y['disabled'])
                else:
                    clothes_size = []

                if len(all_footwear_size) > 1:
                    footwear_size_count_dict = Counter(filtered_footwear_size)
                    footwear_size = [{'id': i.id, size_name_key: i.size, 'display': 'EU ' + str(i.eu_size), 'tooltip':"EU-{}  (US-{}   |   UK-{})".format(i.eu_size,i.us_size,i.uk_size),
                                      'count': footwear_size_count_dict[i] or 0, 'selected': int(
                            i.size) in selected_filters, 'disabled': not i in filtered_footwear_size} for i in
                                     set(all_footwear_size)]
                    # clothes_size = sorted(clothes_size, key=lambda x: (x['id'],x['disabled']))
                    # footwear_size = sorted(footwear_size, key=lambda x: (x['id'],x['disabled']))
                    footwear_size.sort(footwear_size.sort(
                        key=lambda x: x['id']), key=lambda y: y['disabled'])
                else:
                    footwear_size = []
                resp.update({size_value_key: [
                    {'name': 'CLOTHING SIZE', size_inside_value_key: clothes_size},
                    {'name': 'FOOTWEAR SIZE', size_inside_value_key: footwear_size}]})
            # elif filtered_clothes_size:
            #     clothes_size_count_dict = Counter(filtered_clothes_size)
            #     clothes_size = [{'value':i, 'count':clothes_size_count_dict[i] or 0, 'selected': i in selected_filters, 'disabled':not i in filtered_clothes_size} for i in set(all_clothes_size)]
            #     resp = {'filter_types':filter_type_resp_list,'size_type':[{'name':'CLOTHING SIZE','size':clothes_size}]}
            # else:
            #     footwear_size_count_dict = Counter(filtered_footwear_size)
            #     footwear_size = [{'value':i.size, 'display':'UK '+str(i.uk_size) , 'count':footwear_size_count_dict[i], 'selected': int(i.size) in selected_filters, 'disabled':not i in filtered_footwear_size} for i in set(all_footwear_size)]
            #     resp = {'filter_types':filter_type_resp_list,'size_type':[{'name':'FOOTWEAR SIZE','size':footwear_size}]}

    if filter_type in ('price', 'all'):
        # #pdb.set_trace()
        selected_filters = []
        products = filtered_products
        if 'price' in applied_filters:
            local_sorted_request_dict = copy.deepcopy(sorted_request_dict)
            prod_and_filters = get_products_without_filter(local_sorted_request_dict, 'price')
            products = prod_and_filters['products']
            selected_filters = prod_and_filters['selected_filters']
        product_list = products.exclude(
            listing_price=None).order_by('listing_price')
        bucket_list = create_buckets(product_list)
        if len(bucket_list)>1:
            if version > 1:
                min_price_list = []
                max_price_list = []
                for bucket in bucket_list:
                    if bucket['range_tuple'][1] == bucket['range_tuple'][0]:
                        bucket['start_value'] = rounddown(
                            bucket['start_value'] - 10)
                        bucket['end_value'] = roundup(bucket['end_value'] + 10)
                    min_price_list.append(bucket['start_value'])
                    max_price_list.append(bucket['end_value'])
                # pdb.set_trace()
                price = {'min_price_list': min_price_list,
                         'max_price_list': max_price_list}
                price['min_selected_price'] = min(min_price_list, key=lambda x: abs(
                    x - selected_filters[0])) if selected_filters and selected_filters[0] else None
                price['max_selected_price'] = min(max_price_list, key=lambda x: abs(
                    x - selected_filters[1])) if selected_filters and selected_filters[1] else None
                resp.update({'price': price})

            else:
                price = []

                # pdb.set_trace()

                for bucket in bucket_list:
                    if bucket['range_tuple'][1] == bucket['range_tuple'][0]:
                        bucket['start_value'] = rounddown(
                            bucket['start_value'] - 10)
                        bucket['end_value'] = roundup(bucket['end_value'] + 10)

                    # pdb.set_trace()
                    Q_price_obj = Q()
                    selected = False
                    filtered_bucket_products = []
                    # if 'user_price' in sorted_request_dict:
                    for sel_price in user_price:
                        tolerance_range = get_tolerance(sel_price)
                        if tolerance_range[0] <= bucket['range_tuple'][1] and bucket['range_tuple'][0] <= tolerance_range[
                            1]:
                            Q_price_obj |= Q(
                                listing_price__range=tolerance_range)
                    # bucket_products =
                    # for sel_price in selected_price:
                    #     if bucket['range_tuple'][0]<=sel_price[0]<=bucket['range_tuple'][1] or bucket['range_tuple'][0]<=sel_price[0]<=bucket['range_tuple'][1] or (sel_price[0]<=bucket['range_tuple'][0] and sel_price[1]>=bucket['range_tuple'][1]):
                    #         #do a query and chain it
                    #         # prod_list
                    if Q_price_obj:
                        # ##pdb.set_trace()
                        Q_id = Q(id__in=bucket['prod_ids'])
                        Q_price_obj &= Q_id

                        prods = ApprovedProduct.ap_objects.filter(Q_price_obj)
                    else:
                        prods = []
                        # filtered_bucket_products = list(chain(filtered_bucket_products,prods))
                    try:
                        if len(prods) / float(len(bucket['prod_list'])) >= .8:
                            selected = True
                    except ZeroDivisionError:
                        return self.send_response(0, 'Price Range not Available')
                    # ##pdb.set_trace()
                    price.append({'start_value': bucket['start_value'], 'end_value': bucket[
                        'end_value'], 'count': len(bucket['prod_list']), 'selected': selected})
                resp.update({'price': price})
        resp_disc = get_discounts(all_products, products, selected_discount)
        resp.update({disc_value_key: resp_disc})
                # except Exception as e:
                #     resp = {'Error':e}
                # # return self.send_response(1, resp)
    if filter_type == 'disc':
        selected_filters = []
        products = filtered_products
        if 'disc' in applied_filters:
            local_sorted_request_dict = copy.deepcopy(sorted_request_dict)
            prod_and_filters = get_products_without_filter(local_sorted_request_dict, 'disc')
            products = prod_and_filters['products']
            selected_filters = prod_and_filters['selected_filters']
        resp_disc = get_discounts(all_products, products, selected_filters)
        resp.update({disc_value_key: resp_disc})

    if filter_type in ('product_category', 'all'):
        # ###pdb.set_trace()
        selected_filters = []
        products = filtered_products
        if 'product_category' in applied_filters:
            local_sorted_request_dict = copy.deepcopy(sorted_request_dict)
            prod_and_filters = get_products_without_filter(local_sorted_request_dict, 'product_category')
            products = prod_and_filters['products']
            selected_filters = prod_and_filters['selected_filters']
        filter_type_id_list = products.values_list(
            'product_category', flat=True)
        count_dict = Counter(filter_type_id_list)

        # all_product_category_id = list(chain(selected_filters,filter_type_id_list))
        all_product_category_id = all_products.values_list(
            'product_category', flat=True)

        all_sub_cat_list = SubCategory.objects.filter(
            id__in=all_product_category_id)
        if all_sub_cat_list.count()>1:
            all_sub_category_dict = {}
            for all_sub in all_sub_cat_list:
                if all_sub.parent.id in all_sub_category_dict:
                    all_sub_category_dict.get(
                        all_sub.parent.id).append(all_sub)
                else:
                    all_sub_category_dict.update(
                        {all_sub.parent.id: [all_sub]})
            all_cat_id_list = all_sub_cat_list.values_list('parent')
            all_cat_list = Category.objects.filter(id__in=all_cat_id_list)
            # sub_cat_list = SubCategory.objects.filter(id__in=filter_type_id_list)
            # sub_category_dict = {}
            # for sub in sub_cat_list:
            #     if sub.parent.id in sub_category_dict:
            #         sub_category_dict.get(sub.parent.id).append(sub)
            #     else:
            #         sub_category_dict.update({sub.parent.id : [sub]})

            # cat_id_list = sub_cat_list.values_list('parent')
            # cat_list = Category.objects.filter(id__in=cat_id_list)

            srlzr = FilterCategorySeriaizer(all_cat_list, many=True, context={
                'all_sub_category_dict': all_sub_category_dict, 'count_dict': count_dict,
                'selected_cat': selected_filters, 'filtered_subcategory_list': filter_type_id_list,
                'srlzr_change_cond': srlzr_change_cond})
            resp_data = srlzr.data
            # pdb.set_trace()
            # resp_data.sort(resp_data, key=lambda y: y['disabled'])
            resp.update({category_value_key: resp_data})
        else:
            resp.update({category_value_key: None})

    if filter_type in ('brand', 'all'):
        # pdb.set_trace()
        selected_filters = []
        products = filtered_products
        if 'brand' in applied_filters:
            local_sorted_request_dict = copy.deepcopy(sorted_request_dict)
            prod_and_filters = get_products_without_filter(local_sorted_request_dict, 'brand')
            products = prod_and_filters['products']
            selected_filters = prod_and_filters['selected_filters']
        filtered_brand = products.values_list('brand', flat=True)
        count_dict = Counter(filtered_brand)
        all_brand_ids = all_products.values_list(
            'brand', flat=True)
        all_brands = Brand.objects.filter(id__in = all_brand_ids)
        if all_brands.count()>1:
            srlzr = FilterBrandSerializer(all_brands, many=True, context={
                'selected_brand': selected_filters, 'filtered_brand_list': filtered_brand,
                'count_dict': count_dict})
            resp_data = srlzr.data
            resp.update({brand_value_key: resp_data})
        else:
            resp.update({brand_value_key: None})

    if filter_type in ('style', 'all'):
        # pdb.set_trace()
        selected_filters = []
        products = filtered_products
        if 'style' in applied_filters:
            local_sorted_request_dict = copy.deepcopy(sorted_request_dict)
            prod_and_filters = get_products_without_filter(local_sorted_request_dict, 'style')
            products = prod_and_filters['products']
            selected_filters = prod_and_filters['selected_filters']
        filtered_style = products.values_list('style', flat=True)
        count_dict = Counter(filtered_style)
        all_style_ids = all_products.values_list(
            'style', flat=True)
        all_styles = Style.objects.filter(id__in = all_style_ids)
        if all_styles.count()>1:
            srlzr = FilterStyleSerializer(all_styles, many=True, context={
                'selected_style': selected_filters, 'filtered_style_list': filtered_style,
                'count_dict': count_dict})
            resp_data = srlzr.data
            resp.update({style_value_key: resp_data})
        else:
            resp.update({style_value_key: None})

    if filter_type in ('color' 'all'):
        # pdb.set_trace()
        selected_filters = []
        products = filtered_products
        if 'color' in applied_filters:
            local_sorted_request_dict = copy.deepcopy(sorted_request_dict)
            prod_and_filters = get_products_without_filter(local_sorted_request_dict, 'color')
            products = prod_and_filters['products']
            selected_filters = prod_and_filters['selected_filters']
        filtered_color = products.values_list('color', flat=True)
        count_dict = Counter(filtered_color)
        all_color_ids = all_products.values_list(
            'color', flat=True)
        all_colors = Color.objects.filter(id__in = all_color_ids)
        if all_colors.count()>1:
            srlzr = FilterColorSerializer(all_colors, many=True, context={
                'selected_color': selected_filters, 'filtered_color_list': filtered_color,
                'count_dict': count_dict})
            resp_data = srlzr.data
            resp.update({colors_value_key: resp_data})
        else:
            resp.update({colors_value_key: None})

    if filter_type in ('occasion', 'all'):
        # pdb.set_trace()
        selected_filters = []
        products = filtered_products
        if 'occasion' in applied_filters:
            local_sorted_request_dict = copy.deepcopy(sorted_request_dict)
            prod_and_filters = get_products_without_filter(local_sorted_request_dict, 'occasion')
            products = prod_and_filters['products']
            selected_filters = prod_and_filters['selected_filters']
        filtered_occasion = products.values_list('occasion', flat=True)
        count_dict = Counter(filtered_occasion)
        all_occasion_ids = all_products.values_list(
            'occasion', flat=True)
        all_occasions = Occasion.objects.filter(id__in = all_occasion_ids)
        if all_occasions.count()>1:
            srlzr = FilterOccasionSerializer(all_occasions, many=True, context={
                'selected_occasion': selected_filters, 'filtered_occasion_list': filtered_occasion,
                'count_dict': count_dict})
            resp_data = srlzr.data
            resp.update({occasions_value_key: resp_data})
        else:
            resp.update({occasions_value_key: None})

    if filter_type in ('age', 'all'):
        selected_filters = []
        products = filtered_products
        if 'age' in applied_filters:
            local_sorted_request_dict = copy.deepcopy(sorted_request_dict)
            prod_and_filters = get_products_without_filter(local_sorted_request_dict, 'age')
            products = prod_and_filters['products']
            selected_filters = prod_and_filters['selected_filters']
        filtered_age = products.values_list('age', flat=True)
        count_dict = Counter(filtered_age)
        all_age_ids = all_products.values_list(
            'age', flat=True).distinct().order_by()
        all_age_ids = [x for x in all_age_ids if x is not None]
        if len(all_age_ids)>1:
            age_dict = dict(AGE)
            all_age = {}
            for age_id in all_age_ids:
                all_age.update({age_id:age_dict[age_id]})

            resp_data = [{'id': int(k), 'value': v, 'count': count_dict.get(k, 0), 'selected': int(k) in selected_filters,
                          'disabled': not k in filtered_age} for k, v in sorted(all_age.iteritems())]

            resp.update({age_value_key: resp_data})
        else:
            resp.update({age_value_key: None})

    if filter_type in ('condition', 'all'):
        selected_filters = []
        products = filtered_products
        if 'condition' in applied_filters:
            local_sorted_request_dict = copy.deepcopy(sorted_request_dict)
            prod_and_filters = get_products_without_filter(local_sorted_request_dict, 'condition')
            products = prod_and_filters['products']
            selected_filters = prod_and_filters['selected_filters']
        filtered_condition = products.values_list('condition', flat=True)
        count_dict = Counter(filtered_condition)
        all_condition_ids = all_products.values_list(
            'condition', flat=True).distinct().order_by()
        all_condition_ids = [x for x in all_condition_ids if x is not None]
        if len(all_condition_ids) > 1:
            condition_dict = dict(CONDITIONS)
            all_conditions = {}
            for condition_id in all_condition_ids:
                all_conditions.update({condition_id:condition_dict[condition_id]})

            resp_data = [{'id': int(k), 'value': v, 'count': count_dict.get(k, 0), 'selected': int(k) in selected_filters,
                          'disabled': not k in filtered_condition} for k, v in sorted(all_conditions.iteritems())]

            resp.update({condition_value_key: resp_data})
        else:
            resp.update({condition_value_key: None})

    if filter_type in ('shop', 'all'):
        selected_filters = []
        products = filtered_products
        if 'shop' in applied_filters:
            local_sorted_request_dict = copy.deepcopy(sorted_request_dict)
            prod_and_filters = get_products_without_filter(local_sorted_request_dict, 'shop')
            products = prod_and_filters['products']
            selected_filters = prod_and_filters['selected_filters']
        filtered_shops = [product.shop for product in products if product.shop]
        count_dict = Counter(filtered_shops)
        all_shops = set([product.shop for product in all_products if product.shop])
        # all_shops = [1, 2, 3]  #Send all shops all the time. So that users understand the structure.
        if len(all_shops) > 1:
            shop_dict = dict(SHOPS)
            all_shops_dict = {}
            for shop in all_shops:
                all_shops_dict.update({shop: shop_dict[shop]})
            resp_data = [
                    {'id': int(k), 'value': v, 'name': dict(SHOP_NAMES)[int(k)], 'count': count_dict.get(k, 0), 'selected': int(k) in selected_filters or shop_dict[int(k)] in selected_filters,
                     'disabled': not k in filtered_shops} for k, v in sorted(all_shops_dict.iteritems())]
            resp.update({shops_value_key: resp_data})
        else:
            resp.update({shops_value_key: None})

    return resp