from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^oauth_callback', views.QLoginView.as_view(),name='qq'),
    # url(r'^oauth_callback', views.QLoginView.as_view(),name='qq'),


]