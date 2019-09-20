from __future__ import unicode_literals
from celery import shared_task
import logging

from killboard.models import Token

logger = logging.getLogger(__name__)


@shared_task
def cleanup_token():
    """
    Delete expired :model:`esi.Token` models.
    """
    logger.debug("Triggering bulk refresh of all expired tokens.")
    Token.objects.all().get_expired().bulk_refresh()
