from django.conf.urls import patterns, url
from authentication import views

urlpatterns = patterns('',
  url(r'^login/?$', views.LogIn.as_view()),
  url(r'^change_password/?$', views.ChangePassword.as_view()),
)
