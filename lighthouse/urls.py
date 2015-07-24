from django.conf.urls import patterns, url
from lighthouse import views

urlpatterns = patterns('',
  url(r'^light/?$', views.Light.as_view()),
)
