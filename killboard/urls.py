from django.urls import path

from killboard import authentication
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('secret', views.secret, name='secret'),

    # Authentication
    path('login', authentication.process_login, name='login'),
    path('logout', authentication.process_logout, name='logout')
]
