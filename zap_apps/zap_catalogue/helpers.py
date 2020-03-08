from zap_apps.zap_catalogue.models import NumberOfProducts, ApprovedProduct
from zap_apps.cart.models import Cart


def checkAvailability(product, size, quantity):
    if quantity < 1:
        return False
    try:
        n_o_p = NumberOfProducts.objects.get(product=product, size=size)
    except NumberOfProducts.DoesNotExist:
        return False
    print "avilable-qty-> {}".format(n_o_p.quantity)
    print "requested-qty-> {}".format(quantity)
    if n_o_p.quantity >= int(quantity):
        return True
    return False


def checkCartAvailibility(cart_id):
    cart = Cart.objects.get(id=cart_id)
    for item in cart.item.all():
        if not checkAvailability(item.product, item.size, item.quantity):
            return False
    return True


def reduceQuantity(product, size, quantity):
    try:
        # pdb..set_trace()
        availablequantity = NumberOfProducts.objects.get(
            product=product, size=size)
        availablequantity.quantity = availablequantity.quantity - quantity
        availablequantity.save()
        if (availablequantity.quantity == 0 and ApprovedProduct.objects.get(id=product).user.user_type == 'normal') or (sum(list(NumberOfProducts.objects.filter(product=product).values_list('quantity', flat=True))) == 0 and ApprovedProduct.objects.get(id=product).user.user_type == 'store_front'):
            product_object = ApprovedProduct.objects.get(id=product)
            product_data = {'sale': '3'}
            # UPDATE APPROVED PRODUCT WITH SERIALIZER
            # serializer=AlbumSerializer(data=album_data)
            # if serializer.is_valid():
            #     serializer.update(album, serializer.validated_data)

        return True
    except:
        return False


def reduceCartQuantity(cart_id):
    cart = Cart.objects.get(id=cart_id)

    for item in cart.items.all():
        if not reduceQuantity(item.product, item.size, item.quantity):
            return False
    return True


def increaseQuantity(product, size, quantity):
    try:
        availablequantity = NumberOfProducts.objects.get(
            product=product, size=size)
        availablequantity.quantity = availablequantity.quantity + quantity
        availablequantity.save()
  #  if availablequantity.quantity > 0 and product.user.user_type == 'normal':
        product_object = ApprovedProduct.objects.get(id=product)
        product_data = {'sale': '2'}
        # UPDATE APPROVED PRODUCT WITH SERIALIZER
        # serializer=AlbumSerializer(data=album_data)
        # if serializer.is_valid():
        #     serializer.update(album, serializer.validated_data)
        return True
    except:
        return False


def increaseCartQuantity(cart_id):
    print 'test3000'
    cart = Cart.objects.get(id=cart_id)
    print cart, 'function sincreaseQuantity'
    for item in cart.items.all():
        if not increaseQuantity(item.product, item.size, item.quantity):
            return False
    return True
