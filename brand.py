import sys,os,csv
import django
os.environ["DJANGO_SETTINGS_MODULE"] = "zapyle_new.settings.local"
django.setup()
from zap_apps.zap_catalogue.models import Brand
from zap_apps.zapuser.models import BrandTag
with open('brand.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        row = filter(None, row)
        if row:
            try:
                brand = Brand.objects.get(brand__icontains=row[0])
            except Brand.DoesNotExist:
                print row, "DoesNotExist"
                row1 = row[0].split()
                for i in row1:
                    try:
                        brand = Brand.objects.get(brand__icontains=i)
                        print "Solved"
                        break
                    except Brand.DoesNotExist:
                        pass
                    except Brand.MultipleObjectsReturned:
                        pass
            except Brand.MultipleObjectsReturned:
                brand = Brand.objects.get(brand__iexact=row[0])
                print row, "MultipleObjectsReturned"
            if brand:
                row2 = row[1:]
                for i in row2:
                    try:
                        b_tag = BrandTag.objects.get(tag__icontains=i.strip())
                    except BrandTag.DoesNotExist:
                        print i, "DoesNotExist"
                        row1 = i.split()
                        for j in row1:
                            try:
                                b_tag = BrandTag.objects.get(tag__icontains=j)
                                print "Solved"
                                break
                            except BrandTag.DoesNotExist:
                                pass
                            except BrandTag.MultipleObjectsReturned:
                                pass
                    except BrandTag.MultipleObjectsReturned:
                        try:
                            b_tag = BrandTag.objects.get(tag__iexact=i.strip())
                        except BrandTag.DoesNotExist:
                            print i, "MultipleObjectsReturned"
                    if b_tag:
                        brand.tags.add(b_tag)
        brand = None
