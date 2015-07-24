from models import *
from django.contrib.auth.models import User

def create_light(**kwargs):
    defaults = {'which' : 0}
    defaults.update(kwargs)
    return Light(**defaults)

def create_user(**kwargs):
    return User()

def create_light_api_post(**kwargs):
    defaults = {
        'which' : 0,
        'on' : True,
        'hue' : 255,
        'sat' : 255,
        'bri' : 255,
        'transitiontime' : 10
    }
    defaults.update(kwargs)
    return defaults