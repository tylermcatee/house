from django.db import models
from django.conf import settings
from dispatch import *
import random
from dispatch_types import *
from task_types import *
from django.utils import timezone
import json, time

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
        return self.zone.user_authenticated(user)

    def save(self, *args, **kw):
        if self.pk is not None:
            orig = Light.objects.get(pk=self.pk)
            # Name
            if orig.name != self.name:
                Dispatch(self.dispatch_type).update({
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
                Dispatch(self.dispatch_type).update(resource)
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

    def alert(self):
        """
        Calls the alert function for this light.
        """
        Dispatch(self.dispatch_type).alert(self.which)
        self.on = True
        self.save()

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

    def execute_instructions_single(self, user, instructions_single):
        if self.user_authenticated(user):
            instructions = json.loads(instructions_single)
            if 'name' in instructions:
                self.name = instructions['name']
            if 'on' in instructions:
                self.on = instructions['on']
            if 'bri' in instructions:
                self.bri = instructions['bri']
            if 'hue' in instructions:
                self.hue = instructions['hue']
            if 'sat' in instructions:
                self.sat = instructions['sat']
            if 'colorloop' in instructions:
                self.colorloop = instructions['colorloop']
            self.save()


class TaskInstructionsSingle(models.Model):
    """
    A single state change, using just JSON formatted char field.
    """
    light = models.ForeignKey('Light')
    instructions = models.CharField(max_length=2000)

    def as_json(self):
        return {
            'light' : self.light.as_json(),
            'instructions' : json.loads(self.instructions)
        }

class Task(models.Model):
    """
    A Task represents a change on the database, or start of a running thread.
    """
    task_type = models.IntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    # The difference between created and executed is for alarm based tasks
    created = models.DateTimeField(auto_now_add=True)
    executed = models.DateTimeField(null=True, blank=True)
    # Eventually we will add "repeating" functionality to tasks, where a task
    # will just re-schedule itself when it finishes

    # JSON formatted instructions dumped here in a char field
    single_instructions = models.ForeignKey('TaskInstructionsSingle')

    def execute(self):
        """
        Executes the task.
        """
        if self.executed:
            raise("Already executed this task.")

        if self.task_type == task_type_single:
            # Execute the single instruction
            self.single_instructions.light.execute_instructions_single(self.user, self.single_instructions.instructions)
        else:
            raise("Task type not supported")

        # Update the executed to be now
        self.executed = timezone.now()
        self.save()

    def as_json(self):
        """
        Returns the JSON version of the task.
        """
        json = {
            'task_type' : self.task_type,
            'user' : self.user.username,
        }

        if self.task_type == task_type_single:
            json['instructions'] = self.single_instructions.as_json()
        else:
            raise("Task type not supported")

        created = int(time.mktime(self.created.timetuple())*1000)
        json['created'] = created
        if self.executed:
            executed = int(time.mktime(self.executed.timetuple())*1000)
            json['executed'] = executed
            
        return json

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

    def user_authenticated(self, user):
        if self.private:
            if user:
                return user in self.users.all()
            else:
                return False
        # If private is false, everyone has access
        return True

    def as_json(self):
        """
        Returns the zone as JSON including all of its lights.
        """
        base_json = {'name' : self.name, 'lights' : []}
        for light in Light.objects.filter(zone=self):
            base_json['lights'].append(light.as_json())
        return base_json

    def lights(self):
        return Light.objects.filter(zone=self)

    """
    BETA release short cuts.
    """

    def off(self):
        lights = self.lights()
        for light in lights:
            light.on = False
            light.save()

    def white(self):
        lights = self.lights()
        for light in lights:
            light.on = True
            light.sat = 0
            light.save()

    def random(self):
        self.lights().update(on=True)
        for light in self.lights():
            light.sat = 255
            light.random() # Saves
    
