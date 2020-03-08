from datetime import datetime, timedelta

from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.postgres.fields import HStoreField, ArrayField
from .utils import get_user_model, get_model_from_name
from zap_apps.marketing.models import ACTION_TYPES
import pdb
# just using this to parse, but totally insane package naming...
# https://bitbucket.org/schinckel/django-timedelta-field/
import timedelta as djangotimedelta

MODEL_CHOICES = (
    ('ZapUser', 'zapuser'),
    ('ApprovedProduct', 'zap_catalogue'),
    ('Comments', 'zap_catalogue'),
)


class TargetUserGroup(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    lastchanged = models.DateTimeField(auto_now=True)
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='TargetUserGroup Name',
        help_text='A unique name for this TargetUserGroup.')
    description = models.TextField()
    enabled = models.BooleanField(default=False)
    # operator = models.CharField(max_length=5, choices=(('OR', 'OR operator'), ('AND', 'AND operator')), default="AND")
    # message_class = models.CharField(max_length=120, blank=True, default='default')

    def __unicode__(self):
        return self.name


class DripCampaign(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Drip Name',
        help_text='A unique name for this Drip Campaign.')
    description = models.TextField()
    campaign = models.CharField(max_length=30)


class Drip(models.Model):
    MODE_CHOICES = (
        ('email', 'Email'),
        ('push_notification', 'Push Notification'),
        ('sms', 'SMS'),
        # (4, 'Overlay')
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Drip Name',
        help_text='A unique name for this Drip.')
    description = models.TextField()
    parent = models.ForeignKey(DripCampaign, null=True, blank=True)
    enabled = models.BooleanField(default=False)
    bulk = models.BooleanField(default=False)
    target_group = models.ForeignKey(
        'TargetUserGroup', null=True, blank=True, related_name='target_drip')
    static_content_group = models.ForeignKey(
        'StaticContentGroup', null=True, blank=True, related_name='static_content_drip')
    content_group = models.ManyToManyField(
        'ContentGroup', blank=True, related_name='content_drip')
    trigger = models.ForeignKey(
        'Trigger', null=True, blank=True, related_name='trigger_drip')
    action = models.ForeignKey(
        'ActionGroup', null=True, blank=True, related_name='action_drip')

    # message_type = models.CharField(choices=MODE_CHOICES, max_length=2, default=1)
    # message_class = models.CharField(choices=MODE_CHOICES, max_length=120, blank=True, default='sms')
    # overlay = models.ForeignKey('marketing.Overlay')
    email = models.ForeignKey('drip.Email', null=True, blank=True)
    sms = models.ForeignKey('drip.SMS', null=True, blank=True)
    push_notif = models.ForeignKey(
        'drip.PushNotification', null=True, blank=True)
    repeat = models.BooleanField(default=False)
    time = models.TimeField(null=True, blank=True)
    scheduled_time = models.DateTimeField(null=True, blank=True)

    @property
    def drip(self):
        from zap_apps.drip.drips import DripBase
        drip = DripBase(drip_model=self)
        return drip

    def drip_with_context(self, *args, **kwargs):
        from zap_apps.drip.drips import DripBase
        drip = DripBase(self, context=kwargs['context'])
        return drip


class Email(models.Model):
    from_email = models.EmailField(null=True, blank=True,
                                   help_text='Set a custom from email.')
    # from_email_name = models.CharField(max_length=150, null=True, blank=True,
    #     help_text="Set a name for a custom from email.")
    subject_template = models.TextField(null=True, blank=True)
    body_html_template = models.TextField(null=True, blank=True,
                                          help_text='You will have settings and user in the context.')
    subject_context = HStoreField(null=True, blank=True)
    email_context = HStoreField(null=True, blank=True)


class SMS(models.Model):
    name = models.CharField(max_length=30)
    content = models.TextField()


class PushNotification(models.Model):
    name = models.CharField(max_length=30)
    content = models.TextField()
    image = models.ImageField(upload_to="uploads/notification_images/", null=True,blank=True)
    # extra = HStoreField(null=True, blank=True)


class SentDrip(models.Model):

    """
    Keeps a record of all sent drips.
    """
    date = models.DateTimeField(auto_now_add=True)

    # drip = models.ForeignKey('drip.TargetUserGroup', related_name='sent_drips')
    user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'), related_name='sent_drips',
                             on_delete=models.SET_NULL, null=True, blank=True)

    subject = models.TextField()
    body = models.TextField()
    from_email = models.EmailField(
        # For south so that it can migrate existing rows.
        null=True, default=None
    )
    from_email_name = models.CharField(max_length=150,
                                       # For south so that it can migrate
                                       # existing rows.
                                       null=True, default=None
                                       )
