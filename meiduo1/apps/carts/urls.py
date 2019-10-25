from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^carts/$',views.CartsAddView.as_view(),name='addcart'),

]