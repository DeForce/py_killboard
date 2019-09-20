from django.urls import path

from killboard import authentication
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('secret', views.secret, name='secret'),

    # Processing TODO: Create scheduled tasks
    path('process_killmails', views.process_killmails, name='process_killmails'),

    # Testing Base
    path('base', views.base, name='base'),

    # Authentication
    path('sso/callback', authentication.sso, name='sso'),
    path('login', authentication.process_login, name='login'),
    path('logout', authentication.process_logout, name='logout')
]
