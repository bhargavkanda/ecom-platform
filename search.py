import requests
import json
import sys,os
import django
from django.db.models import F
os.environ["DJANGO_SETTINGS_MODULE"] = "zapyle_new.settings.local"
django.setup()
from zap_apps.zap_catalogue.models import Comments,ApprovedProduct
from zap_apps.zapuser.models import ZapUser


ELASTICSEARCH_DOMAIN_URL = 'http://localhost:9200/'

class Search:
    def __init__(self, type=None):
        self.ranges = [{"from": i, "to": i+500-1} for i in xrange(0, 200000, 500)]
        self.type = type
        if self.type:
            self.url = 'http://localhost:9200/zap/'+ self.type + '/'
        else:
            self.url = 'http://localhost:9200/zap/'

    def insert(self, data, id):
        put_url = self.url + id
        return requests.put(put_url, json.dumps(data))

    def bulk_insert(self, data):
        # with open('{}.json'.format(self.type), 'w') as f:
        #     f.write(data)
        put_url = self.url + '_bulk'
        r = requests.post(put_url, data)

    def delete(self, id):
        requests.delete(self.url + id)

    def search(self, q):
        q = "*" + q + "*"
        s = {
                "size": "5",
                "from": "0",
                "query": {
                            "query_string": {
                                    "query": q
                            }
                },
                "_source": {
                    "exclude": ["phone_number"]
                },
                # "aggs": {
                #     "brand_names": {
                #         "terms": {
                #             "field": "brand_name",
                #         }
                #     }
                # },
        }
        r = requests.post(self.url + '_search', json.dumps(s))
        try:
            return r.json()
        except KeyError:
            print r.text
            return []

    def filter(self, q=None):
        q = {"match": {i:j} for i,j in q.items()} if q else {"match_all": {}}
        s = {
            # "query": {
            #     "constant_score": {
            #         "filter": {
            #             "bool": {
            #                 "must": [
            #                     {"term": {"brand_name": q}},
            #                     {"term": {"id": "1541"}}
            #                 ],
            #             }
            #         }
            #     }
            # }
            "query": {
                "filtered": {
                  "query": q,
                }
              },
            "size": 5,
            "from": 0,
            "aggs": {
                "brands": {
                    "terms": {
                        "field": "b",
                    }
                },
                "conditions": {
                    "terms": {
                        "field": "c",
                    }
                },
                "ages": {
                    "terms": {
                        "field": "a",
                    }
                },
                "colors": {
                    "terms": {
                        "field": "id",
                    }
                },
                "sizes": {
                    "terms": {
                        "field": "s",
                    }
                },
                # "price_ranges" : {
                #     "range" : {
                #         "field" : "listing_price",
                #         "ranges" : self.ranges,
                #         "keyed": True,
                #     }
                # },
                "price_ranges" : {
                    "histogram" : {
                        "field" : "lp",
                        "interval" : 500,
                        "min_doc_count" : 1,
                        # "extended_bounds" : {
                        #     "min" : 0,
                        #     "max" : 500
                        # }
                    }
                }
            },
        }
        r = requests.post(self.url + '_search', json.dumps(s))
        try:
            return r.json()
        except KeyError:
            print r.text
            return []

# ZapUser.objects.annotate(pro_pic1=F('profile__pro_pic'), pro_pic2=F('profile___profile_pic')).values('zap_username', 'first_name', 'email', 'phone_number', 'last_name', 'pro_pic1', 'pro_pic2')
# s = Search('product')
# print s.filter({})
# for i in ApprovedProduct.objects.annotate(image=F('images__image'), brand_name=F('brand__brand')).values('id', 'image', 'title',
#                                                                                                 'brand_name',
#                                                                                                 'description', 'listing_price'):
#     s.insert(i, str(i['id']))

def size_type(foo):
    return ("size" if foo.product_category.parent.category_type == 'C' else
            "US" if foo.product_category.parent.category_type == 'FW' else "FREESIZE")


def get_size(p):
    t = size_type(p)
    if t == 'FREESIZE':
        return "FREESIZE"
    if t == 'US':
        return " ".join(["US"+i.us_size for i in p.size.all()])
    if t == 'size':
        return " ".join([i.size for i in p.size.all()])


def data_to_elastic(type):
    string = ""
    if type == 'user':
        for i in ZapUser.objects.annotate(
            pro_pic1=F('profile__pro_pic'),
            pro_pic2=F('profile___profile_pic')
        ).values(
            'zap_username', 'first_name', 'id',
            'email', 'phone_number', 'last_name',
            'pro_pic1', 'pro_pic2'
        ):
            string += json.dumps({"index": {"_id": i['id']}}) + "\n"
            string += json.dumps(i) + "\n"
        s = Search('user')
        s.bulk_insert(string)
    string = ""
    if type == 'product':
        rel = ['brand', 'style', 'color', 'occasion', 'product_category', 'product_category__parent']
        for i in ApprovedProduct.ap_objects.select_related(*rel).filter(sale='2').all():
            print i
            data = {
                'id': i.id,
                'lp': i.listing_price,
                't': i.title,
                'de': i.description,
                'di': i.discount * 100,
                'b': i.brand.brand,
                'st': i.style.style_type if i.style else "not defined",
                'co': i.color.name if i.color else "not defined",
                'o': i.occasion.name if i.occasion else "not defined",
                'c': i.get_condition_display(),
                'a': i.get_age_display(),
                's': get_size(i),
                'ca': i.product_category.parent.name + "--" + i.product_category.name

            }
            print get_size(i)
            string += json.dumps({"index": {"_id": i.id}}) + "\n"
            string += json.dumps(data) + "\n"
        s = Search('product')
        s.bulk_insert(string)




def put_mapping():
    data = {
      "analysis": {
        "analyzer": {
          "final": {
            "type": "custom",
            "tokenizer": "keyword",
            "filter": "lowercase"
          }
        }
      }
    }
    r = requests.put('http://localhost:9200/zap', json.dumps(data))
    print r.text
    data = {
        "product": {
            "properties": {
                "c": {
                    "type": "string",
                    "analyzer": "final"
                },
                "a": {
                    "type": "string",
                    "analyzer": "final"
                },
                "o": {
                    "type": "string",
                    "analyzer": "final"
                },
                "b": {
                    "type": "string",
                    "analyzer": "final"
                }
            }
        }
    }
    r = requests.put('http://localhost:9200/zap/product/_mapping', json.dumps(data))
    print r.text
# put_mapping()
# data_to_elastic('user')
# data_to_elastic('product')
s = Search('product')
print json.dumps(s.filter())