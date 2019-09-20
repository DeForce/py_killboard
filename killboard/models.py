import datetime
import logging
import re

from celery.exceptions import ImproperlyConfigured
from django.conf import settings
from django.db import models
from django.utils import timezone
from oauthlib.oauth2 import InvalidGrantError
from oauthlib.oauth2.rfc6749.errors import InvalidTokenError, InvalidClientIdError, MissingTokenError, \
    InvalidClientError, TokenExpiredError
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

from killboard import app_settings
from killboard.errors import TokenInvalidError, IncompleteResponseError, NotRefreshableTokenError
from killboard.esi_api import esi_client_factory
from killboard.managers import TokenManager

logger = logging.getLogger(__name__)


class Scope(models.Model):
    """
    Represents an access scope granted by SSO.
    """
    name = models.CharField(max_length=100, unique=True, help_text="The official EVE name for the scope.")
    help_text = models.TextField(help_text="The official EVE description of the scope.")

    @property
    def friendly_name(self):
        try:
            return re.sub('_', ' ', self.name.split('.')[1]).strip()
        except IndexError:
            return self.name

    def __str__(self):
        return self.name


class Token(models.Model):
    """
    EVE Swagger Interface Access Token
    Contains information about the authenticating character and scopes granted to this token.
    Contains the access token required for ESI authentication as well as refreshing.
    """

    created = models.DateTimeField(auto_now_add=True)
    access_token = models.TextField(help_text="The access token granted by SSO.",
                                    editable=False)
    refresh_token = models.TextField(blank=True, default='',
                                     help_text="A re-usable token to generate new access tokens upon expiry.",
                                     editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True,
                             help_text="The user to whom this token belongs.")
    character_id = models.IntegerField(help_text="The ID of the EVE character who authenticated by SSO.")
    character_name = models.CharField(max_length=100,
                                      help_text="The name of the EVE character who authenticated by SSO.")
    token_type = models.CharField(max_length=100, choices=(('Character', 'Character'), ('Corporation', 'Corporation'),),
                                  default='Character', help_text="The applicable range of the token.")
    character_owner_hash = models.CharField(max_length=254,
                                            help_text="The unique string identifying this character and its owning EVE "
                                                      "account. Changes if the owning account changes.")
    scopes = models.ManyToManyField(Scope, blank=True, help_text="The access scopes granted by this token.")

    objects = TokenManager()

    def __str__(self):
        return "%s - %s" % (self.character_name, ", ".join(sorted(s.name for s in self.scopes.all())))

    def __repr__(self):
        return "<{}(id={}): {}, {}>".format(
            self.__class__.__name__,
            self.pk,
            self.character_id,
            self.character_name,
        )

    @property
    def can_refresh(self):
        """
        Determines if this token can be refreshed upon expiry
        """
        return bool(self.refresh_token)

    @property
    def expires(self):
        """
        Determines when the token expires.
        """
        return self.created + datetime.timedelta(seconds=app_settings.ESI_TOKEN_VALID_DURATION)

    @property
    def expired(self):
        """
        Determines if the access token has expired.
        """
        return self.expires < timezone.now()

    def refresh(self, session=None, auth=None):
        """
        Refreshes the token.
        :param session: :class:`requests_oauthlib.OAuth2Session` for refreshing token with.
        :param auth: :class:`requests.auth.HTTPBasicAuth`
        """
        logger.debug("Attempting refresh of {0}".format(repr(self)))
        if self.can_refresh:
            if not session:
                session = OAuth2Session(app_settings.ESI_SSO_CLIENT_ID)
            if not auth:
                auth = HTTPBasicAuth(app_settings.ESI_SSO_CLIENT_ID, app_settings.ESI_SSO_CLIENT_SECRET)
            try:
                token = session.refresh_token(app_settings.ESI_TOKEN_URL, refresh_token=self.refresh_token, auth=auth)
                logger.debug("Retrieved new token from SSO servers.")
                self.access_token = token['access_token']
                self.refresh_token = token['refresh_token']
                self.created = timezone.now()
                self.save()
                logger.debug("Successfully refreshed {0}".format(repr(self)))
            except (InvalidGrantError, InvalidTokenError, InvalidClientIdError) as e:
                logger.info("Refresh failed for {0}: {1}".format(repr(self), e))
                raise TokenInvalidError()
            except MissingTokenError as e:
                logger.info("Refresh failed for {0}: {1}".format(repr(self), e))
                raise IncompleteResponseError()
            except InvalidClientError:
                logger.debug("ESI client ID and secret rejected by remote. Cannot refresh.")
                raise ImproperlyConfigured('Verify ESI_SSO_CLIENT_ID and ESI_SSO_CLIENT_SECRET settings.')
        else:
            logger.debug("Not a refreshable token.")
            raise NotRefreshableTokenError()

    def get_esi_client(self, **kwargs):
        """
        Creates an authenticated ESI client with this token.
        :param kwargs: Extra spec versioning as per `esi.clients.esi_client_factory`
        :return: :class:`bravado.client.SwaggerClient`
        """
        return esi_client_factory(token=self, **kwargs)

    @classmethod
    def get_token_data(cls, access_token):
        session = OAuth2Session(app_settings.ESI_SSO_CLIENT_ID, token={'access_token': access_token})
        return session.request('get', app_settings.ESI_TOKEN_VERIFY_URL).json()

    def update_token_data(self, commit=True):
        logger.debug("Updating token data for {0}".format(repr(self)))
        if self.expired:
            if self.can_refresh:
                self.refresh()
            else:
                raise TokenExpiredError()
        token_data = self.get_token_data(self.access_token)
        logger.debug(token_data)
        self.character_id = token_data['CharacterID']
        self.character_name = token_data['CharacterName']
        self.character_owner_hash = token_data['CharacterOwnerHash']
        self.token_type = token_data['TokenType']
        logger.debug("Successfully updated token data.")
        if commit:
            self.save()

