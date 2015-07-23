from tasks import *
import time
from celery.task.control import revoke

which_1 = 9
which_2 = 23
which_3 = 11

color_red = 0
color_yellow = 12750
color_green = 25500
color_blue = 46920
color_pink = 56100

def get_scene(lights, color, transitiontime, delay):
    return {
        'on' : True,
        'hue' : color,
        'sat' : 255,
        'bri' : 255,
        'transitiontime' : transitiontime,
        'delay' : delay,
        'lights' : lights
    }

"""
Do a custom scene where they all sync to red every 10 seconds otherwise are not aligned.
"""

def scene_1(lights):
    scene_1 = [
        get_scene(lights, color_green, 70, 7),
        get_scene(lights, color_blue, 70, 7),
        get_scene(lights, color_red, 20, 2),
    ]
    return scene_1

def scene_2(lights):
    scene_2 = [
        get_scene(lights, color_green, 70, 7),
        get_scene(lights, color_yellow, 70, 7),
        get_scene(lights, color_red, 20, 2),
    ]
    return scene_2

def scene_3(lights):
    scene_3 = [
        get_scene(lights, color_green, 70, 7),
        get_scene(lights, color_pink, 70, 7),
        get_scene(lights, color_red, 20, 2),
    ]
    return scene_3

results = []
results.append(dispatch_task_light_forever.delay(scene_1([9, 13, 3, 6])))
results.append(dispatch_task_light_forever.delay(scene_2([23, 19, 2, 14])))
results.append(dispatch_task_light_forever.delay(scene_3([11, 18, 7])))

print("Press enter to continue...")
char = raw_input()
for result in results:
    print("Canceling task %s" % result.task_id)
    revoke(result.task_id, terminate=True)

print("Done.")