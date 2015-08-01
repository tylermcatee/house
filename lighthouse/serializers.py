from rest_framework import serializers

class PostLightSerializer(serializers.Serializer):
    which = serializers.IntegerField()
    on = serializers.BooleanField()
    hue = serializers.IntegerField()
    sat = serializers.IntegerField()
    bri = serializers.IntegerField()
    transitiontime = serializers.IntegerField()

    def validate_hue(self, value):
        if value < 0 or value > 65280:
            raise serializers.ValidationError("Hue must be between 0 and 65280")
        return value

    def validate_sat(self, value):
        if value < 0 or value > 255:
            raise serializers.ValidationError("Sat must be between 0 and 255")
        return value

    def validate_bri(self, value):
        if value < 0 or value > 255:
            raise serializers.ValidationError("Bri must be between 0 and 255")
        return value

    def validate_transitiontime(self, value):
        if value < 0:
            raise serializers.ValidationError("Transitiontime must be greater than 0")

class PostAlertSerializer(serializers.Serializer):
    which = serializers.IntegerField()