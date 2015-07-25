from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from factories import *
import json
from django.contrib.auth import authenticate

class LogInTest(TestCase):

    def post_request(self, post):
        c = Client()
        return c.post(self.url, content_type = 'application/json', data = json.dumps(post))

    def setUp(self):
        self.url = '/authentication/login'
        self.user_data = create_user_data()
        self.user = create_user(**self.user_data)
        self.token = Token.objects.get(user=self.user)
        self.valid_post = {'username' : self.user_data['username'], 'password' : self.user_data['password']}

    def test_missing_params(self):
        post = {}
        response = self.post_request(post)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_missing_username(self):
        post = {'password' : self.user.password}
        response = self.post_request(post)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_missing_password(self):
        post = {'username' : self.user.username}
        response = self.post_request(post)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_receive_token(self):
        response = self.post_request(self.valid_post)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        content = json.loads(response.content)
        self.assertEqual(content['token'], str(self.token))

class ChangePasswordTest(TestCase):

    def post_without_token(self, post):
        c = Client()
        return c.post(self.url, content_type = 'application/json', data = json.dumps(post))

    def post_with_token(self, post):
        c = Client()
        return c.post(self.url, content_type = 'application/json', data = json.dumps(post), **{'HTTP_AUTHORIZATION' : 'Token %s' % str(self.token)})

    def setUp(self):
        self.url = '/authentication/change_password'
        self.user_data = create_user_data()
        self.user = create_user(**self.user_data)
        self.token = Token.objects.get(user=self.user)
        self.valid_post = {'username' : self.user_data['username'], 'password' : self.user_data['password'], 'new_password' : 'new'}

    def test_missing_params(self):
        post = {}
        response = self.post_with_token(post)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_missing_username(self):
        post = {'password' : self.user.password}
        response = self.post_with_token(post)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_missing_password(self):
        post = {'username' : self.user.username}
        response = self.post_with_token(post)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_missing_token(self):
        response = self.post_without_token(self.valid_post)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_invalid_username(self):
        invalid_post = self.valid_post.copy()
        invalid_post['username'] = 'invalid'
        response = self.post_with_token(invalid_post)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_invalid_password(self):
        invalid_post = self.valid_post.copy()
        invalid_post['password'] = 'invalid'
        response = self.post_with_token(invalid_post)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_successful_change(self):
        old_password = self.user.password
        response = self.post_with_token(self.valid_post)
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)
        user = User.objects.get(username=self.user.username)
        new_password = user.password
        self.assertNotEqual(old_password, new_password)
