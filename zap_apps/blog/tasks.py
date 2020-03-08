import os
from datetime import time

from celery import task
from django.conf import settings
from PIL import Image


@task
def saveImage(b64_list):
    if not os.path.exists(settings.MEDIA_ROOT + '/blog'):
        os.makedirs(settings.MEDIA_ROOT + '/blog')
    for b64 in b64_list:
        header, data = b64['base64'].split(';base64,')
        base64_string = data
        filename = "blog_image%s.png" % str(time()).replace('.', '_')
        fh = open(os.path.join(settings.MEDIA_ROOT + '/blog', filename), "wb")
        fh.write(base64_string.decode('base64'))
        fh.close()
        print '/zapmedia/blog/' + filename
        b64['base64'] = '/zapmedia/blog/' + filename

@task
def saveThumbs(storepath, filename):
    filepath = storepath + filename
    sizes = ['large', 'medium', 'small', 'thumb']
    from zap_apps.zap_catalogue.tasks import image_compression
    for size in sizes:
        split = filename.rsplit('.', 1)
        thumb_name = storepath + '%s.%s.%s' % (split[0], size, 'jpg')
        image = Image.open(filepath)
        original_width, original_height = image.size
        if size == 'large':
            width = 1200
        elif size == 'medium':
            width = 600
        elif size == 'small':
            width = 300
        elif size == 'thumb':
            width = 150
        wpercent = (width / float(image.size[0]))
        height = int((float(image.size[1]) * float(wpercent)))
        size = width, height
        if original_width < width:
            q = 100
            if settings.CELERY_USE:
                image_compression.delay(name=thumb_name, f=filepath, q=q)
            else:
                image_compression(name=thumb_name, f=filepath, q=q)
        else:
            q = 70
            if settings.CELERY_USE:
                image_compression.delay(name=thumb_name, f=filepath, q=q, size=size)
            else:
                image_compression(name=thumb_name, f=filepath, q=q, size=size)
