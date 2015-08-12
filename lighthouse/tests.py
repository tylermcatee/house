from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from factories import *
from models import *
import json, mock
from dispatch import Dispatch
from dispatch_types import *

class LightModelTest(TestCase):

    def test_create_light(self):
        light = create_light()

    def test_add_user(self):
        user = create_user()
        user.save()
        light = create_light()      
        light.save()
        light.zone.users.add(user)
        self.assertItemsEqual([user], light.zone.users.all())

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
        light.zone.private = True
        self.assertFalse(light.user_authenticated(user))

    def test_user_authenticated_private(self):
        user = create_user()
        light = create_light()
        # Need to save these before engaging manytomany field
        user.save()        
        light.save()
        light.zone.users.add(user)
        light.private = True
        self.assertTrue(light.user_authenticated(user))

    def test_as_json(self):
        zone = create_zone(name='test2')
        zone.save()
        light_json = {
            'which' : 0,
            'name' : 'test',
            'zone' : zone,
            'dispatch_type' : dispatch_type_hue,
            'on' : True,
            'bri' : 0,
            'hue' : 0,
            'sat' : 0,
            'colorloop' : 0,
            'reachable' : 0
        }
        light = create_light(**light_json)
        light.save()
        light_json['authenticated'] = True
        light_json['zone'] = zone.name
        self.assertEqual(light_json, light.as_json())

# class LightPOSTTest(TestCase):

#     def post_with_token(self, post):
#         c = Client()
#         return c.post(self.url, content_type = 'application/json', data = json.dumps(post), **{'HTTP_AUTHORIZATION' : 'Token %s' % str(self.token)})

#     def setUp(self):
#         self.url = '/lighthouse/lights'
#         self.user = create_user()
#         self.user.save()
#         self.token = Token.objects.get(user=self.user)

#     def set_up_light(self, private=False, users=[]):
#         l = create_light()
#         l.zone.private = private
#         l.zone.save()
#         l.save()
#         for user in users:
#             l.zone.users.add(user)
#         l.save()

#     def test_no_user_raises_404(self):
#         c = Client()
#         post = {}
#         response = c.post(self.url, content_type = 'application/json', data = json.dumps(post))
#         # Without a proper user token, we should not be able to post
#         self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

#     def test_missing_keys_raises_errors(self):
#         post = create_light_api_post()
#         keys = post.keys()
#         for key in keys:
#             mutable_post = post.copy()
#             mutable_post.pop(key)
#             response = self.post_with_token(mutable_post)
#             # If we missed a key we should be receiving a 400 error
#             self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

#     def test_negative_keys_raises_errors(self):
#         post = create_light_api_post()
#         keys = post.keys()
#         for key in ['hue', 'sat', 'bri', 'transitiontime']:
#             mutable_post = post.copy()
#             mutable_post[key] = -1
#             response = self.post_with_token(mutable_post)
#             # If we pass a negative value for these we should be receiving a 400 error
#             self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

#     def test_hue_range_error(self):
#         post = create_light_api_post()
#         post['hue'] = 65281
#         response = self.post_with_token(post)
#         # If we pass an out of range value for these we should be receiving a 400 error
#         self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

#     def test_no_light_error(self):
#         post = create_light_api_post()
#         response = self.post_with_token(post)
#         # There should be no light
#         self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

#     def test_user_not_allowed_error(self):
#         self.set_up_light(private=True)
#         post = create_light_api_post()
#         response = self.post_with_token(post)
#         # We shouldn't be allowed to see this
#         self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

#     @mock.patch.object(Dispatch, 'dispatch_task_light')
#     def test_user_allowed(self, mock_dispatch):
#         self.set_up_light(private=True, users=[self.user])
#         post = create_light_api_post()
#         response = self.post_with_token(post)
#         # We should now be allowed to see this
#         self.assertEqual(status.HTTP_200_OK, response.status_code)
#         self.assertTrue(mock_dispatch.called)
        

