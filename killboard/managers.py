import logging
from datetime import timedelta

import requests
from django.db import models
from django.utils.six import string_types
from django.utils import timezone
from requests_oauthlib import OAuth2Session

from killboard import app_settings
from killboard.errors import TokenError, IncompleteResponseError

logger = logging.getLogger(__name__)


def _process_scopes(scopes):
    if scopes is None:
        # support filtering by no scopes with None passed
        scopes = []
    if not isinstance(scopes, models.QuerySet) and len(scopes) == 1:
        # support a single space-delimited string inside a list because :users:
        scopes = scopes[0]
    # support space-delimited string scopes or lists
    if isinstance(scopes, string_types):
        scopes = set(scopes.split())
    return set(str(s) for s in scopes)


class TokenQueryset(models.QuerySet):
    def get_expired(self):
        """
        Get all tokens which have expired.
        :return: All expired tokens.
        :rtype: :class:`esi.managers.TokenQueryset`
        """
        max_age = timezone.now() - timedelta(seconds=app_settings.ESI_TOKEN_VALID_DURATION)
        return self.filter(created__lte=max_age)

    def bulk_refresh(self):
        """
        Refreshes all refreshable tokens in the queryset.
        Deletes any tokens which fail to refresh.
        Deletes any tokens which are expired and cannot refresh.
        Excludes tokens for which the refresh was incomplete for other reasons.
        """
        session = OAuth2Session(app_settings.ESI_SSO_CLIENT_ID)
        auth = requests.auth.HTTPBasicAuth(app_settings.ESI_SSO_CLIENT_ID, app_settings.ESI_SSO_CLIENT_SECRET)
        incomplete = []
        for model in self.filter(refresh_token__isnull=False):
            try:
                model.refresh(session=session, auth=auth)
                logging.debug("Successfully refreshed {0}".format(repr(model)))
            except TokenError:
                logger.info("Refresh failed for {0}. Deleting.".format(repr(model)))
                model.delete()
            except IncompleteResponseError:
                incomplete.append(model.pk)
        self.filter(refresh_token__isnull=True).get_expired().delete()
        return self.exclude(pk__in=incomplete)

    def require_valid(self):
        """
        Ensures all tokens are still valid. If expired, attempts to refresh.
        Deletes those which fail to refresh or cannot be refreshed.
        :return: All tokens which are still valid.
        :rtype: :class:`esi.managers.TokenQueryset`
        """
        expired = self.get_expired()
        valid = self.exclude(pk__in=expired)
        valid_expired = expired.bulk_refresh()
        return valid_expired | valid

    def require_scopes(self, scope_string):
        """
        :param scope_string: The required scopes.
        :type scope_string: Union[str, list]
        :return: The tokens with all requested scopes.
        :rtype: :class:`esi.managers.TokenQueryset`
        """
        scopes = _process_scopes(scope_string)
        if not scopes:
            # asking for tokens with no scopes
            return self.filter(scopes__isnull=True)
        from .models import Scope
        scope_pks = Scope.objects.filter(name__in=scopes).values_list('pk', flat=True)
        if not len(scopes) == len(scope_pks):
            # there's a scope we don't recognize, so we can't have any tokens for it
            return self.none()
        tokens = self.all()
        for pk in scope_pks:
            tokens = tokens.filter(scopes__pk=pk)
        return tokens

    def require_scopes_exact(self, scope_string):
        """
        :param scope_string: The required scopes.
        :type scope_string: Union[str, list]
        :return: The tokens with only the requested scopes.
        :rtype: :class:`esi.managers.TokenQueryset`
        """
        num_scopes = len(_process_scopes(scope_string))
        pks = [v['pk'] for v in self.annotate(models.Count('scopes')).require_scopes(scope_string).filter(
            scopes__count=num_scopes).values('pk', 'scopes__id')]
        return self.filter(pk__in=pks)

    def equivalent_to(self, token):
        """
        Gets all tokens which match the character and scopes of a reference token
        :param token: :class:`esi.models.Token`
        :return: :class:`esi.managers.TokenQueryset`
        """
        return self.filter(character_id=token.character_id).require_scopes_exact(token.scopes.all()).filter(
            models.Q(user=token.user) | models.Q(user__isnull=True)).exclude(pk=token.pk)


class TokenManager(models.Manager):
    def get_queryset(self):
        """
        Replace base queryset model with custom TokenQueryset
        :rtype: :class:`esi.managers.TokenQueryset`
        """
        return TokenQueryset(self.model, using=self._db)


class EVEClassManager(models.Manager):
    def get_or_create_from_code(self, i_id, json_data, api):
        try:
            return self.get(id=i_id), False
        except self.model.DoesNotExist:
            item = self.model(id=i_id)
            item.process(json_data, api)
            item.save()
            return item, True
