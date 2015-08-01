from models import *
from django.contrib.auth.models import User

test_which = 1
test_name = 'test'

def create_zone(**kwargs):
    defaults = {'name' : 'zone'}
    defaults.update(kwargs)
    return Zone(**defaults)

def create_light(**kwargs):
    zone = create_zone()
    zone.save()
    defaults = {'which' : test_which, 'zone' : zone, 'name' : test_name}
    defaults.update(kwargs)
    return Light(**defaults)

def create_light_no_zone(**kwargs):
    defaults = {'which' : test_which, 'name' : test_name}
    defaults.update(kwargs)
    return Light(**defaults)

def create_user(**kwargs):
    return User(username='test', password='test')

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

def create_alert_api_post(**kwargs):
    defaults = {
        'which' : test_which,
    }
    defaults.update(kwargs)
    return defaults

def create_resource(**kwargs):
    resource = {
        'resource' : [
            {
                'id' : test_which,
                'name' : test_name,
            },
        ]
    }
    resource.update(**kwargs)
    return resource