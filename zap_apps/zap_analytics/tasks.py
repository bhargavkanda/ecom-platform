from celery.task import task

from zap_apps.zap_analytics.analytics_serializers import *
from zap_apps.zap_catalogue.models import ApprovedProduct
from datetime import datetime
import json
import requests
from zap_apps.zap_analytics.models import ClevertapEvents
from django.db import transaction
from celery.task.schedules import crontab
from celery.decorators import periodic_task


@task
def track_product(product_data):
    product_serializer = ProductAnalyticsSerializer(data=product_data)
    if not product_serializer.is_valid():
        print('Product Analytics Serializer Error : ' + str(product_serializer.errors))
        return
    product_serializer.save()


@task
def track_profile(profile_data):
    profile_serializer = ProfileAnalyticsSerializer(data=profile_data)
    if not profile_serializer.is_valid():
        # print profile_serializer.errors
        return
    profile_serializer.save()


@task
def track_sort(sort_data):
    sort_serializer = SortAnalyticsSerializer(data=sort_data)
    if not sort_serializer.is_valid():
        print(str(sort_serializer.errors))
        return
    sort_serializer.save()


@task
def track_search(search_data):
    search_serializer = SearchAnalyticsSerializer(data=search_data)
    if not search_serializer.is_valid():
        return
    print(str(search_serializer.validated_data))
    search_serializer.save()


@task
def track_notification(notification_data):
    notification_serializer = NotificationAnalyticsSerializer(data=notification_data)
    if not notification_serializer.is_valid():
        print(str(notification_serializer.errors))
        return
    notification_serializer.save()


@task
def track_filter(filter_data):
    filter_serializer = FilterAnalyticsSerializer(data=filter_data)
    if not filter_serializer.is_valid():
        return
    filter_serializer.save()


@task
def track_impressions(product_ids, page, platform, location, user):
    if not user.is_authenticated() and not user.is_superuser:
        user = None
    rank = 0
    impressions = [ImpressionAnalytics(
        product=product,
        location=location,
        platform=platform,
        user=user,
        rank=rank,
        page_num=1
    ) for product in ApprovedProduct.ap_objects.filter(id__in=product_ids)]
    ImpressionAnalytics.objects.bulk_create(impressions)


@periodic_task(run_every=(crontab(minute=0, hour=0)))
def get_clevertap_events():

    headers = {
        "X-CleverTap-Account-Id": "TEST-566-K95-464Z",
        "X-CleverTap-Passcode": "YMC-RUZ-AEAL",
        "Content-Type": "application/json"
    }

    cursor_url = 'https://api.clevertap.com/1/events.json?batch_size=5000'

    # List of all the events
    events = ['love', 'admire', 'comment_on_product', 'add_to_tote', 'removed_from_tote',
              'upload_product', 'mention', 'edit_profile', 'click', 'page_change', 'zoom_image',
              'pincode_check', 'invite_user', 'transaction', 'checkout_step', 'search', 'filter',
              'notification', 'impression', 'coupon_applied', 'charged', 'write_blog', 'comment_on_blog',
              'campaign_page_visits', 'campaign_cta', 'campaign_social_share_cta', 'Product Viewed']

    for event in events:

        # Get cursor for the events
        this_day = str(datetime.now().year) + str('%02d' % datetime.now().month) + str('%02d' % datetime.now().day)
        payload = '{"event_name": "' + event + '", "from": ' + this_day + ', "to": ' + this_day + '}'

        print payload

        response = requests.post(cursor_url, data=payload, headers=headers)
        data = response.json()
        print data
        if data['status'] == 'success':
            cursor = data['cursor']
            next_cursor_data(cursor, event)
        else:
            pass


def next_cursor_data(cursor, event):
    headers = {
        "X-CleverTap-Account-Id": "TEST-566-K95-464Z",
        "X-CleverTap-Passcode": "YMC-RUZ-AEAL",
        "Content-Type": "application/json"
    }

    events_url = 'https://api.clevertap.com/1/events.json?cursor=' + cursor
    event_response = requests.get(events_url, headers=headers)
    event_data = event_response.json()
    print event_data
    if event_data['status'] == 'success':
        if 'next_cursor' in event_data:
            next_cursor = event_data['next_cursor']
            if len(event_data['records']) > 0:
                with transaction.atomic():
                    for record in event_data['records']:
                        entry = ClevertapEvents(name=event, event_details=record)
                        entry.save()
                    next_cursor_data(next_cursor, event)


