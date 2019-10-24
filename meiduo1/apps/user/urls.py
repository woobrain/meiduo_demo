from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register/$', views.Register.as_view(),name='register'),
    url(r'^login/$', views.LoginView.as_view(),name='login'),
    url(r'^logout/$', views.LogoutView.as_view(),name='logout'),
    url(r'emails/$', views.EmailView.as_view(),name='emails'),
    url(r'emailsactive/$', views.Emailactive.as_view(),name='emailsactive'),
    url(r'^center/$', views.CenterView.as_view(),name='center'),
    url(r'^site/$', views.SiteView.as_view(),name='site'),
    url(r'^addresses/create/$', views.AddView.as_view(),name='add'),
    url(r'^addresses/$', views.AddressView.as_view(),name='address'),
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view(),name='address_id'),
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view(),name='default_id'),
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view(),name='title'),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/$', views.RegisterUsernameCountView.as_view(),name='username'),
    url(r'^mobile/(?P<mobile>[1][345789]\d{9})/$', views.RegisterUserPhoneCount.as_view(),name='mobile'),
    # url(r'code/$', views.RegisterUsersmsCount.as_view(),name='sms'),

]