from django.db import models
from django.conf import settings

# Create your models here.
class Light(models.Model):
    """
    An integer corresponding to the integer associated
    with the light on the local bridge.
    """
    which = models.IntegerField()

    """
    Private declares that this light can only be controlled
    by a certain subset of users, given by users. If this is false
    we wont check for this.
    """
    private = models.BooleanField(default=False)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def user_authenticated(self, user):
        if self.private:
            return user in self.users.all()
        # If private is false, everyone has access
        return True

    """
    State of the lights.
    """
    on = models.BooleanField()
    bri = models.IntegerField()
    hue = models.IntegerField()
    sat = models.IntegerField()
    effect = models.CharField(max_length = 40)
    name = models.CharField(max_length = 100)
    

class Zone(models.Model):
    name = models.CharField(max_length = 100)
    lights = models.ManyToManyField('Light')