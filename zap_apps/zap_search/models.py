from django.db import models


SEARCH_ENDPOINT_TYPES = (
    ('SR', 'search_results'),
    ('SS', 'search_suggestions'),
)

SEARCH_TABS = (
    ('P', 'product'),
    ('C', 'closet'),
)


class SearchString(models.Model):
    search_query = models.CharField(max_length=30, null=True, blank=True)
    category = models.ManyToManyField('zap_catalogue.Category', blank=True, related_name='category_search_query')
    subcategory = models.ManyToManyField('zap_catalogue.SubCategory', blank=True, related_name='subcategory_search_query')
    color = models.ManyToManyField('zap_catalogue.Color', blank=True, related_name='color_search_query')
    style = models.ManyToManyField('zap_catalogue.Style', blank=True, related_name='style_search_query')
    occasion = models.ManyToManyField('zap_catalogue.Occasion', blank=True, related_name='occasion_search_query')
    brand = models.ManyToManyField('zap_catalogue.Brand', blank=True, related_name='brand_search_query')
    time = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('zapuser.ZapUser', null=True, blank=True, default=1, related_name='search_query_tracking')
    endpoint_type = models.CharField(choices=SEARCH_ENDPOINT_TYPES, max_length=2, default='SR', null=True, blank=True)
    tab = models.CharField(choices=SEARCH_TABS, max_length=1, default='P', null=True, blank=True)

    def __unicode__(self):
        return 'Search query \"{0}\" by user {1} at {2} '.format(self.search_query, self.user.zap_username, self.time)