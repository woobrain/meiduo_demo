from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'', views.Register.as_view())

]