import time, random
from http import *

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