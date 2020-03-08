from dateutil import parser
from django.conf import settings
from zap_apps.account.zapauth import ZapView, ZapAuthView
from zap_apps.marketing.models import Overlay, UserMarketing, NotificationTracker, Notifs, OverlaySeen, Campaign, Lead
from zap_apps.zapuser.models import ZapUser
from zap_apps.marketing.tasks import track_notifications
from zap_apps.marketing.marketing_data_serializer import OverlaySerializer
import pdb
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse
from zap_apps.zap_notification.views import ZapEmail
from django.template.loader import render_to_string
from rest_framework.decorators import api_view


class SaveNotifTrack(ZapView):
    def post(self, request, format=None):
        platform = request.PLATFORM
        if not platform or request.user.is_anonymous():
            print('Cannot track notifications! Platform not defined!')
            return self.send_response(0, 'Failed')
        data = request.data.copy()
        notif = Notifs.objects.get(id=int(data['notif_id']))
        notification_tracker = NotificationTracker.objects.get(notif=notif, user=request.user,
                                                               sent_time=parser.parse(data['sent_time']).replace(
                                                                   tzinfo=None))
        notification_tracker.opened_time = parser.parse(data['opened_time'])
        notification_tracker.save()
        return self.send_response(1, 'Saved')


# class OverlayView(ZapAuthView):
#     def get_model_fields(self, model):
#         return model._meta.fields
#     def get(self, request, page, format=None):
#         # pdb.set_trace()
#         print page
#         for i in Overlay.objects.filter(page=page, active=True):
#             if i.in_time():
#                 try:
#                     user_marketing = UserMarketing.objects.get(user=request.user)
#                 except UserMarketing.DoesNotExist:
#                     return self.send_response(0, "No Overlays now.")
#                 try:
#                     if getattr(user_marketing, i.campaign, True) == False:
#                         setattr(user_marketing, i.campaign, True)
#                         srlzr = OverlaySerializer(i)
#                         # print srlzr.data
#                         if not settings.DEBUG:
#                             user_marketing.save()
#                         return self.send_response(1, srlzr.data)
#                     else:
#                         continue
#                 except KeyError:
#                     return self.send_response(0, "No campaigns.")
#         return self.send_response(0, "No Overlays now.")

class OverlayView(ZapAuthView):
    def get_model_fields(self, model):
        return model._meta.fields

    def get(self, request, page, format=None):

        print page, '0000'
        for i in Overlay.objects.filter(page=page, active=True):
            # pdb.set_trace()
            if i.in_time():
                show_overlay = False

                # if the user has checked the overlay atleast once
                try:
                    # New Code for Overlay Seen
                    # pdb.set_trace()
                    overlay_seen_object = OverlaySeen.objects.get(user=request.user, overlay=i)
                    number_of_times_seen = overlay_seen_object.number_of_times_seen
                    print number_of_times_seen

                    if number_of_times_seen < i.show_limit:
                        # Show the overlay
                        # Incrememnt number_of_times_field+1
                        show_overlay = True
                        o_object = OverlaySeen.objects.get(user=request.user, overlay=i.id)
                        o_object.number_of_times_seen += 1
                        o_object.save()
                    else:
                        # No overlays to show
                        show_overlay = False

                # If the user has not seen the overlay ever
                except OverlaySeen.DoesNotExist:
                    # Show the overlay
                    # Add an entry to OverlaySeen Model
                    show_overlay = True
                    seen_object = OverlaySeen(user=request.user, overlay=i, number_of_times_seen=1)
                    seen_object.save()

                if show_overlay:
                    srlzr = OverlaySerializer(i)
                    return self.send_response(1, srlzr.data)
                else:
                    return self.send_response(0, "No Overlays now.")

        return self.send_response(0, "No Overlays now.")


class FollowCampaign(ZapAuthView):
    def get(self, request, campaign_id, format=None):
        try:
            user = ZapUser.objects.get(id=request.user.id)
            if str(campaign_id).isdigit():
                campaign = Campaign.objects.get(id=int(campaign_id))
            else:
                campaign = Campaign.objects.get(slug=str(campaign_id))
            campaign.following_users.add(user)
            return self.send_response(1, {'message': 'Sucessfully set reminder'})
        except Exception as e:
            return self.send_response(0, {'error': "Couldn't retrieve user or campaign"})


