import json
from lighthouse.models import *
from django.contrib.auth.models import User

user = User.objects.all()[0]
tv_left_up_left = Light.objects.get(which=23)
tv_left_up_right = Light.objects.get(which=7)
red = {
    'on' : True,
    'hue' : 1,
    'sat' : 255,
}
_red = json.dumps(red)

task_1 = Task(light=tv_left_up_left, instructions=_red, user=user)
task_1.save()
task_2 = Task(light=tv_left_up_right, instructions=_red, user=user)
task_2.save()

zone = Zone.objects.all()[0]

scene = Scene(zone=zone)
scene.save()
scene.tasks.add(task_1)
scene.tasks.add(task_2)
scene.save()
scene.execute()