from django.conf.urls import patterns, url
from authentication import views

urlpatterns = patterns('',
  url(r'^login/?$', views.LogIn.as_view()),
  url(r'^change_password/?$', views.ChangePassword.as_view()),
  url(r'^staff_member_get_token/?$', views.staff_member_get_token),
)
