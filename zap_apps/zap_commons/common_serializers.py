from django.conf import settings
from rest_framework import serializers


class ZapErrorSrlzr(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        super(ZapErrorSrlzr, self).__init__(*args, **kwargs)
        for i in self.fields:
            for j in settings.ERROR_KEYS:
                try:
                    self.fields[i].error_messages[j] = settings.ZAPERROR.error_messages.__dict__[i].__dict__[j]
                except:
                    pass
class ZapErrorModelSrlzr(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super(ZapErrorModelSrlzr, self).__init__(*args, **kwargs)
        for i in self.fields:
            for j in settings.ERROR_KEYS:
                try:
                    self.fields[i].error_messages[j] = settings.ZAPERROR.error_messages.__dict__[i].__dict__[j]
                except:
                    pass