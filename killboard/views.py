import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from helpers.eve_api_scopes import READ_KILLMAIL_PILOT
from helpers.static import INVENTORY_POSITIONS
from killboard.killmails.process import download_killmails
from killboard.models import Token
from killboard.schema.killmail import Killmail


def index(request):
    killmails = Killmail.objects.all().order_by('-km_date')[:10]  # type: [Killmail]
    return render(request, 'killmails.html', context={'killmails': killmails})


def open_killmail(request, killmail_id):
    killmail = Killmail.objects.get(id=killmail_id)
    return render(request, 'killmail.html', context={'killmail': killmail, 'inventory_positions': INVENTORY_POSITIONS})


def base(request):
    return render(request, 'base.html')


@login_required(login_url='/login')
def process_killmails(request):
    token = Token.objects.filter(user__pk=request.user.pk).require_scopes(READ_KILLMAIL_PILOT).require_valid()
    if not token:
        logging.error('Unable to get token for user %s', request.user.username)
    token = token[0]

    client = token.get_esi_client()
    mails = client.Killmails.get_characters_character_id_killmails_recent(character_id=token.character_id)
    result = mails.result()
    logging.debug('Got %s killmails', len(result))
    results = list(download_killmails(result, client))
    answer_dict = {
        'created': results.count(True),
        'updated': results.count(False),
        'total': len(results)
    }

    return render(request, 'generated.html', context=answer_dict)


@login_required(login_url='/login')
def secret(request):
    return HttpResponse('You are welcome!', status=200)

