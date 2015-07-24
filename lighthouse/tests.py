from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from factories import *
from models import *
import json

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

class LightAPITest(TestCase):

    def post_with_token(self, post):
        c = Client()
        return c.post(self.url, content_type = 'application/json', data = json.dumps(post), **{'HTTP_AUTHORIZATION' : 'Token %s' % str(self.token)})

    def setUp(self):
        self.url = '/lighthouse/light'
        self.user = create_user()
        self.user.save()
        self.token = Token.objects.get(user=self.user)

    def set_up_light(self, private=False, users=[]):
        l = create_light()
        l.private = private
        l.save()
        for user in users:
            l.users.add(user)
        l.save()

    def test_no_user_raises_404(self):
        c = Client()
        post = {}
        response = c.post(self.url, content_type = 'application/json', data = json.dumps(post))
        # Without a proper user token, we should not be able to post
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_missing_keys_raises_errors(self):
        post = create_light_api_post()
        keys = post.keys()
        for key in keys:
            mutable_post = post.copy()
            mutable_post.pop(key)
            response = self.post_with_token(mutable_post)
            # If we missed a key we should be receiving a 400 error
            self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_negative_keys_raises_errors(self):
        post = create_light_api_post()
        keys = post.keys()
        for key in ['hue', 'sat', 'bri', 'transitiontime']:
            mutable_post = post.copy()
            mutable_post[key] = -1
            response = self.post_with_token(mutable_post)
            # If we pass a negative value for these we should be receiving a 400 error
            self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_hue_range_error(self):
        post = create_light_api_post()
        post['hue'] = 65281
        response = self.post_with_token(post)
        # If we pass an out of range value for these we should be receiving a 400 error
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_no_light_error(self):
        post = create_light_api_post()
        response = self.post_with_token(post)
        # There should be no light
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_user_not_allowed_error(self):
        self.set_up_light(private=True)
        post = create_light_api_post()
        response = self.post_with_token(post)
        # We shouldn't be allowed to see this
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_user_allowed(self):
        self.set_up_light(private=True, users=[self.user])
        post = create_light_api_post()
        response = self.post_with_token(post)
        # We shouldn't be allowed to see this
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        