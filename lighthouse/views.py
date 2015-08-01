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
from serializers import PostLightSerializer
from serializers import PostAlertSerializer
# Models
import models
# Dispatch
from dispatch import *
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

def update_light_store(resource):
    """
    Updates our backing store with the light information from
    the bridge, so that the admin can go ahead and set permissions
    on lights.
    """
    which = int(resource['id'])
    
    try:
        light = models.Light.objects.get(which=which)
    except:
        light = models.Light(which=which, zone=models.default_zone())

    name = resource['name']
    if light.name != name:
        light.name = name

    light.save()

class Lights(APIView):
    """
    All things light.
    """
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

        light_state = Dispatch().get({'which' : 'all'})
        resources = light_state['resource']
        for resource in resources:
            update_light_store(resource)

        # Now we only want to return the lights that this user has permission to see.
        resources_allowed = []
        for resource in resources:
            which = int(resource['id'])
            light = models.Light.objects.get(which=which)
            if light.user_authenticated(user):
                resources_allowed.append(resource)

        return JSONResponse(resources_allowed)


    def post(self, request):
        """
        Sets the light state.

        Requires a valid user auth token to set the state,
        and the user must be allowed to set the state of that light.
        """
        if not request.user or not request.auth:
            raise Http404
        user = request.user

        # Serialize the data
        serializer = PostLightSerializer(data=request.data)
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
            # Dispatch the task
            dispatch_data = dict(serializer.validated_data)
            Dispatch().dispatch_task_light(**dispatch_data)
            return JSONResponse({}, status=status.HTTP_200_OK)
        return JSONResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            # Dispatch the task
            dispatch_data = dict(serializer.validated_data)
            Dispatch().dispatch_task_alert(**dispatch_data)
            return JSONResponse({}, status=status.HTTP_200_OK)
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

        zones = models.Zone.objects.all()
        zone_json = []
        for zone in zones:
            zone_json.append(zone.as_json())
            
        return JSONResponse(zone_json, status=status.HTTP_200_OK)