class LightGETTest(TestCase):

    def get_with_token(self):
        c = Client()
        return c.get(self.url, **{'HTTP_AUTHORIZATION' : 'Token %s' % str(self.token)})

    def setUp(self):
        self.url = '/lighthouse/lights'
        self.user = create_user()
        self.user.save()
        self.token = Token.objects.get(user=self.user)

    def test_no_user_raises_404(self):
        c = Client()
        response = c.get(self.url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    @mock.patch.object(Dispatch, 'get')
    def test_light_state_returned(self, mock_get):
        light = create_light()
        light.save()
        response = self.get_with_token()
        self.assertTrue(mock_get.called)
        light_response = json.loads(response.content)[0]
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(light.as_json(), light_response)

    @mock.patch.object(Dispatch, 'update')
    @mock.patch.object(Dispatch, 'get')
    def test_light_object_changed_on_state_read(self, mock_get, mock_update):
        light = create_light()
        light.save()
        mock_response = mock_hue_response_for_light(light)
        new_name = 'newname'
        mock_response['name'] = new_name
        mock_get.return_value = {
            'resource' : [mock_response]
        }
        response = self.get_with_token()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        light = Light.objects.get(which=light.which)
        self.assertEqual(light.name, new_name)

class ZoneModelTest(TestCase):

    def test_create_zone(self):
        self.assertEqual(0, len(Zone.objects.all()))
        zone = create_zone()
        zone.save()
        self.assertEqual(1, len(Zone.objects.all()))
        new_zone = Zone.objects.all()[0]
        self.assertEqual(zone, new_zone)

    def test_default_zone_function(self):
        self.assertEqual(0, len(Zone.objects.all()))
        zone = default_zone()
        self.assertEqual(1, len(Zone.objects.all()))
        new_zone = Zone.objects.all()[0]
        self.assertEqual(zone, new_zone)

    def test_as_json_no_lights(self):
        zone_json = {
            'name' : 'test',
        }
        zone = create_zone(**zone_json)
        zone.save()
        # Make it look like what we're expecting for as_json
        zone_json['lights'] = []
        new_zone_json = zone.as_json()
        self.assertEqual(zone_json, new_zone_json)

    def test_as_json_lights(self):
        zone_json = {
            'name' : 'test',
        }
        zone = create_zone(**zone_json)
        zone.save()
        light_json = {'which' : 0, 'name' : 'test'}
        light = create_light_no_zone(**light_json)
        light.zone = zone
        light.save()
        # Make it look like what we're expecting for as_json
        zone_json['lights'] = [light.as_json()]
        new_zone_json = zone.as_json()
        self.assertEqual(zone_json, new_zone_json)

    def test_add_users(self):
        zone = create_zone()
        zone.save()
        user = create_user()
        user.save()
        zone.users.add(user)
        self.assertItemsEqual(zone.users.all(), [user])

class ZoneGETTest(TestCase):

    def get_with_token(self):
        c = Client()
        return c.get(self.url, **{'HTTP_AUTHORIZATION' : 'Token %s' % str(self.token)})

    def setUp(self):
        self.url = '/lighthouse/zones'
        self.user = create_user()
        self.user.save()
        self.token = Token.objects.get(user=self.user)

    def test_no_user_raises_404(self):
        c = Client()
        response = c.get(self.url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    # def test_zone_info_returned(self):
    #     zone_json = {
    #         'name' : 'test',
    #     }
    #     zone = create_zone(**zone_json)
    #     zone.save()
    #     light_json = {'which' : 0, 'name' : 'test'}
    #     light = create_light_no_zone(**light_json)
    #     light.zone = zone
    #     light.save()
    #     # Make it look like what we're expecting for as_json
    #     zone_json['lights'] = [light_json]
    #     response = self.get_with_token()
    #     response_json = json.loads(response.content)
    #     self.assertEqual(status.HTTP_200_OK, response.status_code)
    #     self.assertItemsEqual([zone_json], response_json)

# class AlertPOSTTest(TestCase):

#     def post_with_token(self, post):
#         c = Client()
#         return c.post(self.url, content_type = 'application/json', data = json.dumps(post), **{'HTTP_AUTHORIZATION' : 'Token %s' % str(self.token)})

#     def setUp(self):
#         self.url = '/lighthouse/alert'
#         self.user = create_user()
#         self.user.save()
#         self.token = Token.objects.get(user=self.user)

#     def set_up_light(self, private=False, users=[]):
#         l = create_light()
#         l.zone.private = private
#         l.zone.save()
#         l.save()
#         for user in users:
#             l.zone.users.add(user)
#         l.save()

#     def test_no_user_raises_404(self):
#         c = Client()
#         post = {}
#         response = c.post(self.url, content_type = 'application/json', data = json.dumps(post))
#         # Without a proper user token, we should not be able to post
#         self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

#     def test_missing_keys_raises_errors(self):
#         response = self.post_with_token({})
#         # If we missed a key we should be receiving a 400 error
#         self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

#     def test_user_not_allowed_error(self):
#         self.set_up_light(private=True)
#         post = create_alert_api_post()
#         response = self.post_with_token(post)
#         # We shouldn't be allowed to see this
#         self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

#     @mock.patch.object(Dispatch, 'dispatch_task_alert')
#     def test_user_allowed(self, mock_dispatch):
#         self.set_up_light(private=True, users=[self.user])
#         post = create_alert_api_post()
#         response = self.post_with_token(post)
#         # We should now be allowed to see this
#         self.assertEqual(status.HTTP_200_OK, response.status_code)
#         self.assertTrue(mock_dispatch.called)

    