from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect
from esi.decorators import token_required

from helpers.eve_api_scopes import READ_KILLMAIL_PILOT, READ_KILLMAIL_CORP


def create_user(token):
    user = User(username=token.character_name, password=token.character_owner_hash)
    user.save()
    return user


@token_required([READ_KILLMAIL_PILOT, READ_KILLMAIL_CORP], new=True)
def process_login(request, token):
    if not User.objects.filter(username=token.character_name).exists():
        user = create_user(token)
    else:
        user = User.objects.filter(username=token.character_name)[0]
    login(request, user)
    return redirect('/')


@login_required()
def process_logout(request):
    logout(request)
    return redirect('/')
