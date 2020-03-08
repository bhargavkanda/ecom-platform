from django.conf import settings
from django.http import HttpResponseRedirect
# class DisableCSRFOnDebug(object):
#     def process_request(self, request):
#         if settings.DEBUG:
#             setattr(request, '_dont_enforce_csrf_checks', True)


class CheckSuperUser(object):

    def process_request(self, request):
        if request.user.is_superuser and request.path_info == "/":
            return HttpResponseRedirect("/zapadmin/")
        if not request.user.is_superuser and "zapadmin" in request.path_info:
            return HttpResponseRedirect("/")


class DisableCSRFOnDebug(object):

    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)

class SettingPlatformHeader(object):

    def process_request(self, request):
        setattr(request, 'PLATFORM', request.COOKIES.get('PLATFORM','WEBSITE'))


class DisableCSRFForCitrus(object):

    def process_request(self, request):
        if "payment" in request.path_info:
            setattr(request, '_dont_enforce_csrf_checks', True)


class TestMid(object):

    def process_request(self, request):
        # if 'test' in request.path_info:
        pass
        # print request.COOKIES, ">>>>>>>>>>>>>>>>>"
