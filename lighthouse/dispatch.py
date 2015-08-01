import time, random
from http import *

class Dispatch:

    def __init__(self):
        self.BRIDGE_IP = '192.168.1.42'
        self.USERNAME = 'newdeveloper'

    def get(self, resource, debug=False):
        """
        @summary: Get all lights, get new lights, or get a specific light as\
                  determined by the resource object.
        """
        
        request = Request()
        services = {
            'all':{'service':'lights'},
            'new':{'service':'lights/new'}
        }
        if (isinstance(resource['which'], int)):
            resource['id'] = resource['which']
            resource['which'] = 'one'
        if (resource['which'] == 'one'):
            services['one'] = {'service':'lights/{id}'.format(id=resource['id'])}
        service = services[resource['which']]['service']
        path = 'api/{username}/{service}'.format(
                                                    username=self.USERNAME,
                                                    service=service
                                                )
        url = 'http://{bridge_ip}/{path}'.format(bridge_ip=self.BRIDGE_IP,
                                                 path=path)

        status, content = request.get(url, resource)
        if service == 'lights':
            lights = []
            for (k, v) in content.items():
                v['id'] = int(k)
                lights.append(v)
            if resource.has_key('verbose') and resource['verbose']:
                _lights = []
                for light in lights:
                    path = 'api/{username}/lights/{id}'.format(
                                                                  username=self.USERNAME,
                                                                  id=light['id']
                                                              )
                    url = 'http://{bridge_ip}/{path}'.format(bridge_ip=self.BRIDGE_IP,
                                                     path=path)
                    status, content = request.get(url, resource)
                    _lights.append(content)
                content = _lights
            else:
                content = lights


        if debug:
            return dict(info=status, resource=content)
        else:
            return dict(resource=content)

    def update(self, resource, debug=False):
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
                                               username=self.USERNAME,
                                               service=service
                                           )
        url = 'http://{bridge_ip}/{path}'.format(bridge_ip=self.BRIDGE_IP,
                                                 path=path)
        
        status, content = request.put(url, data)

        if debug:
            return dict(info=status, resource=content)
        else:
            return dict(resource=content)

    def dispatch_task_alert(self, which):
        """
        Sets a light to blink.

        @param which : Which light we are setting, same as the bridge ID.
        @discussion Also will turn the light on if it is off.
        """
        resource = {
            'which' : which,
            'data' : {
                'state' : {
                    'on' : True,
                    'alert' : 'select'
                }
            }
        }

        self.update(resource)
        return

    def dispatch_task_light(self, which, on, hue, sat, bri, transitiontime):
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
            self.update(resource)
            return

        resource['data']['state'] = {
            'on' : on,
            'hue' : hue,
            'sat' : sat,
            'bri' : bri,
            'transitiontime' : transitiontime
        }

        self.update(resource)
        return