# Django Admin
from django.contrib.admin.views.decorators import staff_member_required
# Django
from django.views.decorators.csrf import csrf_exempt
# Django Rest Framework
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework import status
# Response
from django.http import HttpResponse, Http404
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
# Serializers
from serializers import PostAlertSerializer
from serializers import TaskSerializer
from serializers import BetaPostZoneSerializer
# Models
import models
# Synchronization
from synchronization import *
# Dispatch
from dispatch import *
from dispatch_types import *
# Other
import json

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

class Lights(APIView):
    
    def get(self, request):
        """
        Gets all of the lights and their states.
        Also updates our backing database, which will eventually notify all listeners
        that there has been a change.

        Requires a valid user auth token to get the state of the lights.
        """
        if not request.user or not request.auth:
            raise Http404
        user = request.user

        # Synchronize all hue bulbs in the system
        synchronize_hue()

        # Now return all the light states
        return JSONResponse([light.as_json(user) for light in models.Light.objects.all()])

class Alert(APIView):

    def post(self, request):
        """
        Sets the light to blink once.

        Requires a valid user auth token to set the state,
        and the user must be allowed to set the state of that light.
        """
        if not request.user or not request.auth:
            raise Http404
        user = request.user

        # Serialize the data
        data = json.loads(request.body)
        serializer = PostAlertSerializer(data=data)
        # Check if it is valid
        if serializer.is_valid():
            # Get the light
            which = serializer.data['which']
            try:
                light = models.Light.objects.get(which=which)
            except:
                return JSONResponse({'which' : ['No light for which value %d' % which]}, status=status.HTTP_400_BAD_REQUEST)
            # Check the permissions
            if not light.user_authenticated(user):
                return JSONResponse({'user' : ['User is not authenticated for light %d' % which]}, status=status.HTTP_400_BAD_REQUEST)
            # Alert on the light
            light.alert()
            return JSONResponse({}, status=status.HTTP_200_OK)
        return JSONResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Tasks(APIView):

    def get(self, request):
        """
        Gets all of the tasks that have been executed.

        Requires a valid user auth token to get the tasks.
        """
        if not request.user or not request.auth:
            raise Http404
        user = request.user

        # Now return all the tasks
        return JSONResponse([task.as_json() for task in models.Task.objects.all()])

    def post(self, request):
        """
        Posts a change to a single light.
        """
        if not request.user or not request.auth:
            raise Http404
        user = request.user

        # Serialize the data
        data = json.loads(request.body)
        serializer = TaskSerializer(data=data)
        # Check if it is valid
        if serializer.is_valid():
            # Get the light
            which = serializer.data['which']
            try:
                light = models.Light.objects.get(which=which)
            except:
                return JSONResponse({'which' : ['No light for which value %d' % which]}, status=status.HTTP_400_BAD_REQUEST)
            # Check the permissions
            if not light.user_authenticated(user):
                return JSONResponse({'user' : ['User is not authenticated for light %d' % which]}, status=status.HTTP_400_BAD_REQUEST)
            # Copy over the single task data
            copied_data = copy_single_task_data(data)
            # Now make the task and execute it
            task = models.Task(user=user, instructions=json.dumps(copied_data), light=light)
            task.save()
            task.execute()
            return JSONResponse(task.as_json())
        return JSONResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Zones(APIView):
    """
    Permission-authenticated zones or groups of lights.
    """
    def get(self, request):
        """
        Returns zones and the lights that correspond to them.
        """
        if not request.user or not request.auth:
            raise Http404
        user = request.user

        # Synchronize all hue bulbs in the system
        synchronize_hue()

        zones = models.Zone.objects.all()
        zone_json = []
        for zone in zones:
            zone_json.append(zone.as_json(user))
            
        return JSONResponse(zone_json, status=status.HTTP_200_OK)
