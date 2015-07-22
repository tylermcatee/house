from django.contrib import admin
from models import *

# Register your models here.
class UserPhotoAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserPhoto, UserPhotoAdmin)