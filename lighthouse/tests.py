from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from factories import *
from models import *
import json, mock
from dispatch import Dispatch
from dispatch_types import *
import time

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

class TaskInstructionsSingleModelTest(TestCase):

    def test_create_task_instructions(self):
        self.assertEqual(0, len(TaskInstructionsSingle.objects.all()))
        task_instructions_single = create_task_instructions_single()
        task_instructions_single.save()
        self.assertEqual(1, len(TaskInstructionsSingle.objects.all()))
        new_instructions = TaskInstructionsSingle.objects.all()[0]
        self.assertEqual(task_instructions_single, new_instructions)

    def test_task_instructions_json(self):
        task_instructions_single = create_task_instructions_single()
        task_instructions_single.save()
        # Now create what we expect the json to look like
        expected_json = {
            'light' : task_instructions_single.light.as_json(),
            'instructions' : json.loads(task_instructions_single.instructions)
        }
        self.assertEqual(task_instructions_single.as_json(), expected_json)

class TaskModelTest(TestCase):

    def test_create_task(self):
        self.assertEqual(0, len(Task.objects.all()))
        task = create_task()
        task.save()
        self.assertEqual(1, len(Task.objects.all()))
        new_task = Task.objects.all()[0]
        self.assertEqual(task, new_task)

    def test_nonexecuted_task(self):
        task = create_task()
        task.save()
        self.assertEqual(None, task.executed)

    @mock.patch.object(Light, 'execute_instructions_single')
    def test_execute_task(self, mock_execute):
        task = create_task()
        task.save()
        self.assertEqual(None, task.executed)
        task.execute()
        self.assertNotEqual(None, task.executed)

    @mock.patch.object(Light, 'execute_instructions_single')
    def test_execute_twice_raises(self, mock_execute):
        task = create_task()
        task.save()
        self.assertEqual(None, task.executed)
        task.execute()
        self.assertNotEqual(None, task.executed)
        self.assertRaises(task.execute)

    def test_task_json_not_executed(self):
        task = create_task()
        task.save()
        task_instructions_single = task.single_instructions
        # Now create what we expect the json to look like
        single_expected_json = {
            'light' : task_instructions_single.light.as_json(),
            'instructions' : json.loads(task_instructions_single.instructions)
        }
        expected_json = {
            'task_type' : task.task_type,
            'user' : task.user.username,
            'instructions' : single_expected_json,
            'created' : int(time.mktime(task.created.timetuple())*1000)
        }
        self.assertEqual(task.as_json(), expected_json)

    @mock.patch.object(Light, 'execute_instructions_single')
    def test_task_json_executed(self, mock_execute):
        task = create_task()
        task.save()
        task_instructions_single = task.single_instructions
        task.execute()
        # Now create what we expect the json to look like
        single_expected_json = {
            'light' : task_instructions_single.light.as_json(),
            'instructions' : json.loads(task_instructions_single.instructions)
        }
        expected_json = {
            'task_type' : task.task_type,
            'user' : task.user.username,
            'instructions' : single_expected_json,
            'created' : int(time.mktime(task.created.timetuple())*1000),
            'executed' : int(time.mktime(task.executed.timetuple())*1000)
        }
        self.assertEqual(task.as_json(), expected_json)

class TaskGETTest(TestCase):

    def get_with_token(self):
        c = Client()
        return c.get(self.url, **{'HTTP_AUTHORIZATION' : 'Token %s' % str(self.token)})

    def setUp(self):
        self.url = '/lighthouse/tasks'
        self.user = create_user()
        self.user.save()
        self.token = Token.objects.get(user=self.user)

    def test_no_user_raises_404(self):
        c = Client()
        response = c.get(self.url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_task_info_returned(self):
        task = create_task(user = self.user)
        task.save()
        task_json = task.as_json()
        response = self.get_with_token()
        response_json = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertItemsEqual([task_json], response_json)

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

    def test_zone_info_returned(self):
        zone = create_zone()
        zone.save()
        light = create_light_no_zone()
        light.zone = zone
        light.save()
        # Make it look like what we're expecting for as_json
        zone_json = {'name' : zone.name, 'lights' : [light.as_json()]}
        response = self.get_with_token()
        response_json = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertItemsEqual([zone_json], response_json)

class AlertPOSTTest(TestCase):

    def post_with_token(self, post):
        c = Client()
        return c.post(self.url, content_type = 'application/json', data = json.dumps(post), **{'HTTP_AUTHORIZATION' : 'Token %s' % str(self.token)})

    def setUp(self):
        self.url = '/lighthouse/alert'
        self.user = create_user()
        self.user.save()
        self.token = Token.objects.get(user=self.user)

    def set_up_light(self, private=False, users=[]):
        l = create_light()
        l.zone.private = private
        l.zone.save()
        l.save()
        for user in users:
            l.zone.users.add(user)
        l.save()

    def test_no_user_raises_404(self):
        c = Client()
        post = {}
        response = c.post(self.url, content_type = 'application/json', data = json.dumps(post))
        # Without a proper user token, we should not be able to post
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_missing_keys_raises_errors(self):
        response = self.post_with_token({})
        # If we missed a key we should be receiving a 400 error
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_user_not_allowed_error(self):
        self.set_up_light(private=True)
        post = create_alert_api_post()
        response = self.post_with_token(post)
        # We shouldn't be allowed to see this
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @mock.patch.object(Dispatch, 'alert')
    def test_user_allowed(self, mock_dispatch):
        self.set_up_light(private=True, users=[self.user])
        post = create_alert_api_post()
        response = self.post_with_token(post)
        # We should now be allowed to see this
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(mock_dispatch.called)

    