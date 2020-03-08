import requests,json
from django.conf import settings


class AppViralityApi:
    def __init__(self):
        self.api = settings.API_URL
        self.app_key = settings.APP_KEY
        self.privatekey = settings.PRIVATE_KEY

    #cd6bf2b56f3e4eaab73cad8a72afcdfd
    def conversion(self, u_key, eventName, extrainfo):
        d = {
            "userkey": u_key,
            "apikey": self.app_key,
            "privatekey": self.privatekey,
            "eventName": eventName,
            "extrainfo": extrainfo
        }
        headers={'content-type': 'application/json'}
        r = requests.post(url='{}/v1/registerconversionevent'.format(self.api),
                      data=json.dumps(d),
                      headers=headers)
        print r.text;return (r.text, d)

    def getreferrerrewards(self):
        d = {
            "apikey": self.app_key,
            "privatekey": self.privatekey,
        }

        headers={'content-type': 'application/json'}
        r = requests.post(url='{}/v1/getreferrerrewards'.format(self.api),
                      data=json.dumps(d),
                      headers=headers)
        print r.text;return r.text

    def getfriendrewards(self):
        d = {
            "apikey": self.app_key,
            "privatekey": self.privatekey,
        }

        headers={'content-type': 'application/json'}
        r = requests.post(url='{}/v1/getfriendrewards'.format(self.api),
                      data=json.dumps(d),
                      headers=headers)
        print r.text;return r.text

    def redeemrewards(self, l):
        d = {
            "apikey": self.app_key,
            "privatekey": self.privatekey,
            "rewards": l
        }

        headers={'content-type': 'application/json'}
        r = requests.post(url='{}/v1/redeemrewards'.format(self.api),
                      data=json.dumps(d),
                      headers=headers)
        print r.text;return r.text

    def redeemrewards(self, l):
        d = {
            "apikey": self.app_key,
            "privatekey": self.privatekey,
            "rewards": l
        }

        headers={'content-type': 'application/json'}
        r = requests.post(url='{}/v1/redeemrewards'.format(self.api),
                      data=json.dumps(d),
                      headers=headers)
        print r.text;return r.text
    def changerewardstatus(self, l):
        d = {
            "apikey": self.app_key,
            "privatekey": self.privatekey,
            "rewards": l
        }

        headers={'content-type': 'application/json'}
        r = requests.post(url='{}/v1/changerewardstatus'.format(self.api),
                      data=json.dumps(d),
                      headers=headers)
        print r.text;return r.text
    def getuserdata(self, userkey):
        d = {
            "apikey": self.app_key,
            "privatekey": self.privatekey,
            "userkey": userkey
        }

        headers={'content-type': 'application/json'}
        r = requests.post(url='{}/v1/getuserdata'.format(self.api),
                      data=json.dumps(d),
                      headers=headers)
        print r.text;return r.text

    def updateuserinfo(self, userkey, details):
        d = {
            "apikey": self.app_key,
            "privatekey": self.privatekey,
            "userkey": userkey
        }
        d.update(**details)
        headers={'content-type': 'application/json'}
        r = requests.post(url='{}/v1/updateuserinfo'.format(self.api),
                      data=json.dumps(d),
                      headers=headers)
        print r.text;return r.text
    def checkrewardstatus(self, rewarddtlid):
        d = {
            "apikey": self.app_key,
            "privatekey": self.privatekey,
            "rewarddtlid": rewarddtlid
        }
        headers={'content-type': 'application/json'}
        r = requests.post(url='{}/v1/checkrewardstatus'.format(self.api),
                      data=json.dumps(d),
                      headers=headers)
        print r.text;return r.text

    def getappuserdetails(self, userkey):
        d = {
            "apikey": self.app_key,
            "privatekey": self.privatekey,
            "userkey": userkey
        }
        headers={'content-type': 'application/json'}
        r = requests.post(url='{}/v1/getappuserdetails'.format(self.api),
                      data=json.dumps(d),
                      headers=headers)
        print r.text;return r.text

# app = AppViralityApi()
# app.conversion("44895b0e6e3c4869bb077fb2072ce10f", "Upload")

#conversion("44895b0e6e3c4869bb077fb2072ce10f", "Upload")
#getreferrerrewards()
#getfriendrewards()
# redeemrewards([{
#       "participantid": "23234",
#       "amount": "200"            
#     }])
# redeemrewardconversion([
#       {
#       "participantid":"34216",
#       "rewarddetails":[
#       {"rewarddtlid":"43442"
#       },
#       {
#       "rewarddtlid":"43432"
#       },
#       {
#       "rewarddtlid":"43542"
#       }
#       ]} 
#       ]})

# changerewardstatus([
#   {
#   "rewarddtlid":"797",
#   "reward_status":"Approved"
#   }
#   ])

# getuserdata("44895b0e6e3c4869bb077fb2072ce10f")
# updateuserinfo("44895b0e6e3c4869bb077fb2072ce10f", {
#   "EmailId":"test@test.com",
#   })
# checkrewardstatus("rewarddtlid")
# getappuserdetails("userkey")