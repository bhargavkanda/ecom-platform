from dateutil import parser

from zap_apps.account.zapauth import ZapView
from zap_apps.marketing.models import NotificationTracker
from zap_apps.zap_catalogue.models import ApprovedProduct
from zap_apps.zap_analytics.models import AnalyticsSessions, AnalyticsEvents, ProductAnalytics, ImpressionAnalytics
from zap_apps.zap_analytics.analytics_serializers import *
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
import json
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect


class ANALYTICS_TRACK_ITEMS:
    PRODUCT = 'product'
    USER = 'user'


class Analytics(ZapView):

    def post(self, request, track_item, format=None):
        if track_item == ANALYTICS_TRACK_ITEMS.USER:
            action_data = request.data.copy()
            data = {}
            data['action'] = action_data['action']
            data['data'] = action_data['data']
            data['user'] = request.user.id
            if data['action'] == 6:
                data = request.data.copy()
                notif_data = data['data']
                platform = request.PLATFORM
                if platform is None:
                    print('Cannot track notifications! Platform not defined!')
                    return
                notification_tracker = NotificationTracker.objects.get(notif_id=notif_data['notif_id'],
                                                                       user=request.user,
                                                                       sent_time=parser.parse(
                                                                           notif_data['sent_time']).replace(
                                                                           tzinfo=None))
                notification_tracker.opened_time = parser.parse(data['opened_time'])
                notification_tracker.save()
            action_serializer = UserActionSerializer(data=data)
            if not action_serializer.is_valid():
                return self.send_response(0, action_serializer.errors)
            action_serializer.save()
            return self.send_response(1, data)

class RecentProductViewed(ZapView):
    def get(self, request, format=None):

        data = [{'id': i.product.id, 'image': i.product.images.all().order_by('id')[0].image.url_500x500,
                'original_price' : i.product.original_price, 'listing_price':i.product.listing_price,'category':i.product.product_category.parent.name,
                'title':i.product.title, 'sale': True if i.product.sale == '2' else False,'loved': request.user in i.product.loves.all(),
                'available': True if i.product.product_count.filter(quantity__gt=0) else False,'time':i.time} for i in request.user.product_tracking.filter(product__status=1).distinct('product')]
        return self.send_response(1, data)


# Download Seller Analytics
class DownloadSellerAnalytics(ZapView):

    def get(self, request, format=None):

        designer = request.GET.get('designer')
        start = request.GET.get('start')   # DD-MM-YYYY
        end = request.GET.get('end')       # DD-MM-YYYY

        start_date = datetime.strptime(start, "%d-%m-%Y")
        end_date = datetime.strptime(end, "%d-%m-%Y")

        from designer_analytics import DesignerAnalytics

        d = DesignerAnalytics()

        if designer == "all":
            download_url = d.all_designers(start_date, end_date)
        else:
            download_url = d.individual_designer(designer, start_date, end_date)

        return HttpResponseRedirect(download_url)


# Initiate a session everytime user visits zapyle
# Input -  Device ID, platform, start page, source, campaign
# Output - Unique Session ID
class InitiateAnalyticsSession(ZapView):

    def post(self, request, format=None):

        device_id = request.POST.get('device_id')
        platform = request.POST.get('platform')
        start_page = request.POST.get('start_page')
        source = request.POST.get('source')
        campaign = request.POST.get('campaign')

        import datetime, md5, sys, time
        reload(sys)
        sys.setdefaultencoding('utf8')

        now = datetime.datetime.now()
        unix_time = str(time.mktime(now.timetuple()))
        # session_id = str((md5.new(device_id+now).digest()).encode('utf-8').strip())
        session_id = str(device_id)+str(request.user)+unix_time
        import hashlib
        m = hashlib.md5()
        m.update(session_id)
        session_id = m.hexdigest()

        if request.user.is_authenticated():
            user = request.user.zapuser
        else:
            user = None

        # Create New Entry for this session
        session_created = AnalyticsSessions.objects.create(unique_session=session_id,
                                         user=user,
                                         platform=platform,
                                         start_page=start_page,
                                         source=source,
                                         device_id=device_id,
                                         campaign=campaign)

        # Send Session ID to the client as a response
        if session_created:
            data = [{'result': 'success', 'session_id': session_id}]
        else:
            data = [{'result': 'failed'}]

        return self.send_response(1, data)

"""
End Analytics session when user leaves zapyle
Input - session id, End Page
Ouput - Success/Failed message
"""
class EndAnalyticsSession(ZapView):

    def post(self, request, format=None):

        session_id = request.POST.get('session_id')
        end_page = request.POST.get('end_page')
    
        try:
            import datetime
            session = AnalyticsSessions.objects.get(unique_session=session_id)
            session.end_timestamp = datetime.datetime.now()
            session.end_page = end_page
            
            session.save()
            data = [{'result': 'success'}]

        except ObjectDoesNotExist:
            data = [{'result': 'failed', 'message': 'Session not found'}]

        return self.send_response(1, data)

"""
Track Events for the given analytics session
Input - name, session id, timestamp, event details
Output - Success/Failed message

JSON structure for creating records
{
	"data": [{
		"name": "love",
		"session_id": "91a187683372aceb839f271b8e01c292",
		"event_details": {
			"user_id": "1234",
			"product_id": "12344"
		}
	}, {
		"name": "love",
		"session_id": "91a187683372aceb839f271b8e01c292",
		"event_details": {
			"user_id": "1234",
			"product_id": "12345"
		}
	}]
}"""


class TrackAnalyticsEvents(ZapView):
    
    def post(self, request, format=None):

        events = request.POST.get('events')

        import json
        records = json.loads(events)
        
        from django.db import IntegrityError
        try:
            with transaction.atomic():
                for event in records['data']:
                    print event
                    session_instance = AnalyticsSessions.objects.get(unique_session=event['session_id'])
                    entry = AnalyticsEvents(name=event['name'], session=session_instance, event_details=event['event_details'])
                    entry.save()
                data = [{'result': 'success'}]
        except IntegrityError:
            data = [{'result': 'failed'}]

        return self.send_response(1, data)


class SellerAnalytics(ZapView):

    def get(self, request, format=None):

        sort_by = request.GET.get('sort_by')    # fetch the results either by user or product
        id = request.GET.get('id')  # id of user or product

        if sort_by == 'product':
            product_view_object = ProductAnalytics.objects.filter(product=id)
            product_impression_object = ImpressionAnalytics.objects.filter(product=id)
        elif sort_by == 'user':
            product_view_object = ProductAnalytics.objects.filter(product__user=id)
            product_impression_object = ImpressionAnalytics.objects.filter(product__user=id)

            # List of all the products by a seller
            seller_products = product_view_object.order_by('product').distinct()
            print seller_products, 'Seller Products'

            srlzr = SellerAnalyticsByUserSerializer(seller_products, many=True)
        else:
            return self.send_response(0, '{"result":"Not a valid sort by parameter"}')

        results = {}

        if sort_by == 'user':
            results = srlzr.data


        # results['total_views'] = product_view_object.count()
        # results['total_impressions'] = product_impression_object.count()
        # results['unique_views']= product_view_object.order_by('user').distinct().count()
        # results['unique_impressions'] = product_impression_object.order_by('user').distinct().count()

        return self.send_response(1, results)