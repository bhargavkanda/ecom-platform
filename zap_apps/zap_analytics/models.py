from django.contrib.postgres.fields import IntegerRangeField, ArrayField, JSONField
from django.db import models

SORT_OPTIONS = (
    (0, 'relevance'),
	(1, '-listing_price'),
	(2, 'listing_price'),
	(3, 'loves'),
	(4, '-discount'),
)

NOTIFICATION_TYPE = (
    ('P', 'product'),
    ('M', 'marketing'),
)

LOCATION_CHOICES = (
    ('D', 'discover'),
    ('B', 'buy'),
    ('F', 'filtered_list'),
    ('S', 'search_results'),
)

USER_ACTIONS = (
    (1, 'ProductView'),
    (2, 'ProfileView'),
    (3, 'Filter'),
    (4, 'Search'),
    (5, 'Sort'),
    (6, 'Notification'),
)

EVENT_CHOICES = (
    ('love', 'Love'),
    ('admire', 'Admire'),
    ('comment_on_product', 'Comment on Product'),
    ('add_to_tote', 'Add to Tote'),
    ('remove_from_tote', 'Remove from Tote'),
    ('upload_product', 'Upload Product'),
    ('write_blog', 'Write Blog'),
    ('mention', 'Mention'),
    ('comment_on_blog', 'Comment on Blog'),
    ('edit_profile', 'Edit Profile'),
    ('click', 'Click'),
    ('page_change', 'Page Change'),
    ('zoom_image', 'Zoom Image'),
    ('pincode_check', 'Pincode Check'),
    ('invite_user', 'Invite User'),
    ('transaction', 'Transaction'),
    ('checkout_step', 'Checkout Step'),
    ('search', 'Search'),
    ('filter', 'Filter'),
    ('notification', 'Notification'),
    ('impression', 'Impression'),
    ('pre_launch_page_visits', 'Luxury Brand Pre Launch page Visit'),
    ('pre_launch_cta', 'Pre Launch CTA'),
    ('pre_launch_share_cta', 'Pre Launch Share CTA'),
)


class ProductAnalytics(models.Model):
    product = models.ForeignKey('zap_catalogue.ApprovedProduct', null=True, blank=True, related_name='product_analytics')
    time = models.DateTimeField(auto_now=True)
    platform = models.CharField(max_length=10, blank=True, null=True)
    user = models.ForeignKey('zapuser.ZapUser', null=True, blank=True, default=1, related_name='product_tracking')

    def __unicode__(self):
        return 'Product id {0} by user {1} at {2}'.format(str(self.product.id), self.user.zap_username, self.time)


class ProfileAnalytics(models.Model):
    profile = models.ForeignKey('zapuser.UserProfile', null=True, blank=True, related_name='profile_analytics')
    time = models.DateTimeField(auto_now=True)
    platform = models.CharField(max_length=10, blank=True, null=True)
    user = models.ForeignKey('zapuser.ZapUser', null=True, blank=True, default=1, related_name='profile_tracking')

    def __unicode__(self):
        return 'User Profile id {0} by user {1} at {2}'.format(str(self.profile.id), self.user.zap_username, self.time)


class SortAnalytics(models.Model):
    sort_option = models.IntegerField(choices=SORT_OPTIONS, default=0)
    time = models.DateTimeField(auto_now=True)
    platform = models.CharField(max_length=10, blank=True, null=True)
    user = models.ForeignKey('zapuser.ZapUser', null=True, blank=True, default=1, related_name='sort_tracking')

    def __unicode__(self):
        return 'Sorted by {0} by user {1} at {2}'.format(str(self.sort_option), self.user.zap_username, self.time)


class SearchAnalytics(models.Model):
    search_query = models.CharField(max_length=30, null=True, blank=True)
    category = models.ManyToManyField('zap_catalogue.Category', blank=True, related_name='category_search')
    subcategory = models.ManyToManyField('zap_catalogue.SubCategory', blank=True, related_name='subcategory_search')
    color = models.ManyToManyField('zap_catalogue.Color', blank=True, related_name='color_search')
    style = models.ManyToManyField('zap_catalogue.Style', blank=True, related_name='style_search')
    occasion = models.ManyToManyField('zap_catalogue.Occasion', blank=True, related_name='occasion_search')
    brand = models.ManyToManyField('zap_catalogue.Brand', blank=True, related_name='brand_search')
    time = models.DateTimeField(auto_now=True)
    platform = models.CharField(max_length=10, blank=True, null=True)
    user = models.ForeignKey('zapuser.ZapUser', null=True, blank=True, default=1, related_name='search_tracking')

    def __unicode__(self):
        return 'Search query \"{0}\" by user {1} at {2} '.format(self.search_query, self.user.zap_username, self.time)


class FilterAnalytics(models.Model):
    category = models.ManyToManyField('zap_catalogue.Category', blank=True, related_name='category_filter')
    subcategory = models.ManyToManyField('zap_catalogue.SubCategory', blank=True, related_name='subcategory_filter')
    color = models.ManyToManyField('zap_catalogue.Color', blank=True, related_name='color_filter')
    style = models.ManyToManyField('zap_catalogue.Style', blank=True, related_name='style_filter')
    occasion = models.ManyToManyField('zap_catalogue.Occasion', blank=True, related_name='occasion_filter')
    brand = models.ManyToManyField('zap_catalogue.Brand', blank=True, related_name='brand_filter')
    platform = models.CharField(max_length=10, blank=True, null=True)
    price = ArrayField(ArrayField(models.IntegerField(null=True, blank=True), size=2), null=True, blank=True)
    size = models.ManyToManyField('zap_catalogue.Size', blank=True, related_name='size_filter')
    time = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('zapuser.ZapUser', null=True, blank=True, default=1, related_name='filter_tracking')

    def __unicode__(self):
        return 'Filter applied by user {0} at {1} '.format(self.user.zap_username, self.time)


