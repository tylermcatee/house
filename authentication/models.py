from django.contrib import admin
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

# Auth token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

# User photo

class UserPhoto(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, unique=True)
    photo = models.ImageField(upload_to='profilephotos', blank=True, null=True)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_photo(sender, instance=None, created=False, **kwargs):
    if created:
        UserPhoto.objects.create(user=instance)