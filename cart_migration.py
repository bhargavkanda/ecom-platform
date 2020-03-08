import os
import django
os.environ["DJANGO_SETTINGS_MODULE"] = "zapyle_new.settings.local"
django.setup()

from zap_apps.order.models import OrderedProduct, Order
from zap_apps.zap_catalogue.models import ProductImage
def size_type(foo):
    return foo.size_type or (
        "UK" if foo.product_category.parent.category_type == 'C' else 
        "US" if foo.product_category.parent.category_type == 'FW' else "FREESIZE")

def get_size(o, p):
    t = size_type(p)
    if t == 'FREESIZE':
        return "FREESIZE"
    if t == 'US':
        return o.size.us_size
    if t == 'UK':
        return o.size.uk_size
    if t == 'EU':
        return o.size.eu_size
from django.core.files import File  # you need this somewhere
from zap_apps.zap_catalogue.product_serializer import ProductImageSerializer
import base64

for i in Order.objects.all():
    product = i.product
    with open(product.images.all().order_by('id')[0].image.path, "rb") as f:
        data = f.read()
        data = data.encode("base64")
    img_serializer = ProductImageSerializer(
                data={'image': data})
    img_serializer.is_valid()   
    img_serializer.save()    # 
    op = OrderedProduct()
    op.image_id = img_serializer.data['id']
    op.title = product.title
    op.description = product.description
    op.style = product.style.style_type if product.style else ''
    op.brand = product.brand.brand
    op.original_price = product.original_price
    op.listing_price = product.listing_price
    op.size = get_size(i, product)
    op.occasion = product.occasion.name if product.occasion else ''
    op.product_category = product.product_category.name
    op.color = product.color.name if product.color else ''
    op.age = product.get_age_display()
    op.condition = product.get_condition_display()
    op.discount = product.discount
    op.percentage_commission = product.percentage_commission
    op.save()
    i.ordered_product = op
    i.save()
