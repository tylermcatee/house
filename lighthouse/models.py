from django.db import models
from django.conf import settings
from dispatch import *

# Create your models here.
class Light(models.Model):
    """
    An integer corresponding to the integer associated
    with the light on the local bridge.
    """
    which = models.IntegerField()
    # A name just for readability
    name = models.CharField(max_length=100)
    # The zone declares which part of the house the light is in
    zone = models.ForeignKey('Zone')

    # State variables
    on = models.BooleanField(default=False)
    bri = models.IntegerField()
    hue = models.IntegerField()
    sat = models.IntegerField()
    colorloop = models.BooleanField(default=False)
    reachable = models.BooleanField(default=False)

    def user_authenticated(self, user):
        if self.zone.private:
            return user in self.zone.users.all()
        # If private is false, everyone has access
        return True

    def save(self, *args, **kw):
        if self.pk is not None:
            orig = Light.objects.get(pk=self.pk)
            if orig.name != self.name:
                # We have changed the name of the light,
                # we need to update the bridge.
                Dispatch().update({
                        'which' : self.which,
                        'data' : {
                            'attr' : {
                                'name' : self.name
                            }
                        }
                    })
        super(Light, self).save(*args, **kw)

    def as_json(self):
        """
        Returns the light description as json
        """
        return {'which' : self.which, 'name' : self.name}
        

def default_zone():
    """
    Gets a default zone that lights get put into when created.
    """
    default_zone = 'Living Room'
    try:
        zone = Zone.objects.get(name=default_zone)
        return zone
    except:
        zone = Zone(name=default_zone)
        zone.save()
        return zone

class Zone(models.Model):
    class Meta:
        ordering = ['name',]
    def __unicode__(self):
        return self.name
    """
    A zone represents a grouping of lights.

    Zones are rooms, and under this control schema rooms are controlled
    individually. Only special cases like group 0 controls the whole house.
    """
    name = models.CharField(max_length=100, unique=True)
    """
    Private declares that this zone can only be controlled
    by a certain subset of users.
    """
    private = models.BooleanField(default=False)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def as_json(self):
        """
        Returns the zone as JSON including all of its lights.
        """
        base_json = {'name' : self.name, 'lights' : []}
        for light in Light.objects.filter(zone=self):
            base_json['lights'].append(light.as_json())
        return base_json

class Scene(models.Model):
    class Meta:
        ordering = ['name',]
    def __unicode__(self):
        return self.name
    """
    A scene represents a setting on a zone of lights.

    Scene may optionally affect each light in the zone.
    """
    zone = models.ForeignKey('Zone')
    name = models.CharField(max_length=100, unique=True)
    