class FollowCampaignAllUsers(ZapView):

    def verify_email(self, email, unique_code):
        verification_url = settings.DOMAIN_NAME + '/marketing/verify_lead/?key=' + str(unique_code)
        z = ZapEmail()
        email_body = '<p>Hi Zapyler, <br/><br/>Thank you for signing up!<br/><br/> ' \
                     'Verify your e-email address to be notified: <br/><br/>' \
                     + verification_url + '<br/><br/>Yours Fashionably,<br/>Zapyle</p>'
        z.send_email_alternative('Verify your e-mail address here ', settings.FROM_EMAIL, email, email_body)

    def verify_sms(self, phone_number, unique_code):
        pass

    def send_drip_email(self, referral_lead, campaign_id, referral_url):
        referral_url = settings.DOMAIN_NAME + referral_url
        if str(campaign_id).isdigit():
            campaign = Campaign.objects.get(id=int(campaign_id))
        else:
            campaign = Campaign.objects.get(slug=str(campaign_id))
        if referral_lead:
            users_referred = Lead.objects.filter(Q(referral_lead=referral_lead) & Q(acquired_campaign=campaign)).count()
            referral = Lead.objects.get(pk=referral_lead.id)
        else:
            return

        params = {}

        if users_referred == 5:
            params['subject'] = 'Woohoo! You did it.'
            params['heading'] = '5/5 DONE. CONGRATULATIONS!'
            params['message'] = 'You just earned your Rs. 1000 voucher! \n\r \n\rKeep sharing! More surprises might be ' \
                                'coming your way:\n\r \n\r' + referral_url
            send_mail = True
        elif 0 < users_referred < 5:
            params['subject'] = 'Good News! ' + str(5-users_referred) +' more to go.'
            params['heading'] = 'Good News! ' + str(users_referred) + '/5 done.'
            params['message'] = 'You\'re now only ' + str(5-users_referred) +' friends away from your Rs. 1000 voucher' \
                                                                            ', so get them going! \n\r \n\rShare more, ' \
                                                                            'earn quicker: ' + referral_url
            send_mail = True
        else:
            send_mail = False

        params['url'] = referral_url

        if send_mail:
            # Send email to user with the params
            z = ZapEmail()
            html = settings.LEAD_TEMPLATE
            html_body = render_to_string(html['html'], params)
            z.send_email_alternative(params['subject'], settings.FROM_EMAIL, referral.email, html_body)

    def post(self, request, format=None):
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        name = request.POST.get('name', '')
        campaign_id = request.POST.get('campaign_id', '')
        unique_code = request.POST.get('unique_code', '')

        referral_user = referring_user = referral_email = referral_phone = None
        if str(campaign_id).isdigit():
            campaign = Campaign.objects.get(id=int(campaign_id))
        else:
            campaign = Campaign.objects.get(slug=str(campaign_id))
        try:
            if Lead.objects.filter(Q(email=email) & Q(phone_number=phone) & Q(acquired_campaign=campaign)).count() > 0:
                message = 'User already registered for this campaign '
                return self.send_response(0, {'message': message})
        except Lead.DoesNotExist:
            pass

        if len(unique_code) > 0:
            print unique_code
            try:
                referring_user = Lead.objects.get(unique_code=unique_code)
                referral_email = referring_user.email
                referral_phone = referring_user.phone_number
            except Lead.DoesNotExist:
                referring_user = None
                pass

            try:
                if referral_email:
                    referral_user = ZapUser.objects.get(email=referral_email)
                if referral_phone:
                    referral_user = ZapUser.objects.get(phone_number=referral_phone)
            except ZapUser.DoesNotExist:
                pass

        try:
            import time
            import hashlib
            timestamp = str(int(time.time()))
            referral_code = timestamp + name + email + phone
            m = hashlib.md5()
            m.update(referral_code)
            referral_code = m.hexdigest()

            print str(referring_user) + str(referral_user)
            if str(campaign_id).isdigit():
                campaign = Campaign.objects.get(id=int(campaign_id))
            else:
                campaign = Campaign.objects.get(slug=str(campaign_id))
            lead_generated = Lead(name=name,
                                  email=email,
                                  phone_number=phone,
                                  referral_user=referral_user,
                                  referral_lead=referring_user,
                                  acquired_campaign=campaign,
                                  unique_code=referral_code,
                                  source=unique_code
                                  )
            lead_generated.save()

            # Add user to follow in Campaign
            campaign.following_leads.add(lead_generated)

            # Check if coresponding zap user exists
            try:
                if len(phone) > 0:
                    zapuser = ZapUser.objects.get(phone_number=phone)
                    campaign.following_users.add(zapuser)
                if len(email) > 0:
                    zapuser = ZapUser.objects.get(email=email)
                    campaign.following_users.add(zapuser)
            except ZapUser.DoesNotExist:
                pass

            url = settings.DOMAIN_NAME + '/campaign/' + campaign.slug + '/?ref=' + str(referral_code)
            self.verify_email(email, referral_code)
            url2 = settings.DOMAIN_NAME + '/campaign/' + campaign.slug + '/?ref=' + str(unique_code)
            # self.send_drip_email(referring_user, campaign_id, url2)
            message = 'User now following the campaign'
            return self.send_response(1, {'message': message, 'url': url})
        except Exception as e:
            print str(e)
            message = 'Failed to add user to campaign. Try again. ' + str(e)
            return self.send_response(0, {'message': message})


