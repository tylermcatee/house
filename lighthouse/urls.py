from django.conf.urls import patterns, url
from lighthouse import views

urlpatterns = patterns('',
  url(r'^lights/?$', views.Lights.as_view()),
)
