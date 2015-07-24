# Django Rest Framework
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework import status
# Response
from django.http import HttpResponse, Http404
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
# Serializers
from serializers import LightSerializer
# Models
import models

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

class Light(APIView):
    """
    All things light.
    """
    def post(self, request):
        """
        Sets the light state.
        """
        if not request.user or not request.auth:
            raise Http404
        user = request.user

        # Serialize the data
        serializer = LightSerializer(data=request.data)
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

            return JSONResponse({'which' : which})
        return JSONResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

