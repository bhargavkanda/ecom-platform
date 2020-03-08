from celery.task import task

from zap_apps.zap_analytics.models import ImpressionAnalytics
from zap_apps.zap_catalogue.models import ApprovedProduct


@task
def track_discover_impressions(serializer, platform, user):
    if platform is None:
        print('Cannot track impressions on discover! Platform not defined!')
        return
    product_ids = []
    for serializer_data in serializer.data:
        data = dict(serializer_data)
        d = dict(data['content_data']['discover_data'])

        if 'product' in d:
            products = d['product']

            for product in products:
                product_ids.append(product['id'])
    all_products = ApprovedProduct.ap_objects.filter(id__in=product_ids)
    if not user.is_authenticated() and not user.is_superuser:
        user = None
    impressions = [ImpressionAnalytics(
                    product=product,
                    location='D',
                    platform=platform,
                    user=user,
                    rank=0,
                    page_num=1
                ) for product in all_products]

    ImpressionAnalytics.objects.bulk_create(impressions)