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
Task.objects.all().delete()

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
    'colorloop' : False,
}
create_global_scene(off, 'Off')
# Create the 'white' scenes
white = {
    'on' : True,
    'sat' : 0,
    'bri' : 255,
    'colorloop' : False,
}
create_global_scene(white, 'White')
# Create the 'warm' scenes
warm = {
    'on' : True,
    'hue' : 3000,
    'sat' : 100,
    'bri' : 255,
    'colorloop' : False,
}
create_global_scene(warm, 'Warm')
# Create the 'Red' scenes
red = {
    'on' : True,
    'hue' : 0,
    'sat' : 255,
    'bri' : 255,
    'colorloop' : False,
}
create_global_scene(red, 'Red')
# Create the 'saturated random' scene
random = {
    'on' : True,
    'random' : True,
    'sat' : 255,
    'bri' : 255,
    'colorloop' : False,
}
create_global_scene(random, 'Saturated Random')
# Create the 'light random' scene
light_random = {
    'on' : True,
    'random' : True,
    'sat' : 100,
    'bri' : 255,
    'colorloop' : False,
}
create_global_scene(light_random, 'Light Random')
# Create the 'colorloop' scene
colorloop = {
    'colorloop' : True
}
create_global_scene(colorloop, 'Colorloop')

# Create the living room movie mode scene
movie_mode_off = [2,18,19,23,24,25, 30]
zone = Zone.objects.get(name='Living Room')
tasks = []
# Create the off tasks
off_instructions = {
    'on' : False
}
for light_which in movie_mode_off:
    light = Light.objects.get(which=light_which)
    instructions = json.dumps(off_instructions)
    task = Task(light=light, instructions=instructions)
    task.save()
    tasks.append(task)

movie_mode_on = [6,7,9,11,13,14,26]
on_instructions = {
    'on' : True,
    'bri' : 50,
    'sat' : 255
}
color_dict = {
    6 : 28302,
    7 : 3545,
    9 : 44287,
    11 : 64034,
    13: 47939,
    14 : 3105,
    26 : 4500,
}
colorloop_dict = {
    6 : True,
    7 : False,
    9 : False,
    11 : False,
    13: True,
    14 : True,
    26: False,
}
for light_which in movie_mode_on:
    light = Light.objects.get(which=light_which)
    _instructions = on_instructions.copy()
    _instructions['hue'] = color_dict[light_which]
    _instructions['colorloop'] = colorloop_dict[light_which]
    if _instructions['colorloop']:
        _instructions['bri'] = 255
    if light_which == 3:
        _instructions['bri'] = 0
    instructions = json.dumps(_instructions)
    task = Task(light=light, instructions=instructions)
    task.save()
    tasks.append(task)

# Create the movie mode scene
scene = Scene(zone=zone, name='Movie Mode')
scene.save()
for task in tasks:  
    scene.tasks.add(task)
scene.save()

# Create my light / colorloop mode
tasks = []
white = [2, 18, 19, 11, 26]
colorloop = [9, 6, 14, 13, 23, 7, 24, 25, 30]
white_instructions = {
    'on' : True,
    'hue' : 0,
    'bri' : 255,
    'sat' : 0,
    'colorloop' : False,
}
colorloop_instructions = {
    'on' : True,
    'random' : True,
    'colorloop' : True,
    'sat' : 255,
    'bri' : 255,
}
for light_which in white:
    light = Light.objects.get(which=light_which)
    instructions = json.dumps(white_instructions)
    task = Task(light=light, instructions=instructions)
    task.save()
    tasks.append(task)
for light_which in colorloop:
    light = Light.objects.get(which=light_which)
    instructions = json.dumps(colorloop_instructions)
    task = Task(light=light, instructions=instructions)
    task.save()
    tasks.append(task)

# Create my scene
scene = Scene(zone=zone, name="Tyler's")
scene.save()
for task in tasks:  
    scene.tasks.add(task)
scene.save()

# Create Tyler's for room
zone = Zone.objects.get(name='Tylers Room')
white = [29, 1, 17, 15, 16]
colorloop = [28, 10, 8, 3]
tasks = []
for light_which in white:
    light = Light.objects.get(which=light_which)
    instructions = json.dumps(white_instructions)
    task = Task(light=light, instructions=instructions)
    task.save()
    tasks.append(task)
for light_which in colorloop:
    light = Light.objects.get(which=light_which)
    instructions = json.dumps(colorloop_instructions)
    task = Task(light=light, instructions=instructions)
    task.save()
    tasks.append(task)

# Create my scene
scene = Scene(zone=zone, name="Tyler's")
scene.save()
for task in tasks:  
    scene.tasks.add(task)
scene.save()