def verify_lead(request):
    unique_id = request.GET.get('key', '')

    ref_url = ''

    error_message = "Oops! The url doesn't seem to be right! Copy the link in your email and paste in your nrowser and  try again."
    success_message = ''

    if unique_id:
        try:
            lead = Lead.objects.get(unique_code=unique_id)
            if lead:
                success_message = 'You have verified your email.'
                lead.verified = True
                lead.save()

                z = ZapEmail()
                params = {}
                url = settings.DOMAIN_NAME + '/campaign/' + str(lead.acquired_campaign.slug) + '/?ref=' + str(unique_id)
                params['subject'] = 'Success! You\'re on our A-List.'
                params['heading'] = 'You\'re on our A-List'
                params['message'] = 'Now be the first to give your friends the big news! ' \
                                    '\n\r \n\r Get 5 friends to sign up using your unique url and earn a Rs.1000 ' \
                                    'voucher to shop:\n\r\n\r' + url
                html = settings.LEAD_TEMPLATE
                html_body = render_to_string(html['html'], params)
                z.send_email_alternative(params['subject'], settings.FROM_EMAIL, lead.email, html_body)
                ref_url = settings.DOMAIN_NAME + '/campaign/' + str(lead.acquired_campaign.slug) + '/?ref=' + str(unique_id)

                if lead.referral_lead:
                    ref_url2 = '/campaign/' + str(lead.acquired_campaign.slug) + '/?ref=' + \
                               str(lead.referral_lead.unique_code)
                    f = FollowCampaignAllUsers()
                    f.send_drip_email(lead.referral_lead, lead.acquired_campaign.id, ref_url2)

            else:
                message = error_message

        except Lead.DoesNotExist:
            message = error_message
    else:
        message = error_message

    return render(request, 'marketing/thank_you.html', {'msg': success_message, 'ref_url': ref_url})


@api_view(['GET', 'POST'])
def international_treat(request, campaign_id, thanks_page=None):
    user_exists = False
    if str(campaign_id).isdigit():
        campaign = Campaign.objects.get(id=int(campaign_id))
    else:
        campaign = Campaign.objects.get(slug=str(campaign_id))
    if request.method == 'GET':
        if thanks_page:
            msg = "Hey it's you again! We see you've already registered with us. Stay tuned for an update on the launch!"
            email = request.GET.get('email', False)
            if email:
                lead = Lead.objects.get(Q(email=email) & Q(acquired_campaign=campaign))
                ref_url = settings.DOMAIN_NAME + '/campaign/' + campaign.slug + '/?ref=' + str(lead.unique_code)
            else:
                msg = ''
                ref_url = request.GET.get('url','')
            return render(request, 'marketing/thank_you.html', {'ref_url': ref_url, 'msg':msg})    
        return render(request, 'marketing/itreat.html')
