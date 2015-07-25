from models import *
from django.contrib.auth.models import User

test_which = 1

def create_light(**kwargs):
    defaults = {'which' : test_which}
    defaults.update(kwargs)
    return Light(**defaults)

def create_user(**kwargs):
    return User()

def create_light_api_post(**kwargs):
    defaults = {
        'which' : test_which,
        'on' : True,
        'hue' : 0,
        'sat' : 255,
        'bri' : 255,
        'transitiontime' : 10
    }
    defaults.update(kwargs)
    return defaults