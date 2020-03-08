import operator
import functools
from django.db.models.query import QuerySet
from django.conf import settings
from django.db.models import Q
from django.template import Context, Template
from django.utils.module_loading import import_module
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from zap_apps.zap_notification.views import ZapEmail, PushNotification, ZapSms
from zap_apps.zap_catalogue.models import ApprovedProduct
from zap_apps.zapuser.models import ZapUser
from .models import SentDrip
from .utils import get_user_model
import ast
from .drip_serializer import ContentProductSerializer, ContentUserSerializer
try:
    from django.utils.timezone import now as conditional_now
except ImportError:
    from datetime import datetime
    conditional_now = datetime.now


import logging
import pdb



def configured_message_classes():
    conf_dict = getattr(settings, 'DRIP_MESSAGE_CLASSES', {})
    conf_dict['email'] = 'zap_apps.drip.drips.DripEmail'
    conf_dict['sms'] = 'zap_apps.drip.drips.DripSMS'
    conf_dict['push_notification'] = 'zap_apps.drip.drips.DripPush'
    return conf_dict


def message_class_for(name):
    path = configured_message_classes()[name]
    mod_name, klass_name = path.rsplit('.', 1)
    mod = import_module(mod_name)
    klass = getattr(mod, klass_name)
    return klass


class DripSMS(object):

    def __init__(self, drip_base, user=None, bulk=False):
        self.drip_base = drip_base
        self.user = user
        # self.context = {'user': self.user}
        self.bulk = bulk

    def send(self, **kwargs):
        sms = ZapSms()
        if self.bulk:
            content = self.drip_base.drip_model.sms.content
            full_nums = ",".join(filter(
                None, [i.phone_number[-10:] for i in user if hasattr(i, 'phone_number') and i.phone_number]))
        else:
            t = Template(self.drip_base.drip_model.sms.content)
            try:
                content = t.render(
                    Context(self.drip_base.get_content_groups_data(context=kwargs['context'])))
            except:
                content = t.render(
                    Context(self.drip_base.get_content_groups_data()))
            full_nums = self.user.phone_number
        sms.send_sms(full_nums, content)
        return None


class DripPush(object):

    def __init__(self, drip_base, user=None, bulk=False):
        self.drip_base = drip_base
        self.target_user = user
        if not (isinstance(self.target_user, list) or isinstance(self.target_user,QuerySet)):
            self.target_user = [self.target_user]
        # self.context = {'user': self.user}
        self.bulk = bulk





    def get_extra_data(self, **kwargs):
        sent_time = conditional_now()
        extra = {}
        data = self.drip_base.get_action_data(context=kwargs['context'])
        if self.drip_base.drip_model.action.mode == 'product':
            product = ApprovedProduct.ap_objects.get(id=data[0].id)
            extra = {
                'action': 'product',
                'product_id': product.id,
                'product_title': product.title,
                'product_img_url': product.images.all()[0].image.url_100x100,
                'product_sale': product.get_sale_display(),

            }
        elif self.drip_base.drip_model.action.mode == 'profile':
            profile = ZapUser.objects.get(id=data[0].id)
            extra = {
                'action': 'profile',
                'profile_id': profile.id,
                'profile_name': profile.zap_username,
                'profile_type': profile.user_type.name,
                'profile_pic': profile.profile.profile_pic
            }
        elif self.drip_base.drip_model.action.mode == 'filtered':
            extra = {
                'action': 'filtered',
                'product_ids': data.values_list('id', flat=True)
                # 'args': notif.action.get_args_string()
            }
            print(data)
        elif self.drip_base.drip_model.action.mode == 'newsfeed':
            extra = {
                'action': 'newsfeed'
            }
            print(data)
        elif self.drip_base.drip_model.action.mode == 'upload':
            extra = {
                'action': 'upload'
            }
        extra['marketing'] = True
        if self.drip_base.drip_model.push_notif.image:
            extra['image'] = self.drip_base.drip_model.push_notif.image
        # extra['notif_id'] = str(notif.id)
        extra['sent_time'] = str(sent_time)
        extra = {k: str(v) for k, v in extra.items()}
        return extra
    def send(self, **kwargs):
        pushnots = PushNotification()

        if self.bulk:
            content = self.drip_base.drip_model.push_notif.content
            # pushnots.send_notification(
            #     self.user, content, extra=self.drip_base.drip_model.push_notif.extra)
        else:

            t = Template(self.drip_base.drip_model.push_notif.content)
            try:
                context_dict = self.drip_base.get_content_groups_data(context=kwargs['context'])
                context_dict.update({'target_user':ContentUserSerializer(self.target_user[0]).data})
            except:
                context_dict = self.drip_base.get_content_groups_data()
                context_dict.update({'target_user':self.target_user})
            content = t.render(
                    Context(context_dict))
            # pdb.set_trace()
            if self.drip_base.drip_model.action.mode == 'own_profile':

                for user in self.target_user:
                    extra = {
                        'action': 'profile',
                        'profile_id': user.id,
                        'profile_name': user.zap_username,
                        'profile_type': user.user_type.name,
                        'profile_pic': user.profile.profile_pic,
                        'marketing': True,
                        # 'notif_id': str(notif.id),
                        'sent_time': str(sent_time),
                        'image': self.drip_base.drip_model.push_notif.image
                    }
                    extra = {k: str(v) for k, v in data.items()}
                    # print extra
                    # own_profile_list.append({'zap_username': user.zap_username, 'text': notif.text, 'data': data})
                    pushnots.send_notification(user, content, extra=extra)

            else:
                # print self.drip_base.get_content_groups_data(context=kwargs['context'])
                # print self.target_user
                # print content

                # print self.get_extra_data(context=kwargs['context'])
                # pdb.set_trace()
                pushnots.send_notification(
                    self.target_user, content, extra=self.get_extra_data(context=kwargs['context']))
        return None

