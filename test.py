
# image = Image.open("/home/latheef/Downloads/test.jpg")
# image.save("/home/latheef/Downloads/test1.jpg",quality=10)

from PIL import Image
import os
import django
os.environ["DJANGO_SETTINGS_MODULE"] = "zapyle_new.settings.local"
django.setup()
from zap_apps.zap_catalogue.models import ProductImage
from zap_apps.zapuser.models import UserProfile

AllImages = ProductImage.objects.all()
sizes = ((100, 100), (500, 500), (1000, 1000), ("oc", "oc"))
count = AllImages.count()
for idx, i in enumerate(AllImages):
    for size in sizes:
        (w, h) = size
        split = i.image.path.rsplit('.', 1)
        thumb_name = '%s.%sx%s.%s' % (split[0], w, h, split[1])
        image = Image.open(i.image.path)
        if w == 'oc':
            s = os.path.getsize(i.image.path)/(1024*1024)
            if s <= .5:
                split1 = i.image.path.rsplit('.', 1)
                thumb_name1 = '%s.%sx%s.%s' % (split1[0], w, h, split1[1])
                image.save(thumb_name1,quality=70)
            if .5 <= s <= 1:
                split1 = i.image.path.rsplit('.', 1)
                thumb_name1 = '%s.%sx%s.%s' % (split1[0], w, h, split1[1])
                image.save(thumb_name1,quality=50)
            else:
                split1 = i.image.path.rsplit('.', 1)
                thumb_name1 = '%s.%sx%s.%s' % (split1[0], w, h, split1[1])
                image.save(thumb_name1,quality=30)
        if w == '100' or w == 100:
            width, height = image.size
            split1 = i.image.path.rsplit('.', 1)
            thumb_name1 = '%s.%sx%s.%s' % (split1[0], w, h, split1[1])
            if (width < 100 or height < 100):
                q = 100
                image.save(thumb_name1,quality=q)
            else:
                image.thumbnail(size, Image.ANTIALIAS)
                q = 80
                image.save(thumb_name1,quality=q)
        if w == '500' or w == 500:
            width, height = image.size
            split1 = i.image.path.rsplit('.', 1)
            thumb_name1 = '%s.%sx%s.%s' % (split1[0], w, h, split1[1])
            if (width < 500 or height < 500):
                q = 100
                image.save(thumb_name1,quality=q)
            else:
                image.thumbnail(size, Image.ANTIALIAS)
                q = 80
                image.save(thumb_name1,quality=q)
        if w == '1000' or w == 1000:
            width, height = image.size
            split1 = i.image.path.rsplit('.', 1)
            thumb_name1 = '%s.%sx%s.%s' % (split1[0], w, h, split1[1])
            if (width < 1000 or height < 1000):
                q = 100
                image.save(thumb_name1,quality=q)
            else:
                image.thumbnail(size, Image.ANTIALIAS)
                q = 80
                image.save(thumb_name1,quality=q)
    print (count-idx),' images remaining to compress'
print "compression completed"

AllImages = UserProfile.objects.all()
sizes = ((100, 100), (500, 500))
count = AllImages.count()
for idx, i in enumerate(AllImages):
    if i.pro_pic:
        for size in sizes:
            (w, h) = size
            split = i.pro_pic.path.rsplit('.', 1)
            thumb_name = '%s.%sx%s.%s' % (split[0], w, h, split[1])
            image = Image.open(i.pro_pic.path)
            if w == 'oc':
                s = os.path.getsize(i.pro_pic.path)/(1024*1024)
                if s <= .5:
                    split1 = i.pro_pic.path.rsplit('.', 1)
                    thumb_name1 = '%s.%sx%s.%s' % (split1[0], w, h, split1[1])
                    image.save(thumb_name1,quality=70)
                if .5 <= s <= 1:
                    split1 = i.pro_pic.path.rsplit('.', 1)
                    thumb_name1 = '%s.%sx%s.%s' % (split1[0], w, h, split1[1])
                    image.save(thumb_name1,quality=50)
                else:
                    split1 = i.pro_pic.path.rsplit('.', 1)
                    thumb_name1 = '%s.%sx%s.%s' % (split1[0], w, h, split1[1])
                    image.save(thumb_name1,quality=30)
            if w == '100' or w == 100:
                width, height = image.size
                split1 = i.pro_pic.path.rsplit('.', 1)
                thumb_name1 = '%s.%sx%s.%s' % (split1[0], w, h, split1[1])
                if (width < 100 or height < 100):
                    q = 100
                    image.save(thumb_name1,quality=q)
                else:
                    image.thumbnail(size, Image.ANTIALIAS)
                    q = 80
                    image.save(thumb_name1,quality=q)
            if w == '500' or w == 500:
                width, height = image.size
                split1 = i.pro_pic.path.rsplit('.', 1)
                thumb_name1 = '%s.%sx%s.%s' % (split1[0], w, h, split1[1])
                if (width < 500 or height < 500):
                    q = 100
                    image.save(thumb_name1,quality=q)
                else:
                    image.thumbnail(size, Image.ANTIALIAS)
                    q = 80
                    image.save(thumb_name1,quality=q)
            if w == '1000' or w == 1000:
                width, height = image.size
                split1 = i.pro_pic.path.rsplit('.', 1)
                thumb_name1 = '%s.%sx%s.%s' % (split1[0], w, h, split1[1])
                if (width < 1000 or height < 1000):
                    q = 100
                    image.save(thumb_name1,quality=q)
                else:
                    image.thumbnail(size, Image.ANTIALIAS)
                    q = 80
                    image.save(thumb_name1,quality=q)
        print (count-idx),' images remaining to compress'
    print "compression completed"