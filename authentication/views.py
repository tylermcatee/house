# Django auth
from django.contrib.auth.models import *
from django.contrib.auth import authenticate
# Django Rest Framework
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework import status
# Response
from django.http import HttpResponse, Http404
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
# Serializers
from serializers import UserSerializer
from serializers import ChangePasswordSerializer

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

class LogIn(APIView):
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.data['username']
            password = serializer.data['password']
            user = authenticate(username=username, password=password)
            if user:
                token = Token.objects.get(user = user)
                response = {'token' : str(token)}
                return JSONResponse(response, status=status.HTTP_201_CREATED)
            else:
                error = {
                    "username" : "The username or password is invalid",
                    "password" : "The username or password is invalid"
                }
                return JSONResponse(error, status=status.HTTP_400_BAD_REQUEST)
        return JSONResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePassword(APIView):
    def post(self, request, format=None):
        if not request.user or not request.auth:
            raise Http404
        user = request.user

        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.data['username']
            password = serializer.data['password']
            user = authenticate(username=username, password=password)
            if user:
                new_password = serializer.data['new_password']
                user.set_password(new_password)
                user.save()
                return JSONResponse(serializer.data, status=status.HTTP_202_ACCEPTED)
            else:
                error = {
                    "username" : "The username or password is invalid",
                    "password" : "The username or password is invalid"
                }
                return JSONResponse(error, status=status.HTTP_400_BAD_REQUEST)
        return JSONResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


