from django.urls import path

from killboard import authentication
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('killmail/<int:killmail_id>', views.open_killmail, name='open_killmail'),

    # Processing TODO: Create scheduled tasks
    path('process_killmails', views.process_killmails, name='process_killmails'),

    # Testing Base
    path('base', views.base, name='base'),
    path('secret', views.secret, name='secret'),

    # Authentication
    path('sso/callback', authentication.sso, name='sso'),
    path('login', authentication.process_login, name='login'),
    path('logout', authentication.process_logout, name='logout')
]
