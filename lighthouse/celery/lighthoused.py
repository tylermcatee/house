from celery import Celery
import time
from beautifulhue.api import Bridge
import random

app = Celery('lighthouse', broker='redis://localhost:6379/0')
living_room = [11, 13, 19, 18, 23, 3, 2, 7, 6, 9, 14]
BRIDGE_IP = '192.168.1.42'
USERNAME = 'newdeveloper'

@app.task
def lights_random():
    bridge = Bridge(device={'ip' : BRIDGE_IP}, user={'name' : USERNAME})
    for _ in living_room:
        resource = {
            'which' : _,
            'data' : {
                'state' : {
                    'hue' : random.randint(0, 65280),
                    'sat' : 255,
                    'bri' : 255
                }
            }
        }
        bridge.light.update(resource)