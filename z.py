from datetime import datetime
import json
import requests

def get_clevertap_events():

    headers = {
        "X-CleverTap-Account-Id": "TEST-566-K95-464Z",
        "X-CleverTap-Passcode": "YMC-RUZ-AEAL",
        "Content-Type": "application/json"
    }

    cursor_url = 'https://api.clevertap.com/1/events.json?batch_size=5000'

    # List of all the events
    events = ['love', 'admire', 'comment_on_product', 'add_to_tote', 'removed_from_tote',
              'upload_product', 'mention', 'edit_profile', 'click', 'page_change', 'zoom_image',
              'pincode_check', 'invite_user', 'transaction', 'checkout_step', 'search', 'filter',
              'notification', 'impression', 'coupon_applied', 'charged', 'write_blog', 'comment_on_blog',
              'campaign_page_visits', 'campaign_cta', 'campaign_social_share_cta', 'Product Viewed']

    for event in events:

        # Get cursor for the events
        this_day = str(datetime.now().year) + str('%02d' % datetime.now().month) + str('%02d' % datetime.now().day)
        payload = '{"event_name": "' + event + '", "from": ' + this_day + ', "to": ' + this_day + '}'

        print payload

        response = requests.post(cursor_url, data=payload, headers=headers)
        data = response.json()
        print data
        if data['status'] == 'success':
            cursor = data['cursor']
            next_cursor_data(cursor)
        else:
            pass


def next_cursor_data(cursor):
    headers = {
        "X-CleverTap-Account-Id": "TEST-566-K95-464Z",
        "X-CleverTap-Passcode": "YMC-RUZ-AEAL",
        "Content-Type": "application/json"
    }

    events_url = 'https://api.clevertap.com/1/events.json?cursor=' + cursor
    event_response = requests.get(events_url, headers=headers)
    event_data = event_response.json()
    print event_data
    if event_data['status'] == 'success':
        if 'next_cursor' in event_data:
            next_cursor = event_data['next_cursor']
            if len(event_data['records']) > 0:
                for record in event_data['records']:
                    print record
                next_cursor_data(next_cursor)

get_clevertap_events()