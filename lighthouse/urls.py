from django.conf.urls import patterns, url
from lighthouse import views

urlpatterns = patterns('',
  url(r'^lights/?$', views.Lights.as_view()),
  url(r'^zones/?$', views.Zones.as_view()),
  url(r'^alert/?$', views.Alert.as_view()),
)