# class RelatedContent(models.Model):
#     model_choice = models.CharField(max_length=20, choices=MODEL_CHOICES, default='ZapUser')
#     key_name = models.CharField(max_length=20, null=True, blank=True)
#     content_rules = models.CharField(max_length=100)


class Trigger(models.Model):
    name = models.CharField(max_length=30, unique=True)
    model = models.CharField(
        max_length=20, choices=MODEL_CHOICES, default='ZapUser')
    option = models.CharField(
        max_length=10, choices=(('create', 'Create'), ('modify', 'Modify')))
    rules = models.ManyToManyField('TriggerRules', related_name='trigger', blank=True)
    # fields = ArrayField(
    #     HStoreField()
    # ,null=True, blank=True)
    # after_in_mins = models.IntegerField(default=0)
    # target_user_rules = models.ForeignKey('RelatedContent', related_name='trigger_user')
    # content_rules = models.ManyToManyField('RelatedContent', related_name='trigger_content')
    # rules = ArrayField(
    #     HStoreField()
    # ,null=True, blank=True)

METHOD_TYPES = (
    ('filter', 'Filter'),
    ('exclude', 'Exclude'),
)

LOOKUP_TYPES = (
    ('exact', 'exactly'),
    ('iexact', 'exactly (case insensitive)'),
    ('contains', 'contains'),
    ('icontains', 'contains (case insensitive)'),
    ('regex', 'regex'),
    ('iregex', 'contains (case insensitive)'),
    ('gt', 'greater than'),
    ('gte', 'greater than or equal to'),
    ('lt', 'less than'),
    ('lte', 'less than or equal to'),
    ('startswith', 'starts with'),
    ('endswith', 'starts with'),
    ('istartswith', 'ends with (case insensitive)'),
    ('iendswith', 'ends with (case insensitive)'),
    ('in', 'checks in a list with dynamic'),
)


class QuerySetRule(models.Model):

    date = models.DateTimeField(auto_now_add=True)
    lastchanged = models.DateTimeField(auto_now=True)

    target_group = models.ForeignKey(
        'TargetUserGroup', related_name='queryset_rules', null=True, blank=True)
    static_content_group = models.ForeignKey(
        'StaticContentGroup', related_name='static_queryset_rules', null=True, blank=True)
    content_group = models.ForeignKey(
        'ContentGroup', related_name='content_queryset_rules', null=True, blank=True)
    action_group = models.ForeignKey(
        'ActionGroup', related_name='content_queryset_rules', null=True, blank=True)


    method_type = models.CharField(
        max_length=12, default='filter', choices=METHOD_TYPES)
    field_name = models.CharField(
        max_length=128, verbose_name='Field name of User')
    lookup_type = models.CharField(
        max_length=12, default='exact', choices=LOOKUP_TYPES)

    field_value = models.CharField(max_length=255,
                                   help_text=('Can be anything from a number, to a string. Or, do ' +
                                              '`now-7 days` or `today+3 days` for fancy timedelta.'),
                                   null=True, blank=True)
    dynamic_value = models.ForeignKey('DynamicValue', null=True, blank=True)

    # def clean(self):

    #     User = get_user_model(self.content_group.model_choice if self.content_group else 'ZapUser')
    #     try:
    #         self.apply(User.objects.all())
    #     except Exception as e:
    #         raise ValidationError(
    #             '%s raised trying to apply rule: %s' % (type(e).__name__, e))

    @property
    def annotated_field_name(self):
        field_name = self.field_name
        if field_name.endswith('__count'):
            agg, _, _ = field_name.rpartition('__')
            field_name = 'num_%s' % agg.replace('__', '_')

        return field_name

    # def get_model_from_name(self, model_name):
    #     from django.apps import apps
    #     from zap_apps.drip.models import MODEL_CHOICES
    #     model_choiches_dict = dict(MODEL_CHOICES)
    #     # try:
    #     selected_model = apps.get_model(
    #         app_label=model_choiches_dict.get(model_name), model_name=model_name)
    #     return selected_model

    def get_dynamic_field_value(self, context):
        model_name = self.dynamic_value.model_choice
        selected_model = get_model_from_name(model_name)
        selected_model_id = context[model_name]
        selected_object = selected_model.objects.filter(id=selected_model_id)
        related_values = selected_object.values_list(
            self.dynamic_value.field_name, flat=True)
        if not self.lookup_type == 'in':
            return related_values[0]
        return related_values

    def apply_any_annotation(self, qs):
        if self.field_name.endswith('__count'):
            field_name = self.annotated_field_name
            agg, _, _ = self.field_name.rpartition('__')
            qs = qs.annotate(**{field_name: models.Count(agg, distinct=True)})
        return qs

    def filter_kwargs(self, qs, now=datetime.now, context=None):
        # Support Count() as m2m__count
        field_name = self.annotated_field_name
        field_name = '__'.join([field_name, self.lookup_type])
        if self.dynamic_value:
            field_value = self.get_dynamic_field_value(context)
        else:
            field_value = self.field_value

            # set time deltas and dates
            if self.field_value.startswith('now-'):
                field_value = self.field_value.replace('now-', '')
                field_value = now() - djangotimedelta.parse(field_value)
            elif self.field_value.startswith('now+'):
                field_value = self.field_value.replace('now+', '')
                field_value = now() + djangotimedelta.parse(field_value)
            elif self.field_value.startswith('today-'):
                field_value = self.field_value.replace('today-', '')
                field_value = now().date() - djangotimedelta.parse(field_value)
            elif self.field_value.startswith('today+'):
                field_value = self.field_value.replace('today+', '')
                field_value = now().date() + djangotimedelta.parse(field_value)

            # F expressions
            if self.field_value.startswith('F_'):
                field_value = self.field_value.replace('F_', '')
                field_value = models.F(field_value)

            # set booleans
            if self.field_value == 'True':
                field_value = True
            if self.field_value == 'False':
                field_value = False

        kwargs = {field_name: field_value}

        return kwargs

    def apply(self, qs, now=datetime.now):
        # pdb.set_trace()
        kwargs = self.filter_kwargs(qs, now)
        qs = self.apply_any_annotation(qs)

        if self.method_type == 'filter':
            return qs.filter(**kwargs)
        elif self.method_type == 'exclude':
            return qs.exclude(**kwargs)

        # catch as default
        return qs.filter(**kwargs)