# class DripOverlay(object):
#     pass


def evaluated_template_data(input_dict, context):
    template_data = {}
    # pdb.set_trace()
    for k, v in input_dict.iteritems():
        if isinstance(v, list):
            cur_quryset = context[k+'_list']
            # cur_list = [{n:eval(v[0][n]) for n in v[0]} for i in cur_quryset]

            cur_list = []
            for i in cur_quryset:
                ab = {}
                for nk, nv in v[0].iteritems():
                    ab.update({nk: eval(nv)})
                cur_list.append(ab)
            template_data.update({k: cur_list})
        elif isinstance(v, str):
            template_data.update({k: eval(v)})

    return template_data


class DripEmail(object):

    def __init__(self, drip_base, user=None, bulk=False):
        self.drip_base = drip_base
        self.user = user
        # self.context = {'user': self.user}
        self.attachment = self.drip_base.attachment
        self.attachment_name = self.drip_base.attachment_name

    @property
    def from_email(self):
        return self.drip_base.drip_model.from_email

    # @property
    # def from_email_name(self):
    #     return self.drip_base.from_email_name

    # @property
    def subject(self, **kwargs):
        try:
            self.subject = Template(self.drip_base.drip_model.email.subject_template).render(
                Context(self.drip_base.get_content_groups_data(context=kwargs['context'])))
        except:
            self.subject = Template(self.drip_base.drip_model.email.subject_template).render(
                Context(self.drip_base.get_content_groups_data()))
        return self.subject

    # @property
    def body(self, **kwargs):
        try:
            self.body = Template(self.drip_base.drip_model.email.body_html_template).render(
                Context(self.drip_base.get_content_groups_data(context=kwargs['context'])))
        except:
            self.body = Template(self.drip_base.drip_model.email.body_html_template).render(
                Context(self.drip_base.get_content_groups_data()))
        return self.body

    @property
    def plain(self):
        if not self._plain:
            self._plain = strip_tags(self.body)
        return self._plain

    # @property
    # def message(self):
    #     if not self._message:
    #         if self.email.from_email_name:
    #             from_ = "%s <%s>" % (self.email.from_email_name, self.email.from_email)
    #         else:
    #             from_ = self.email.from_email

    #         self._message = EmailMultiAlternatives(
    #             self.subject, self.plain, from_, [self.user.email])

    #         # check if there are html tags in the rendered template
    #         if len(self.plain) != len(self.body):
    #             self._message.attach_alternative(self.body, 'text/html')
    #     return self._message

    def send(self, **kwargs):
        # pdb.set_trace()
        if not (isinstance(self.user, list) or isinstance(self.user,QuerySet)):
            email_list = [self.user.email]
        else:
            email_list = self.user.values_list('email', flat=True)
        zapemail = ZapEmail()
        # print self.subject(context=kwargs['context'])
        # print self.body(context=kwargs['context'])
        zapemail.send_email_alternative(self.subject(context=kwargs['context']), settings.FROM_EMAIL, email_list, self.body(
            context=kwargs['context']), self.attachment, self.attachment_name)
    

