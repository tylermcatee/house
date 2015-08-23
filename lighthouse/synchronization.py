import models
from dispatch import *
from dispatch_hue import *

def copy_single_task_data(data):
    """
    A convenience method for taking single task data
    and returning an appropriate array.
    """
    copied_data = {}

    if 'name' in data:
        copied_data['name'] = data['name']
    if 'on' in data:
        on = data['on']
        if type(on) is bool:
            copied_data['on'] = on
    if 'bri' in data:
        bri = data['bri']
        if type(bri) is int:
            if bri >= 0 and bri <= 255:
                copied_data['bri'] = bri
    if 'hue' in data:
        hue = data['hue']
        if type(hue) is int:
            if hue >= 0 and hue <= PHILLIPS_HUE_MAX_HUE:
                copied_data['hue'] = hue
    if 'sat' in data:
        sat = data['sat']
        if type(sat) is int:
            if sat >= 0 and sat <= 255:
                copied_data['sat'] = sat
    if 'colorloop' in data:
        colorloop = data['colorloop']
        if type(colorloop) is bool:
            copied_data['colorloop'] = colorloop

    return copied_data

def synchronize_hue():
    """
    Calls to the bridge and updates all hue database states
    that may have changed.
    """
    light_state = Dispatch(dispatch_type_hue).get({'which' : 'all'})
    resources = light_state['resource']
    for resource in resources:
        update_hue(resource)

def update_light(light, state, key):
    if key in state:
        value = state[key]
        current_value = getattr(light, key)
        if value != current_value:
            setattr(light, key, value)
    return light

def update_hue(resource):
    """
    Updates our backing store with the light information from
    the bridge, so that the admin can go ahead and set permissions
    on lights.
    """
    which = int(resource['id'])
    
    try:
        light = models.Light.objects.get(which=which)
    except:
        light = models.Light(which=which, zone=models.default_zone())

    name = resource['name']
    if light.name != name:
        light.name = name

    # Start variables
    state = resource['state']
    state_variables = ['on', 'bri', 'hue', 'sat', 'reachable']
    for state_variable in state_variables:
        light = update_light(light, state, state_variable)
    # Special case for colorloop
    if 'effect' in state:
        colorloop = state['effect']
        if colorloop == 'colorloop':
            colorloop = True
        else:
            colorloop = False
        if light.colorloop != colorloop:
            light.colorloop = colorloop

    light.dispatch_type = dispatch_type_hue
    light.save()