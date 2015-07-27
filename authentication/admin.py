from django.contrib import admin
from models import *

# Register your models here.
class UserPhotoAdmin(admin.ModelAdmin):
    list_display=('get_user_name',)
    def get_user_name(self, obj):
        return obj.user.username + "'s photo"
admin.site.register(UserPhoto, UserPhotoAdmin)