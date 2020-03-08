from celery.task import task

from zap_apps.zap_search.search_serializer import SearchStringSerializer


@task
def save_search_query(search_data):
    search_serializer = SearchStringSerializer(data=search_data)
    if not search_serializer.is_valid():
        print('Serializer errors : ' + str(search_serializer.errors))
        return
    search_serializer.save()
