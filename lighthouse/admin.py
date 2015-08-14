from django import forms
from django.contrib import admin
from models import *

class ZoneChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(Zone, ZoneAdmin)

def randomize_lights(modeladmin, request, queryset):
    for light in queryset:
        light.random()

class LightAdmin(admin.ModelAdmin):
    class Media:
        js = ['lightadmin.js', ]
    list_display = ('name', 'dispatch_type', 'which', 'zone', 'reachable', 'on', 'bri', 'hue', 'sat', 'colorloop')
    actions = [randomize_lights]

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'zone':
            kwargs['form_class'] = ZoneChoiceField
            kwargs['queryset'] = Zone.objects.order_by('name')
        return super(LightAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        
admin.site.register(Light, LightAdmin)