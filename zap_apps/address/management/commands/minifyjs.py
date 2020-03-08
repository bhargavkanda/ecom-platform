from django.core.management.base import BaseCommand, CommandError
from jsmin import jsmin
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Initial data for all States'
    def handle(self, *args, **options):
        folder1 = os.path.dirname(settings.BASE_DIR) + '/frontend/static/frontend/scripts/'
        files1 = ['app.js',
             'directives.js',
             'main.js',
             'services/cartService.js']
        folder2 = os.path.dirname(settings.BASE_DIR) + '/frontend/static/frontend/scripts/controllers/'
        files2 = ['PopController.js',
             'editproductController.js',
             'ProductController.js',
             'HomeFeedController.js',
             'TokenController.js',
             'about.js',
             'BloggerController.js',
             'CheckoutController.js',
             'BordingController.js',
             'HeaderController.js',
             'zapupload.js',
             'ProfileController.js',
             'summaryController.js',
             'HomeController.js']
        with open(folder2+'zapjs.min.js', 'w') as out_file:
            for i in files1:
                with open(folder1 + i) as js_file:
                    minified = jsmin(js_file.read())
                    out_file.write(minified)
                    out_file.write("\n")
            for i in files2:
                with open(folder2 + i) as js_file:
                    minified = jsmin(js_file.read())
                    out_file.write(minified)
                    out_file.write("\n")

        folder1 = os.path.dirname(settings.BASE_DIR) + '/frontend/static/frontend/bower_components/'
        files1 = ['jquery/dist/jquery.min.js',
             'angular/angular.min.js',
             'angular-route/angular-route.min.js',
             'angular-resource/angular-resource.min.js',
             'angular-animate/angular-animate.min.js',
             'a0-angular-storage/dist/angular-storage.min.js',
             'angular-cookies/angular-cookies.js',
             'angular-sanitize/angular-sanitize.js',
             'angular-touch/angular-touch.min.js',
             'angular-ui-router/release/angular-ui-router.min.js',
             'ngstorage/ngStorage.min.js',
             'satellizer/satellizer.min.js',
             'sweetalert/dist/sweetalert.min.js',
             'angular-img-cropper/dist/angular-img-cropper.min.js',
             'angular-messages/angular-messages.js',
             'cropper/dist/cropper.js']
        folder2 = os.path.dirname(settings.BASE_DIR) + '/frontend/static/frontend/scripts/controllers/'
        files2 = []
        with open(folder2+'zapjsthirdparty.min.js', 'w') as out_file:
            for i in files1:
                with open(folder1 + i) as js_file:
                    minified = jsmin(js_file.read())
                    out_file.write(minified)
                    out_file.write("\n")
            for i in files2:
                with open(folder2 + i) as js_file:
                    minified = jsmin(js_file.read())
                    out_file.write(minified)
                    out_file.write("\n")    

        folder22 = os.path.dirname(settings.BASE_DIR) + '/frontend/static/frontend/bower_components/'
        files22 = ['jquery/dist/jquery.min.js','angular/angular.min.js','ngstorage/ngStorage.min.js']
        folder3 = os.path.dirname(settings.BASE_DIR) + '/zap_apps/account/static/account/'
        files3 = [
            # 'js/jquery/jquery-1.11.3.min.js',
            'js/angular-sanitize.min.js',
            'js/iscroll.js',
            'js/jquery.scrollTo.min.js',
            'js/jquery.sticky-kit.min.js',
            'js/main.js',
            'js/header.js',
            'services/userService.js',
            'js/materialize.js']
        with open(folder3+'zapjs.min.js', 'w') as out_file:
            for i in files22:
                with open(folder22 + i) as js_file:
                    minified = jsmin(js_file.read())
                    out_file.write(minified)
                    out_file.write("\n")
            for i in files3:
                with open(folder3 + i) as js_file:
                    minified = jsmin(js_file.read())
                    out_file.write(minified)
                    out_file.write("\n")


        folder1a = os.path.dirname(settings.BASE_DIR) + '/frontend/static/frontend/bower_components/'
        files1a = ['jquery/dist/jquery.min.js','angular/angular.min.js','angular-route/angular-route.min.js',
            'angular-resource/angular-resource.min.js','angular-animate/angular-animate.min.js',
            'a0-angular-storage/dist/angular-storage.min.js','angular-cookies/angular-cookies.js',
            'angular-sanitize/angular-sanitize.js','angular-touch/angular-touch.min.js',
            'angular-ui-router/release/angular-ui-router.min.js','ngstorage/ngStorage.min.js',
            'satellizer/satellizer.min.js','angular-img-cropper/dist/angular-img-cropper.min.js',
            'cropper/dist/cropper.js','angular-messages/angular-messages.js','chosen/chosen.jquery.js',
            'sweetalert/dist/sweetalert.min.js']
        folder1b = os.path.dirname(settings.BASE_DIR) + '/frontend/static/frontend/admin_styles/scripts/'
        files1b = ['chosen.ajaxaddition.jquery.js','AdminController.js']#,'kendo.all.min.js']
        folder1c = os.path.dirname(settings.BASE_DIR) + '/frontend/static/frontend/scripts/js/'
        files1c = ['jquery.twbsPagination.js']
        with open(folder1b+'zapadminjs.min.js', 'w') as out_file:
            for i in files1a:
                with open(folder1a + i) as js_file:
                    minified = jsmin(js_file.read())
                    out_file.write(minified)
                    out_file.write("\n")
            for i in files1c:
                with open(folder1c + i) as js_file:
                    minified = jsmin(js_file.read())
                    out_file.write(minified)
                    out_file.write("\n")
            for i in files1b:
                with open(folder1b + i) as js_file:
                    minified = jsmin(js_file.read())
                    out_file.write(minified)
                    out_file.write("\n")