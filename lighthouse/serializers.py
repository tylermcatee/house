from rest_framework import serializers

class PostAlertSerializer(serializers.Serializer):
    which = serializers.IntegerField()

class TaskSingleSerializer(serializers.Serializer):
    which = serializers.IntegerField()

class BetaPostZoneSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    action = serializers.CharField(max_length=100)