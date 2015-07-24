from __future__ import absolute_import

import time, random
from beautifulhue.api import Bridge

from celery.task import task
from http import *

living_room = [11, 13, 19, 18, 23, 3, 2, 7, 6, 9, 14]
tylers_room = [10, 15, 16, 1, 8, 17]
BRIDGE_IP = '192.168.1.42'
USERNAME = 'newdeveloper'

def update(resource, debug=False):
    """
    @summary: Rename lights, or set a light's state, as determined by the\
              resource object.
    """

    request = Request()
    if (resource['data'].has_key('attr')):
        service = 'lights/{id}'.format(id=resource['which'])
        data = resource['data']['attr']
    elif (resource['data'].has_key('state')):
        service = 'lights/{id}/state'.format(id=resource['which'])
        data = resource['data']['state']
    else:
        raise Exception('Unknown data type.')

    path = 'api/{username}/{service}'.format(
                                           username=USERNAME,
                                           service=service
                                       )
    url = 'http://{bridge_ip}/{path}'.format(bridge_ip=BRIDGE_IP,
                                             path=path)
    
    status, content = request.put(url, data)

    if debug:
        return dict(info=status, resource=content)
    else:
        return dict(resource=content)

@task
def dispatch_task_light(which, on, hue, sat, bri, transitiontime):
    """
    Sets the state of a single light

    @param which : Which light we are setting, same as the bridge ID.
    @param on : Whether or not the light should be on
    @param hue : The color of the light
    @param sat : How saturated the color is
    @param bri : How bright the light is
    @param transitiontime: In hundreds of miliseconds (i.e. 10 = 1 second)
    """
    resource = {
        'which' : which,
        'data' : {
            'state' : {
                'on' : on
            }
        }
    }

    # Don't send all the parameters for the update if we're turning it off
    if not on:
        update(resource)
        return

    resource['data']['state'] = {
        'on' : on,
        'hue' : hue,
        'sat' : sat,
        'bri' : bri,
        'transitiontime' : transitiontime
    }

    update(resource)
    return

@task
def dispatch_task_light_forever(dispatch_task_list):
    """
    Does a custom color loop on of dispatch commands

    @param dispatch_task_list : A list of dictionaries, each specifying a state
    of the light to go to, as well as a delay before the next is read. We will 
    loop through this forever, until the task is canceled.

        @param lights : A list of lights to apply this to
        @param on : Whether or not the light should be on
        @param hue : The color of the light
        @param sat : How saturated the color is
        @param bri : How bright the light is
        @param transitiontime : In hundreds of miliseconds (i.e. 10 = 1 second)
        @param delay : How long until the next setting
    """
    start_time = time.time()
    delayed_time = 0
    while True:
        for dispatch_task in dispatch_task_list:
            on = dispatch_task['on']
            hue = dispatch_task['hue']
            sat = dispatch_task['sat']
            bri = dispatch_task['bri']
            transitiontime = dispatch_task['transitiontime']
            delay = dispatch_task['delay']

            lights = dispatch_task['lights']
            for light in lights:
                # Call the dispatch
                dispatch_task_light(light, on, hue, sat, bri, transitiontime)

            # Delay
            time.sleep(delay)

@task
def lights_random(on = True, sat=255, bri=255, transitiontime=10):
    for _ in living_room:
        dispatch_task_light(_, on, random.randint(0, 65280), sat, bri, transitiontime)

@task
def lights_random_forever(rotationtime = 1, sat=255, bri=255):
    while True:
        lights_random(sat, bri, rotationtime * 10)
        time.sleep(rotationtime)
