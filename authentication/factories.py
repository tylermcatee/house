from models import *
from django.contrib.auth.models import User

def create_user_data(**kwargs):
    data = {
        'username' : 'test',
        'password' : 'test',
        'email' : 'test@test.com'
    }
    data.update(kwargs)
    return data

def create_user(**kwargs):
    user = User(**kwargs)
    user.set_password(kwargs['password'])
    user.save()
    return user