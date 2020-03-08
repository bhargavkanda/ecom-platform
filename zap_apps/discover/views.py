from django.conf import settings
from django.shortcuts import render
from zap_apps.account.zapauth import ZapView
from zap_apps.discover.discover_serializer import HomefeedSerializer
from zap_apps.discover.models import Homefeed
from zap_apps.discover.tasks import track_discover_impressions
from django.db.models import Q
import datetime
from django.utils import timezone

# Create your views here.

from django.core.cache import cache
class Discover(ZapView):
    def get(self, request, format=None):
        feedfilters = Q(active=True, start_time__lte=timezone.now(), end_time__gte=timezone.now(), show_in__slug='home')
        if request.GET.get('page', False):
            page = request.GET.get('page', False)
            if page == 'events':
                feedfilters = Q(active=True, start_time__lte=timezone.now(), end_time__gte=timezone.now(), show_in__slug='events')

        if request.GET.get('ajax',False):
            # srlzr = cache.get('cache_discover_data')
            # if not srlzr:
            feed = Homefeed.objects.filter(feedfilters).filter(platform__in=[0,2]).order_by('-importance')
            srlzr = HomefeedSerializer(feed, many=True,
                                           context={'current_user_id': request.user.id or 0,
                                                    'platform': 'web', 'mobile_website':request.META.get('HTTP_MOBILE','false')})
                # cache.set(
                #     'cache_discover_data',
                #     srlzr,
                #     600)
            if settings.CELERY_USE:
                track_discover_impressions.delay(srlzr, request.PLATFORM or 'WEBSITE', request.user)
            else:
                track_discover_impressions(srlzr, request.PLATFORM or 'WEBSITE', request.user)
            return self.send_response(1, srlzr.data)
        elif request.PLATFORM in ['IOS','ANDROID']:
            # pdb.set_trace()
            feed = Homefeed.objects.filter(feedfilters).filter(platform__in=[0,1]).order_by('-importance')
            srlzr = HomefeedSerializer(feed, many=True, context={'current_user_id': request.user.id or 0})
            if settings.CELERY_USE:
                track_discover_impressions.delay(srlzr, request.PLATFORM or 'WEBSITE', request.user)
            else:
                track_discover_impressions(srlzr, request.PLATFORM or 'WEBSITE', request.user)
            return self.send_response(1, srlzr.data)
        return render(request, 'discover/discover.html',{'image_header':True,'ZAP_ENV_VERSION': settings.ZAP_ENV_VERSION})