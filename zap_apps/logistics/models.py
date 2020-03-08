from django.db import models

# Create your models here.
LOGISTICS_PARTNERS = (
    ('DL', 'Delhivery'),
    ('PR', 'Parcelled'),
    ('ZP', 'Zapyle Delivery'),
    ('SR', 'Self Returns'),
    ('AR', 'Aramex')
)


# class Pincode(models.Model):
#     pincode = models.CharField(max_length=6)
#     pickup_partners = models.ManyToManyField(choices = LOGISTICS_PARTNERS)
#     delivery_partners = models.ManyToManyField(choices = LOGISTICS_PARTNERS)
LOGISTICS_STATUS = {
    'DL': [('Success', 0), ('Manifested', 1), ('In Transit', 2), ('Dispatched', 3), ('Pending', 3),
           ('Delivered', 4), ('Returned', 5), ('RTO', 6)],
    'PR': [('Success', 0), ('Confirmed', 1), ('On Hold', 1), ('On Our Way', 1), ('Picked Up', 2),
           ('Received At Hub', 2), ('Dispatched From Origin Hub',
                                    2), ('In Transit', 2), ('Out For Delivery', 3),
           ('On Our Way For Delivery', 3), ('On Hold During Delivery',
                                            3), ('Delivery Attempted', 3), ('Delivered', 4),
           ('Returning To Origin', 5), ('Returned To Origin', 6)],
    'ZL': [('Success', 0), ('Manifested', 1), ('Picked Up', 2), ('Dispatched', 3), ('Delivered', 4),
           ('Returned', 5), ('RTO', 6)],
    'SR': [('Manifested', 1), ('Delivered', 4), ('Returned', 5), ('RTO', 6)]
}

"""
Pincodes servicible by delhivery 
"""
class DelhiveryPincode(models.Model):
    pincode = models.CharField(max_length=6)
    prepaid = models.CharField(max_length=1)
    cash = models.CharField(max_length=1)
    cod = models.CharField(max_length=1)
    repl = models.CharField(max_length=1)
    dispatch_center = models.CharField(max_length=100)
    state_code = models.CharField(max_length=100)
    coc_code = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    def __unicode__(self):
        return unicode(self.pincode)

"""
This contains evaluated logistics partner for either orders or returns.
"""
class Logistics(models.Model):

    orders = models.ManyToManyField(
        'order.Order',  blank=True, related_name='order_logistic')
    returns = models.ManyToManyField(
        'order.Return', blank=True, related_name='return_logistic')
    confirmed_at = models.DateTimeField(auto_now_add=True)
    consignee = models.ForeignKey(
        'address.Address', related_name='buyer_logistics')
    consignor = models.ForeignKey(
        'address.Address', related_name='seller_logistics')
    # zap_inhouse = models.BooleanField(default=False)
    # reached_zapyle = models.BooleanField(default=False)

    triggered_pickup = models.BooleanField(default=False)
    # status = models.IntegerField(null=True, blank=True)
    delivery_time = models.DateTimeField(null=True, blank=True)

    pickup_partner = models.CharField(
        null=True, blank=True, max_length=3, choices=LOGISTICS_PARTNERS)
    product_delivery_partner = models.CharField(
        null=True, blank=True, max_length=3, choices=LOGISTICS_PARTNERS)

    def __unicode__(self):
        return unicode(self.id)+' | '+ unicode(self.orders.values_list('id', flat=True))+' | '+ unicode(self.returns.values_list('id', flat=True))

"""
Contains response details from APIs of different logistics partner.
"""
class LogisticsLog(models.Model):
    partner = models.CharField(max_length=3, choices=LOGISTICS_PARTNERS)
    # pickup_notified = models.BooleanField(default=False)

    logistics = models.ForeignKey(
        'logistics.Logistics', related_name='logistics_log')
    # partner = models.CharField(max_length=3, choices = LOGISTICS_PARTNERS)
    returns = models.BooleanField(default=False)
    waybill = models.CharField(max_length=20)
    # barcode = models.CharField(max_length=200, null=True, blank=True)
    log_status = models.IntegerField(null=True, blank=True)
    pickup = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    track = models.BooleanField(default=False)
    updated_time = models.DateTimeField(auto_now=True)
    # status_time = models.DateTimeField(null=True, blank=True)
    whole_response = models.CharField(max_length=3000)
    error_message = models.CharField(max_length=200, null=True, blank=True)
    logistics_ref = models.CharField(max_length=40, null=True, blank=True)
    extra = models.CharField(max_length=1000, null=True, blank=True)
    rejected = models.BooleanField(default=False)
    # product_verified = models.BooleanField(default=False)

# documents_sent_at = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.waybill)+' | '+unicode(self.logistics.orders.values_list('id', flat=True))+' | '+unicode(self.logistics.returns.values_list('id', flat=True))

"""
Aramex Status Codes
"""
class AramexStatus(models.Model):
    status_code = models.CharField(max_length=10)
    problem_code = models.CharField(max_length=5, null=True, blank=True)
    track_code = models.CharField(max_length=10)
    condition_code = models.CharField(max_length=10, null=True, blank=True)
    code_description = models.CharField(max_length=100)
    customer_description = models.CharField(max_length=500)
    logistic_status = models.IntegerField(default=0)

    def __unicode__(self):
        return unicode(self.status_code) + "---" + unicode(self.problem_code)
