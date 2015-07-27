from django.db import models
from django.conf import settings

# Create your models here.
class Light(models.Model):
    """
    An integer corresponding to the integer associated
    with the light on the local bridge.
    """
    which = models.IntegerField()
    # A name just for readability
    name = models.CharField(max_length = 100)
    # The zone declares which part of the house the light is in
    zone = models.ForeignKey('Zone')

    def user_authenticated(self, user):
        if self.zone.private:
            return user in self.zone.users.all()
        # If private is false, everyone has access
        return True

class Zone(models.Model):
    """
    A zone represents a grouping of lights.

    Zones are rooms, and under this control schema rooms are controlled
    individually. Only special cases like group 0 controls the whole house.
    """
    which = models.IntegerField()
    name = models.CharField(max_length = 100)
    """
    Private declares that this zone can only be controlled
    by a certain subset of users.
    """
    private = models.BooleanField(default=False)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