class StaticContentGroup(models.Model):
    products = models.ManyToManyField(
        'zap_catalogue.ApprovedProduct', blank=True)
    users = models.ManyToManyField('zapuser.ZapUser', blank=True)

class ActionGroup(models.Model):
    
    mode = models.CharField(
        max_length=20, choices=ACTION_TYPES, default='newsfeed')
    date = models.DateTimeField(auto_now_add=True)
    lastchanged = models.DateTimeField(auto_now=True)
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='ActionGroup Name',
        help_text='A unique name for this ActionGroup.')
    description = models.TextField()
    enabled = models.BooleanField(default=False)
    model_choice = models.CharField(
        max_length=20, choices=MODEL_CHOICES, default='ZapUser')
    # key_name = models.CharField(max_length=20)
    # # operator = models.CharField(max_length=5, choices=(('OR', 'OR operator'), ('AND', 'AND operator')), default="AND")
    # message_class = models.CharField(max_length=120, blank=True, default='default')

    def __unicode__(self):
        return self.name



class ContentGroup(models.Model):
    MODE_CHOICES = (
        ('dynamic', 'dyncamic content'),
        ('personal', 'personal content'),
    )
    mode = models.CharField(
        max_length=20, choices=MODE_CHOICES, default='dynamic')
    date = models.DateTimeField(auto_now_add=True)
    lastchanged = models.DateTimeField(auto_now=True)
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='ContentGroup Name',
        help_text='A unique name for this ContentGroup.')
    description = models.TextField()
    enabled = models.BooleanField(default=False)
    model_choice = models.CharField(
        max_length=20, choices=MODEL_CHOICES, default='ZapUser')
    key_name = models.CharField(max_length=20)
    # operator = models.CharField(max_length=5, choices=(('OR', 'OR operator'), ('AND', 'AND operator')), default="AND")
    # message_class = models.CharField(max_length=120, blank=True, default='default')

    def __unicode__(self):
        return self.name


