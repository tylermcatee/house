from django.contrib import admin
from models import *

class LightAdmin(admin.ModelAdmin):
    list_display = ('name', 'which')
admin.site.register(Light, LightAdmin)

class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(Zone, ZoneAdmin)