from django.db import models
from mongoengine import *

# Create your models here.
# DISCOUNT_RULE = (
# 	(1,[100,80]),
# 	(2,[80,70]),
# 	(3,[70,60]),
# 	(4,[60,50]),
# 	(5,[50,40]),
# 	(6,[40,30]),
# 	(7,[30,20]),
# 	(8,[20,10]),
# 	)

# DISCOUNT_RULE = (
# 	(1,[100,70]),
# 	(2,[70,50]),
# 	(3,[50,30]),
# 	(4,[30,0]),
# 	)
FILTER_PRICE_TOLERANCE = .1

DISCOUNT_RULE = (
    (1,70),
    (2,50),
    (3,30),
    (4,10),
    )


SORT_RULE = (
	(1,'-listing_price'),
	(2,'listing_price'),
	(3,'loves'),
	(4,'-discount')
)

class RangeDict():
    def __init__(self):
        self._dict = {}

    def __getitem__(self, key):
        for k, v in self._dict.items():
            if k[0] <= key < k[1]:
                return v

        

    def __setitem__(self, key, value):
        if len(key) == 2:
            if key[0] < key[1]:
                self._dict.__setitem__((key[0], key[1]), value)


disc_range = RangeDict()

# disc_range[[.8,1]] = 1
# disc_range[[.7,.8]] = 2
# disc_range[[.6,.7]] = 3
# disc_range[[.5,.6]] = 4
# disc_range[[.4,.5]] = 5
# disc_range[[.3,.4]] = 6
# disc_range[[.2,.3]] = 7
# disc_range[[.1,.2]] = 8

disc_range[[0.7,0.1]] = 1
disc_range[[0.5,0.7]] = 2
disc_range[[0.3,0.5]] = 3
disc_range[[0.1,0.3]] = 4



class FilterTracker(DynamicDocument):
    user = StringField(max_length=30)
    filters = ListField(DictField())
