import json
import sys, os
from os.path import expanduser
home = expanduser("~")
sys.path.append(home + '/Zapcodebase/zapyle_new')
import urllib
from time import time
import django
from bs4 import BeautifulSoup
from django.conf import settings
django.setup()

from zap_apps.blog.models import BlogPost
from zapyle_new.settings.test import *
settings.configure()
os.environ["DJANGO_SETTINGS_MODULE"] = "zapyle_new.settings.test"




def download_images():
    blog_posts = BlogPost.objects.all()

    blog_media_path = settings.MEDIA_ROOT + '/blog'
    if not os.path.exists(blog_media_path):
        os.makedirs(blog_media_path)

    for post in blog_posts:

        soup = BeautifulSoup(post.body, 'lxml')
        images = soup.findAll('img')

        if not images:
            continue

        print "post_id : {}".format(post.id)

        blog_id = post.id
        blog_dir_name = ''.join(['blog_', str(blog_id)])
        print blog_dir_name
        blog_id_path = ''.join([blog_media_path, '/', blog_dir_name])
        print "blog_id_path : {}".format(blog_id_path)
        if not os.path.exists(blog_id_path):
            os.makedirs(blog_id_path)

        for image in images:
            image_url = image['src']

            if image_url.startswith(blog_id_path):
                continue

            print "image_url : {}".format(image_url)
            filename = "blog_image_%s.png" % str(time()).replace('.', '_')
            file_path = ''.join([blog_id_path, '/', filename])
            print file_path
            urllib.urlretrieve(image_url, file_path)
            image['src'] = file_path

            print "new_url : " + image['src']

        # import pdb
        # pdb.set_trace()
        post.body = str(soup.find('body').contents[0])
        post.cover_pic = images[0]['src']
        print post


download_images()
