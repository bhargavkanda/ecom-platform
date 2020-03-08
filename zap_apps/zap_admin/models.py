from django.db import models

# Create your models here.
ADMIN_STATUS = [(0,'Success'), (1, 'Confirmed'), (2, 'Picked Up'), (3, 'Out For Delivery'), 
        (4, 'Delivered'), (5, 'Returning To Origin'), (6, 'Returned To Origin')]

# class MarketingImage(models.Model):
#     image = models.ImageField(upload_to="uploads/marketing/")