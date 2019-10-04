from django.urls import path

from killboard import authentication
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('killmail/<int:killmail_id>', views.open_killmail, name='open_killmail'),
    path('character/<int:character_id>', views.open_character, name='open_character'),
    path('corporation/<int:corporation_id>', views.open_corporation, name='open_corporation'),
    path('alliance/<int:alliance_id>', views.open_alliance, name='open_alliance'),
    path('system/<int:solar_system_id>', views.open_system, name='open_system'),

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
