from django.test import TestCase
from django.contrib.auth.models import User
from factories import *

class LightTest(TestCase):

    def test_create_light(self):
        light = create_light()

    def test_add_user(self):
        user = create_user()
        light = create_light()
        # Need to save these before engaging manytomany field
        user.save()        
        light.save()
        light.users.add(user)
        self.assertItemsEqual([user], light.users.all())

    def test_user_authenticated_not_private(self):
        user = create_user()
        light = create_light()
        self.assertTrue(light.user_authenticated(user))

    def test_user_not_authenticated_private(self):
        user = create_user()
        light = create_light()
        # Need to save these before engaging manytomany field
        user.save()        
        light.save()
        light.private = True
        self.assertFalse(light.user_authenticated(user))

    def test_user_authenticated_private(self):
        user = create_user()
        light = create_light()
        # Need to save these before engaging manytomany field
        user.save()        
        light.save()
        light.users.add(user)
        light.private = True
        self.assertTrue(light.user_authenticated(user))

        