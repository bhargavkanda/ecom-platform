from celery import task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from zap_apps.filters.models import FilterTracker
from django.conf import settings
import pdb


@task
def filter_tracker(user_id,filters_dict):
    # #pdb.set_trace()
    if settings.MONGO_DB_TRACKER:
        track = FilterTracker.objects(user=user_id).modify(upsert=True,new=True,set__user=user_id)
        track.modify(push__filters=filters_dict)
        track.save()