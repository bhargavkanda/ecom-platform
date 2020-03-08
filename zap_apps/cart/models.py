from django.db import models
from django.conf import settings
# Create your models here.




class DeletedItem(models.Model):
    user = models.ForeignKey(
        'zapuser.ZapUser', blank=True, null=True, related_name="deleted_item")
    product = models.ForeignKey(
        'zap_catalogue.ApprovedProduct', related_name='deleted_item')
    size = models.ForeignKey('zap_catalogue.Size', related_name='deleted_item')


class CustomItemData(models.Model):
    note = models.CharField(max_length=300, null=True, blank=True)
    lehenga_length = models.CharField(max_length=10, null=True, blank=True)

class Item(models.Model):
    cart = models.ForeignKey(
        'cart.Cart', related_name="item", null=True, blank=True)
    product = models.ForeignKey(
        'zap_catalogue.ApprovedProduct', related_name='cart_item')
    expires_at = models.DateTimeField(blank=True, null=True)
    size = models.ForeignKey('zap_catalogue.Size', related_name='item_size')
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True, editable=False)
    customize_data = models.ForeignKey('cart.CustomItemData', null=True, blank=True)
    offer = models.ForeignKey('offer.ZapOffer', null=True, blank=True, on_delete=models.SET_NULL, related_name='applied_item')
    def delete(self, *args, **kwargs):
        DeletedItem.objects.get_or_create(product=self.product, size=self.size, user=self.cart.user)
        super(Item, self).delete(*args, **kwargs)
    # sold_out = models.BooleanField(default=False)
    def get_size_type(self):
        return self.product.size_type or (
            "UK" if self.product.product_category.parent.category_type == 'C' else
            "US" if self.product.product_category.parent.category_type == 'FW' else "FREESIZE")
    def get_size_string(self):
        size_type = self.get_size_type()
        if size_type == "FREESIZE":
            return "FREESIZE"
        if size_type == "US":
            return "US_{}".format(self.size.us_size)
        if size_type == "UK":
            return "UK_{}".format(self.size.uk_size)
        if size_type == "EU":
            return "EU_{}".format(self.size.eu_size)

    @property
    def selling_price(self):
        if self.offer:
            return self.product.get_offer_price(self.offer.id)
        else:
            return self.product.listing_price

    def price(self):
        return (self.selling_price * self.quantity) + (float(settings.SHIPPING_CHARGE) if self.selling_price < float(settings.SHIPPING_CHARGE_PRICE_LIMIT) else 0.0)

    def __unicode__(self):
        if self.cart:
            return (self.cart.user.zap_username or self.cart.user.email or "") +": "+ str(self.product.id) + ' -- ' + self.product.title + " -- " + str(self.added_at)
        else:
            return str(self.product.id) + ' -- ' + self.product.title + str(self.added_at)
    # shipping_charge = models.IntegerField(default=0)
    # def save(self, *args, **kwargs):
    #     self.shipping_charge = settings.SHIPPING_CHARGE if self.product.original_price < settings.SHIPPING_CHARGE_PRICE_LIMIT else 0
    #     super(Item, self).save(*args, **kwargs)

class Cart(models.Model):
    user = models.OneToOneField(
        'zapuser.ZapUser', blank=True, null=True, related_name="user_cart")
    offer = models.ForeignKey('offer.ZapOffer', null=True, blank=True, on_delete=models.SET_NULL, related_name='applied_cart')
    delivery_address = models.ForeignKey(
        'address.Address', related_name='buyer_address', null=True, blank=True)

    def offer_discount(self):
        return self.offer.get_benefit(self.user.id) if self.offer else 0

    def total_original_price(self):
        items = self.item.all()
        return sum(map(lambda x: (x.product.original_price * x.quantity), items))

    def total_listing_price(self):
        items = self.item.all()
        return sum(map(lambda x: (x.selling_price * x.quantity), items))

    def seller_discount(self):
        items = self.item.all()
        return sum(map(lambda x: (x.product.original_price * x.quantity), items)) - sum(map(lambda x: (x.product.listing_price * x.quantity), items))

    def zapyle_discount(self):
        items = self.item.all()
        return (sum(map(lambda x: (x.product.listing_price * x.quantity), items)) - sum(map(lambda x: (x.selling_price * x.quantity), items))) + self.offer_discount()

    def total_discount(self):
        return self.seller_discount() + self.zapyle_discount()

    def total_shipping_charge(self):
        items = self.item.all()
        return sum(map(lambda x: settings.SHIPPING_CHARGE if x.selling_price < settings.SHIPPING_CHARGE_PRICE_LIMIT else 0, items))

    def total_price_with_shipping_charge(self):
        items = self.item.all()
        return (sum(map(lambda x: (x.selling_price * x.quantity) + (settings.SHIPPING_CHARGE if x.selling_price < settings.SHIPPING_CHARGE_PRICE_LIMIT else 0), items))) - self.offer_discount()

    def is_empty(self):
        return self.item.all().count() == 0

    def __unicode__(self):
        return self.user.zap_username or self.user.email or ""
# class Cart(models.Model):
#     user = models.ForeignKey(
#         'zapuser.ZapUser', blank=True, null=True, related_name="user_cart")
#     items = models.ManyToManyField('cart.Item')
#     # total_price = models.FloatField()
#     # final_price = models.FloatField()
#     delivery_address = models.ForeignKey(
#         'address.Address', related_name='buyer_address', null=True, blank=True)
#     coupon = models.ForeignKey('coupon.Coupon', null=True, blank=True, on_delete=models.SET_NULL)
#     success = models.BooleanField(default=False)
#     shipping_charge = models.FloatField(null=True, blank=True, default=0)

#     # zapcash_used = models.
#     # quantity = models.IntegerField(default=1)_

#     def add_shipping_charge_to_cart(self):
#         total_price = 0
#         for item in self.items.all():
#             total_price += item.price * item.quantity
#         self.shipping_charge = settings.SHIPPING_CHARGE if total_price < settings.SHIPPING_CHARGE_PRICE_LIMIT else 0
#         self.save()
#         return True

#     @property
#     def total_price(self):
#         total_price = 0
#         for item in self.items.all():
#             total_price += item.price * item.quantity
#         return total_price

#     @property
#     def cart_price(self):
#         total_price = 0
#         for item in self.items.all():
#             total_price += item.price * item.quantity
#         return (total_price + settings.SHIPPING_CHARGE) if total_price < settings.SHIPPING_CHARGE_PRICE_LIMIT else total_price

#     @property
#     def cart_price_after_coupon(self):
#         total_price = self.cart_price
#         if self.coupon:
#             print 'test1'
#             if self.coupon.abs_discount:
#                 discount = self.coupon.abs_discount
#             elif self.coupon.perc_discount:
#                 discount = (self.coupon.perc_discount * total_price) / 100
#             print discount, '  -- ', self.coupon.max_discount
#             discount = min(discount, self.coupon.max_discount or discount)

#             return int(round(total_price - discount))
#         return int(round(total_price))

#     @property
#     def get_coupon_discount(self):
#         if self.coupon:
#             total_price = 0
#             for item in self.items.all():
#                 total_price += item.price * item.quantity
#             print 'test1'
#             if self.coupon.abs_discount:
#                 discount = self.coupon.abs_discount
#             elif self.coupon.perc_discount:
#                 discount = (self.coupon.perc_discount * total_price) / 100
#             discount = min(discount, self.coupon.max_discount or discount)

#             return discount
#         return 0
