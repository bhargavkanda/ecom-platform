import types

from django.contrib.auth.models import User
# from rest_framework.authentication import BasicAuthentication
# from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.utils import six
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from zap_apps.zapuser.models import ZapUser, BuildNumber
from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings
from zap_apps.account.models import Testimonial
from zap_apps.account.account_serializer import TestimonialSerializer



# def api_view(http_method_names=None):
#     """
#     Decorator that converts a function-based view into an APIView subclass.
#     Takes a list of allowed methods for the view as an argument.
#     """
#     http_method_names = ['GET'] if (http_method_names is None) else http_method_names
#
#     def wrap(func):
#
#         WrappedAPIView = type(
#             six.PY3 and 'WrappedAPIView' or b'WrappedAPIView',
#             (APIView,),
#             {'__doc__': func.__doc__}
#         )
#
#         # Note, the above allows us to set the docstring.
#         # It is the equivalent of:
#         #
#         #     class WrappedAPIView(APIView):
#         #         pass
#         #     WrappedAPIView.__doc__ = func.doc    <--- Not possible to do this
#
#         # api_view applied without (method_names)
#         assert not(isinstance(http_method_names, types.FunctionType)), \
#             '@api_view missing list of allowed HTTP methods'
#
#         # api_view applied with eg. string instead of list of strings
#         assert isinstance(http_method_names, (list, tuple)), \
#             '@api_view expected a list of strings, received %s' % type(http_method_names).__name__
#
#         allowed_methods = set(http_method_names) | set(('options',))
#         WrappedAPIView.http_method_names = [method.lower() for method in allowed_methods]
#
#         def handler(self, *args, **kwargs):
#             return func(*args, **kwargs)
#
#         for method in http_method_names:
#             setattr(WrappedAPIView, method.lower(), handler)
#
#         WrappedAPIView.__name__ = func.__name__
#
#         WrappedAPIView.renderer_classes = getattr(func, 'renderer_classes',
#                                                   APIView.renderer_classes)
#
#         WrappedAPIView.parser_classes = getattr(func, 'parser_classes',
#                                                 APIView.parser_classes)
#
#         WrappedAPIView.authentication_classes = getattr(func, 'authentication_classes',
#                                                         APIView.authentication_classes)
#
#         WrappedAPIView.throttle_classes = getattr(func, 'throttle_classes',
#                                                   APIView.throttle_classes)
#
#         WrappedAPIView.permission_classes = getattr(func, 'permission_classes',
#                                                     APIView.permission_classes)
#
#         return WrappedAPIView.as_view()
#     return wrap
#
# def wrap():
#     return True


def admin_only(func):
    def wrap(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseRedirect("/admin/login/?next={}".format(request.path_info))
            # return Response({'status': "error", "data": "You are not an admin
            # user"})
        return func(request, *args, **kwargs)
    return wrap


def zap_login_required(func):

    @ensure_csrf_cookie
    @api_view(['GET', 'POST', 'DELETE', 'PUT', 'HEAD'])
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return Response({'status': "error", "data": "unauthenticated"})
        if request.user.is_superuser:
            return Response({'status': "error", "data": "You are logged in as admin user."})
        return func(request, *args, **kwargs)
    return wrap


def zap_login_required_testimonials(func):
    @ensure_csrf_cookie
    @api_view(['GET', 'POST', 'DELETE', 'PUT', 'HEAD'])
    def wrap(request, *args, **kwargs):
        from zap_apps.zapuser.zapuser_serializer import CheckBuildNumberSlzr

        # import pdb; pdb.set_trace()
        data = Testimonial.objects.order_by('?').first()
        srlzr = TestimonialSerializer(data)
        if not request.user.is_authenticated():
            build_data = request.GET.copy()
            build = False
            if build_data:
                srlzr = CheckBuildNumberSlzr(data={"number":build_data['number']})
                if not srlzr.is_valid():
                    return Response({'status': "error", "data": srlzr.errors})
                if BuildNumber.objects.filter(number__lte=int(request.GET['number']), app=str(request.PLATFORM).lower()):
                    return Response({'status': "error", "data": {'show_guest': settings.SHOW_GUEST, 'testimonial': srlzr.data, 
                        'build': True, 'referral': getattr(settings, "EASTER_REFERRAL", False)}})
                else:
                    previous_build = BuildNumber.objects.filter(app=request.PLATFORM.lower())[0]
                    new_features = previous_build.new_features.all()
                    features = []
                    for feature in new_features:
                        features.append({'title': feature.title, 'description': feature.description})
                    return Response({'status': "error", "data": {"build":False, "features":features}})
            return Response({'status': "error", "data": {'show_guest': settings.SHOW_GUEST, 'testimonial': srlzr.data}})
        if request.user.is_superuser:
            return Response({'status': "error", "data": {'show_guest': settings.SHOW_GUEST, 'testimonial': srlzr.data}})
        return func(request, *args, **kwargs)
    return wrap


class LoginRequiredMixin(object):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return zap_login_required(view)


class FBAuthBackend(object):

    def authenticate(self, fb_id=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            user = ZapUser.objects.get(fb_id=fb_id)
            return user
        except ZapUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        """ Get a User object from the user_id. """
        try:
            return ZapUser.objects.get(pk=user_id)
        except ZapUser.DoesNotExist:
            return None


class EmailAuthBackend(object):

    def authenticate(self, email=None, password=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            user = ZapUser.objects.get(email=email)
            if user.check_password(password):
                return user
        except ZapUser.DoesNotExist:
            try:
                user = ZapUser.objects.get(zap_username=email)
                if user.check_password(password):
                    return user
            except ZapUser.DoesNotExist:
                return None

    def get_user(self, user_id):
        """ Get a User object from the user_id. """
        try:
            return ZapUser.objects.get(pk=user_id)
        except ZapUser.DoesNotExist:
            return None


class InstgramAuthBackend(object):

    def authenticate(self, instagram_id=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            user = ZapUser.objects.get(instagram_id=instagram_id)
            return user
        except ZapUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        """ Get a User object from the user_id. """
        try:
            return ZapUser.objects.get(pk=user_id)
        except ZapUser.DoesNotExist:
            return None


class ZapView(APIView):

    def send_response(self, status, data=None):
        if status == 1:
            return Response({'status': 'success', 'data': data})
        if status == 0:
            return Response({'status': 'error', 'detail': data or "Sorry, Please try later."})

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(ZapView, self).dispatch(*args, **kwargs)


class ZapAuthView(LoginRequiredMixin, ZapView):
    pass


def zap_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.

    response = exception_handler(exc, context)
    # Now add the HTTP status code to the response.
    if response and response.status_code in [400, 401, 403, 404, 500, 405]:
        response.data['status'] = "error"
    return response
