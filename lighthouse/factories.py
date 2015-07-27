from models import *
from django.contrib.auth.models import User

test_which = 1

def create_zone(**kwargs):
    defaults = {'which' : test_which, 'name' : 'zone'}
    defaults.update(kwargs)
    return Zone(**defaults)

def create_light(**kwargs):
    zone = create_zone()
    zone.save()
    defaults = {'which' : test_which, 'zone' : zone}
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