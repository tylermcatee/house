from models import *
from django.contrib.auth.models import User

def create_light(**kwargs):
    defaults = {'which' : 0}
    defaults.update(kwargs)
    return Light(**defaults)

def create_user(**kwargs):
    return User()