class NotificationAnalytics(models.Model):
    notification = models.ForeignKey('marketing.Notifs', null=True, blank=True, related_name='notification_analytics')
    sent_time = models.DateTimeField(null=True, blank=True)
    open_time = models.DateTimeField(null=True, blank=True)
    platform = models.CharField(max_length=10, blank=True, null=True)
    user = models.ForeignKey('zapuser.ZapUser', null=True, blank=True, default=1, related_name='notification_tracking')
    notification_type = models.CharField(choices=NOTIFICATION_TYPE, null=True, blank=True, max_length=1)

    def __unicode__(self):
        return '{0} notification sent to user {1} at {2}'.format(self.notification_type, self.user.zap_username, self.time)


class ImpressionAnalytics(models.Model):
    product = models.ForeignKey('zap_catalogue.ApprovedProduct', null=True, blank=True, related_name='product_impressions')
    rank = models.IntegerField(null=True, blank=True, default=1)
    page_num = models.IntegerField(null=True, blank=True, default=1)
    location = models.CharField(choices=LOCATION_CHOICES, max_length=1, default='D')
    time = models.DateTimeField(auto_now=True)
    platform = models.CharField(max_length=10, blank=True, null=True)
    user = models.ForeignKey('zapuser.ZapUser', null=True, blank=True, default=1, related_name='impression_tracking')

    def __unicode__(self):
        return 'Impression of product id {0} at location {1} on page number {2} at rank {3}'.format(self.product.id, self.page_num, self.location, self.rank)


class UserAction(models.Model):
    user = models.ForeignKey('zapuser.ZapUser', null=True, blank=True, default=1, related_name='user_action_tracking')
    action = models.IntegerField(choices=USER_ACTIONS, null=True, blank=True, default=1)
    time = models.DateTimeField(auto_now=True)
    data = JSONField(null=True, blank=True, default=dict())

    def __unicode__(self):
        return 'UserAction: Action - {0}'.format(self.action)


"""
Analytics - Single End Point
All Events
"""
class AnalyticsSessions(models.Model):
    unique_session = models.CharField(max_length=200)
    user = models.ForeignKey('zapuser.ZapUser', null=True, blank=True, default=1, related_name='user_sessions')
    platform = models.CharField(max_length=30)
    start_timestamp = models.DateTimeField(auto_now_add=True)
    end_timestamp = models.DateTimeField(null=True, blank=True)
    start_page = models.CharField(max_length=500)
    end_page = models.CharField(max_length=500)
    device_id = models.CharField(max_length=500)
    source = models.CharField(max_length=500)
    campaign = models.CharField(max_length=500)

    def __unicode__(self):
        return 'New Session from {0} and source - {1}'.format(self.platform, self.source)

"""
All user initiated actions goes here

-------------------------------DATA STORAGE FORMATS--------------------------------
Events:
-------

Note: 
1. Ignore the square braces for the format, each property is seperated by a tab
2. If a field doesn't exist/apply for a given entry, pass null for it


love                  [user_id  product_id]
admire                [admiring_user_id  admired_user_id]
comment_on_product    [user_id  product_id]
add_to_tote           [user_id  product_id  size  quantity  price]
remove_from_tote      [user_id  product_id  size  quantity  price]
upload_product        [user_id  product_id  price  condition]
write_blog            [user_id  blog_id]
mention               [commenting_user_id  comment_id  mentioned_user_id  product_id]
comment_on_blog       [user_id  blog_comment_id  blog_id]
edit_profile          [user_id  name/address/bank_account/description/gender/dob/location]
click                 [user_id  entity  context]
page_change           [user_id  new_page  old_page  page_view_starttime  page_view_endtime]
zoom_image            [user_id  product_id  unique_zooms]
pincode_check         [user_id  pincode_checked]
invite_user           [user_id  invite_channel]
transaction           [user_id  transaction_id  transaction_amount]
checkout_step         [user_id  cart_id  step  value_of_cart]
search                [user_id  search_query  search_context/page  number_of_results]
filter                [user_id  category  subcategory  color  style  occasion  brand  price  size]
notification          [user_id  notification_id  sent_time  open_time  notification_type]
impression            [user_id  rank  page_num  location]
pre_launch_page_visits          [campaign_id    source]
pre_launch_cta                  [campaign_id    email_id    source]
pre_launch_social_share_cta     [campaign_id     medium     source]
"""
class AnalyticsEvents(models.Model):
    name = models.CharField(choices=EVENT_CHOICES, max_length=500, default='love')
    session = models.ForeignKey('AnalyticsSessions', related_name="event_session")
    timestamp = models.DateTimeField(auto_now=True)
    event_details = JSONField()

    def __unicode__(self):
        return 'New action for {0}'.format(self.name)

class ClevertapEvents(models.Model):
    name = models.CharField(max_length=500)
    event_details = JSONField()

    def __unicode__(self):
        return 'New action for {0}'.format(self.name)
