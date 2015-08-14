from rest_framework import serializers

class PostAlertSerializer(serializers.Serializer):
    which = serializers.IntegerField()

class TaskSerializer(serializers.Serializer):
    which = serializers.IntegerField()

class PostSceneSerializer(serializers.Serializer):
    id = serializers.IntegerField()