class TriggerRules(models.Model):
    name = models.CharField(max_length=20)
    SAVE_CHOICES = (
        ('presave', 'presave'),
        ('postsave', 'postsave')
        )
    LOOKUP_EVAL_TYPES = (
        ('equal', 'equal'),
        ('contains', 'contains'),
        ('gt', 'greater than'),
        ('gte', 'greater than or equal to'),
        ('lt', 'less than'),
        ('lte', 'less than or equal to'),
        ('startswith', 'starts with'),
        ('endswith', 'starts with'),
        ('in', 'checks in a list with dynamic'),
    )
    left_save_method = models.CharField(choices=SAVE_CHOICES, max_length=10, default='postsave')
    left_field_name = models.CharField(max_length=30)
    lookup_type = models.CharField(choices=LOOKUP_EVAL_TYPES, max_length=20, default='equal')
    right_save_method = models.CharField(choices=SAVE_CHOICES, max_length=10, null=True, blank=True)
    right_field_name =  models.CharField(max_length=30, null=True, blank=True)
    right_static = models.CharField(max_length=30, null=True, blank=True)



    def __unicode__(self):
        return self.name



class DynamicValue(models.Model):

    model_choice = models.CharField(
        max_length=20, choices=MODEL_CHOICES, default='ZapUser')
    field_name = models.CharField(
        max_length=128, verbose_name='Field name of User')

    def __unicode__(self):
        return self.model_choice + '---' + self.field_name
# class TriggerSetRule(models.Model):


#     model_choice = models.CharField(max_length=20, choices=MODEL_CHOICES, default='ZapUser')

#     method_type = models.CharField(max_length=12, default='filter', choices=METHOD_TYPES)
#     field_name = models.CharField(max_length=128, verbose_name='Field name of User')
#     lookup_type = models.CharField(max_length=12, default='exact', choices=LOOKUP_TYPES)

#     field_value = models.CharField(max_length=255,
#         help_text=('Can be anything from a number, to a string. Or, do ' +
#                    '`now-7 days` or `today+3 days` for fancy timedelta.'), null=True, blank=True)

#     def clean(self):
#         User = get_user_model(self.model_choice)
#         try:
#             self.apply(User.objects.all())
#         except Exception as e:
#             raise ValidationError(
#                 '%s raised trying to apply rule: %s' % (type(e).__name__, e))

#     @property
#     def annotated_field_name(self):
#         field_name = self.field_name
#         if field_name.endswith('__count'):
#             agg, _, _ = field_name.rpartition('__')
#             field_name = 'num_%s' % agg.replace('__', '_')

#         return field_name

#     def apply_any_annotation(self, qs):
#         if self.field_name.endswith('__count'):
#             field_name = self.annotated_field_name
#             agg, _, _ = self.field_name.rpartition('__')
#             qs = qs.annotate(**{field_name: models.Count(agg, distinct=True)})
#         return qs

#     def filter_kwargs(self, qs, now=datetime.now, context=None, drip=None):
#         # Support Count() as m2m__count
#         field_name = self.annotated_field_name
#         field_name = '__'.join([field_name, self.lookup_type])
#         # field_value = self.field_value
#         if self.field_value:
#             field_value = self.field_value


#         # if context and context['execute']:
#         field_value = context['context_value_dict'][self.field_name]
#         field_val = field_value

#         # set time deltas and dates
#         if field_val.startswith('now-'):
#             field_value = field_val.replace('now-', '')
#             field_value = now() - djangotimedelta.parse(field_value)
#         elif field_val.startswith('now+'):
#             field_value = field_val.replace('now+', '')
#             field_value = now() + djangotimedelta.parse(field_value)
#         elif field_val.startswith('today-'):
#             field_value = field_val.replace('today-', '')
#             field_value = now().date() - djangotimedelta.parse(field_value)
#         elif field_val.startswith('today+'):
#             field_value = field_valfield_val.replace('today+', '')
#             field_value = now().date() + djangotimedelta.parse(field_value)

#         # F expressions
#         if field_val.startswith('F_'):
#             field_value = field_val.replace('F_', '')
#             field_value = models.F(field_value)

#         # set booleans
#         if field_val == 'True':
#             field_value = True
#         if field_val == 'False':
#             field_value = False

#         kwargs = {field_name: field_value}

#         return kwargs

#     def apply(self, qs, now=datetime.now):
#         # pdb.set_trace()
#         kwargs = self.filter_kwargs(qs, now)
#         qs = self.apply_any_annotation(qs)

#         if self.method_type == 'filter':
#             return qs.filter(**kwargs)
#         elif self.method_type == 'exclude':
#             return qs.exclude(**kwargs)

#         # catch as default
#         return qs.filter(**kwargs)
