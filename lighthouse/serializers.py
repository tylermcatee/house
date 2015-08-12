from rest_framework import serializers

class PostAlertSerializer(serializers.Serializer):
    which = serializers.IntegerField()