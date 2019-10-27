from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^orders/commit/$', views.OrderComView.as_view(),name='commit'),


]