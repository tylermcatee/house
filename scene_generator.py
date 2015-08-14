import os, sys, time, random
my_path = os.path.dirname(os.path.realpath(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'house.settings'
import django
django.setup()
from lighthouse.models import *
from lighthouse.synchronization import *
import json

synchronize_hue()

# WARNING: Deletes all scenes!
Scene.objects.all().delete()

def create_global_scene(instructions, name):
    _instructions = json.dumps(instructions)

    # Give this scene to every zone
    for zone in Zone.objects.all():
        # Create the tasks
        tasks = []
        for light in zone.lights():
            task = Task(light=light, instructions=_instructions)
            task.save()
            tasks.append(task)
        # Create the scene
        scene = Scene(zone=zone, name=name)
        scene.save()
        for task in tasks:  
            scene.tasks.add(task)
        scene.save()

# Create the 'off' scenes
off = {
    'on' : False,
}
create_global_scene(off, 'Off')
# Create the 'white' scenes
white = {
    'on' : True,
    'sat' : 0,
}
create_global_scene(white, 'White')
# Create the 'saturated random' scene
random = {
    'random' : True,
    'sat' : 255
}
create_global_scene(random, 'Saturated Random')
# Create the 'light random' scene
light_random = {
    'random' : True,
    'sat' : 100,
}
create_global_scene(light_random, 'Light Random')
# Create the 'colorloop' scene
colorloop = {
    'colorloop' : True
}
create_global_scene(colorloop, 'Colorloop')
# Create the 'colorloop off' scene
colorloop_off = {
    'colorloop' : False
}
create_global_scene(colorloop_off, 'Colorloop Off')