class DripBase(object):

    """
    A base object for defining a Drip.

    You can extend this manually, or you can create full querysets
    and templates from the admin.
    """
    #: needs a unique name
    name = None

    def __init__(self, drip_model, *args, **kwargs):
        # pdb.set_trace()
        self.drip_model = drip_model
        self.target_group = drip_model.target_group
        self.name = drip_model.name
        # self.subject_context = drip_model.email.subject_context
        # self.email_context = drip_model.email.email_context
        self.context = kwargs['context'] if kwargs else {}
        self.attachment = kwargs['context']['attach'][
            'attachment'] if kwargs and 'attach' in kwargs["context"] else None
        self.attachment_name = kwargs['context']['attach'][
            'attachment_name'] if kwargs and 'attach' in kwargs["context"] else None

        if not self.name:
            raise AttributeError('You must define a name.')

    #########################
    ### DATE MANIPULATION ###
    #########################

    def now(self):
        """
        This allows us to override what we consider "now", making it easy
        to build timelines of who gets what when.
        """
        return conditional_now() + self.timedelta(**{})

    def timedelta(self, *a, **kw):
        """
        If needed, this allows us the ability to manipuate the slicing of time.
        """
        from datetime import timedelta
        return timedelta(*a, **kw)

    def walk(self, into_past=0, into_future=0):
        """
        Walk over a date range and create new instances of self with new ranges.
        """
        walked_range = []
        for shift in range(-into_past, into_future):
            kwargs = dict(drip_model=self.drip_model,
                          name=self.name,
                          now_shift_kwargs={'days': shift})
            walked_range.append(self.__class__(**kwargs))
        return walked_range

    def apply_queryset_rules(self, qs, group, context=None):
        """
        First collect all filter/exclude kwargs and apply any annotations.
        Then apply all filters at once, and all excludes at once.
        """
        clauses = {
            'filter': [],
            'exclude': []}
        # pdb.set_trace()
        for rule in group:
            
            print clauses, rule.method_type
            clause = clauses.get(rule.method_type, clauses['filter'])
            kwargs = rule.filter_kwargs(qs, now=self.now, context=context)
            clause.append(Q(**kwargs))

            qs = rule.apply_any_annotation(qs)

        if clauses['exclude']:
            qs = qs.exclude(functools.reduce(operator.or_, clauses['exclude']))
        qs = qs.filter(*clauses['filter'])
        return qs

    ##################
    ### MANAGEMENT ###
    ##################

    def get_queryset(self, selected_model=None, context=None, action=False, content_group=None):
        # 
        
        if action:
            self._queryset = self.apply_queryset_rules(self.queryset(selected_model),
                                                       self.drip_model.action.content_queryset_rules.all(), context).distinct()

        elif selected_model:
            self._queryset = self.apply_queryset_rules(self.queryset(selected_model), 
                                                       content_group.content_queryset_rules.all(), context).distinct()
        else:
            self._queryset = self.apply_queryset_rules(self.queryset(selected_model),
                                                       self.target_group.queryset_rules.all(), context).distinct()
        # self._queryset = self.apply_queryset_rules(self.queryset(selected_model))\
        #                      .distinct()
        return self._queryset

    def run(self):
        """
        Get the queryset, prune sent people, and send it.
        """
        if not self.drip_model.enabled:
            return None

        self.prune()
        count = self.send()

        return count

    def prune(self):
        pass

        """
        Do an exclude for all Users who have a SentDrip already.
        """
        # target_user_ids = self.get_queryset().values_list('id', flat=True)
        # exclude_user_ids = SentDrip.objects.filter(date__lt=conditional_now(),
        #                                            drip=self.drip_model,
        #                                            user__id__in=target_user_ids)\
        #                                    .values_list('user_id', flat=True)
        # self._queryset = self.get_queryset().exclude(id__in=exclude_user_ids)

        # subcategory._meta.get_field('category').rel.to

    # def get_trigger_contents(content_rule):
    #     for content in content_rule:
    def get_action_data(self, **kwargs):
        action = self.drip_model.action 
        selected_model = action.model_choice
        context = self.context 
        return self.get_queryset(selected_model, context, action=True)
        # if selected_model == 'ApprovedProduct':
        #     return 
        #     return {content_group.key_name: ContentProductSerializer(all_queryset, many=True).data}
        # elif selected_model == 'ZapUser':
        #     return {content_group.key_name:ContentUserSerializer(all_queryset, many=True).data}

    def get_content_groups_data(self, **kwargs):
        # if self.drip_model.triggered_group.all():
        
        if self.drip_model.static_content_group:
            return {'users': ContentUserSerializer(self.drip_model.static_content_group.users.all(), many=True).data,
                    'products': ContentProductSerializer(self.drip_model.static_content_group.produtcs.all(), many=True).data}
        if self.drip_model.content_group.all():
            data = {}
            for content_group in self.drip_model.content_group.all():
                selected_model = content_group.model_choice
                context = self.context
                all_queryset = self.get_queryset(selected_model, context, content_group=content_group)
                if selected_model == 'ApprovedProduct':
                    srlzr_data = ContentProductSerializer(all_queryset, many=True).data
                    if len(srlzr_data) == 1:
                        srlzr_data = srlzr_data[0]
                    data.update({content_group.key_name: srlzr_data})
                elif selected_model == 'ZapUser':
                    srlzr_data = ContentUserSerializer(all_queryset, many=True).data
                    if len(srlzr_data) == 1:
                        srlzr_data = srlzr_data[0]
                    data.update({content_group.key_name:srlzr_data})
            return data

    def send(self):
        """
        Send the message to each user on the queryset.

        Create SentDrip for each user that gets a message.

        Returns count of created SentDrips.
        """

        # if not self.from_email:
        #     self.from_email = getattr(settings, 'DRIP_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)
        
        msg_mode = []
        if self.drip_model.email:
            msg_mode.append('email')
        if self.drip_model.sms:
            msg_mode.append('sms')
        if self.drip_model.push_notif:
            msg_mode.append('push_notification')
        for mode in msg_mode:
            MessageClass = message_class_for(mode)
            if self.drip_model.bulk:
                users = self.get_queryset(context=self.context)
                message_instance = MessageClass(
                    self, users, bulk=True)
                message_instance.send(context=self.context)
            else:
                for user in self.get_queryset(context=self.context):
                    message_instance = MessageClass(self, user)
                    message_instance.send(context=self.context)
        # count = 0
        # for user in self.get_queryset():
        #     message_instance = MessageClass(self, user)
        #     try:
        #         result = message_instance.message.send()
        #         if result:
        #             SentDrip.objects.create(
        #                 drip=self.drip_model,
        #                 user=user,
        #                 from_email=self.from_email,
        #                 from_email_name=self.from_email_name,
        #                 subject=message_instance.subject,
        #                 body=message_instance.body
        #             )
        #             count += 1
        #     except Exception as e:
        #         logging.error("Failed to send drip %s to user %s: %s" % (self.drip_model.id, user, e))
        return True

    ####################
    ### USER DEFINED ###
    ####################

    def queryset(self, selected_model=None):
        """
        Returns a queryset of auth.User who meet the
        criteria of the drip.

        Alternatively, you could create Drips on the fly
        using a queryset builder from the admin interface...
        """
        selected_model = get_user_model(selected_model)
        return selected_model.objects
