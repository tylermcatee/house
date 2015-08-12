from django.db import models
from django.conf import settings
from dispatch import *
import random
from dispatch_types import *

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

    # Identifies which dispatch object to use when changing state
    dispatch_type = models.IntegerField()

    # State variables
    on = models.BooleanField(default=False)
    bri = models.IntegerField(default=0)
    hue = models.IntegerField(default=0)
    sat = models.IntegerField(default=0)
    colorloop = models.BooleanField(default=False)
    reachable = models.BooleanField(default=False)

    def user_authenticated(self, user):
        if self.zone.private:
            if user:
                return user in self.zone.users.all()
            else:
                return False
        # If private is false, everyone has access
        return True

    def save(self, *args, **kw):
        if self.pk is not None:
            orig = Light.objects.get(pk=self.pk)

            # Name
            if orig.name != self.name:
                Dispatch().update({
                        'which' : self.which,
                        'data' : {
                            'attr' : {
                                'name' : self.name
                            }
                        }
                    })

            # State
            resource = {
                'which' : self.which,
                'data' : {
                    'state' : {}
                }
            }

            if self.on != orig.on:
                resource['data']['state']['on'] = self.on
            if self.bri != orig.bri:
                resource['data']['state']['bri'] = self.bri
            if self.hue != orig.hue:
                resource['data']['state']['hue'] = self.hue
            if self.sat != orig.sat:
                resource['data']['state']['sat'] = self.sat
            if self.colorloop != orig.colorloop:
                if self.colorloop:
                    colorloop_str = 'colorloop'
                else:
                    colorloop_str = 'none'
                resource['data']['state']['effect'] = colorloop_str

            # If we have resource to update, dispatch it
            if len(resource['data']['state'].keys()) > 0:
                Dispatch().update(resource)

        super(Light, self).save(*args, **kw)

    def as_json(self, user=None):
        """
        Returns the light description as json
        Also returns whether the user is authenticated
        """
        return {
            'which' : self.which, 
            'name' : self.name,
            'zone' : self.zone.name,
            'dispatch_type' : self.dispatch_type,
            'on' : self.on,
            'bri' : self.bri,
            'hue' : self.hue,
            'sat' : self.sat,
            'colorloop' : self.colorloop,
            'reachable' : self.reachable,
            'authenticated' : self.user_authenticated(user)
        }

    def random(self, hue = True, sat = False, bri = False):
        """
        Sets the light to random values for hue, sat, and bri.
        """
        if not self.hue and not self.sat and not self.bri:
            return # Do nothing
        if hue:
            self.hue = random.randint(0, 65280)
        if sat:
            self.sat = random.randint(0, 255)
        if bri:
            self.bri = random.randint(0, 255)
        self.save()

        

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
    
