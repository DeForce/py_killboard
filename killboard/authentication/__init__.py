import logging
from functools import wraps
import random

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser, User
from django.http import Http404
from django.shortcuts import redirect
from requests_oauthlib import OAuth2Session

from helpers.eve_api_scopes import ALL_SCOPES
from killboard import app_settings
from killboard.models import Token, Scope

logger = logging.getLogger(__name__)


def sso(request):
    logger.debug("Received callback for {0} session {1}".format(request.user, request.session.session_key[:5]))
    redirect_back = request.session.get('redirect_back', '/')
    code = request.GET.get('code', None)
    state = request.GET.get('state', None)

    if not state == request.session['state']:
        logger.error('Unable to validate request, dropping')
        return Http404('Invalid state')

    oauth = OAuth2Session(app_settings.ESI_SSO_CLIENT_ID, redirect_uri=app_settings.ESI_SSO_CALLBACK_URL)
    token = oauth.fetch_token(app_settings.ESI_TOKEN_URL, client_secret=app_settings.ESI_SSO_CLIENT_SECRET,
                              code=code)
    r = oauth.request('get', app_settings.ESI_TOKEN_VERIFY_URL)
    r.raise_for_status()
    token_data = r.json()

    if isinstance(request.user, AnonymousUser):
        if not User.objects.filter(username=token_data['CharacterName']).exists():
            user = User(username=token_data['CharacterName'])
            user.save()
        else:
            user = User.objects.get(username=token_data['CharacterName'])
        login(request, user)
    else:
        user = request.user

    token = Token.objects.create(
        character_id=token_data['CharacterID'],
        character_name=token_data['CharacterName'],
        character_owner_hash=token_data['CharacterOwnerHash'],
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        token_type=token_data['TokenType'],
        user=user
    )

    if 'Scopes' in token_data:
        for s in token_data['Scopes'].split():
            try:
                scope = Scope.objects.get(name=s)
                token.scopes.add(scope)
            except Scope.DoesNotExist:
                # This scope isn't included in a data migration. Create a placeholder until it updates.
                try:
                    help_text = s.split('.')[1].replace('_', ' ').capitalize()
                except IndexError:
                    # Unusual scope name, missing periods.
                    help_text = s.replace('_', ' ').capitalize()
                scope = Scope.objects.create(name=s, help_text=help_text)
                token.scopes.add(scope)
        logger.debug("Added {0} scopes to new token.".format(token.scopes.all().count()))

    queryset = Token.objects.get_queryset().equivalent_to(token)

    if queryset.exists():
        logger.debug(
            "Identified {0} tokens equivalent to new token. Updating access and refresh tokens.".format(
                queryset.count()))
        queryset.update(
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            created=token.created,
        )
        if queryset.filter(user=token.user).exists():
            logger.debug("Equivalent token with same user exists. Deleting new token.")
            token.delete()
            token = queryset.filter(user=token.user)[0]  # pick one at random
    token.save()
    return redirect(redirect_back)


def process_login(request):
    if not request.session.exists(request.session.session_key):
        logger.debug("Creating new session before redirect.")
        request.session.create()

    url = request.get_full_path()
    scopes = ALL_SCOPES
    oauth = OAuth2Session(app_settings.ESI_SSO_CLIENT_ID, redirect_uri=app_settings.ESI_SSO_CALLBACK_URL, scope=scopes)
    redirect_url, state = oauth.authorization_url(app_settings.ESI_OAUTH_LOGIN_URL)

    logger.debug("Redirecting {0} session {1} to SSO. Callback will be redirected to {2}".format(
        request.user, request.session.session_key[:5], url))
    request.session['state'] = state

    redirect_after_url = request.GET.get('next')
    if redirect_after_url:
        request.session['redirect_back'] = redirect_after_url

    return redirect(redirect_url)


@login_required(login_url='/login')
def process_logout(request):
    logout(request)
    return redirect('/')
