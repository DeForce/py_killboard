import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from helpers.eve_api_scopes import READ_KILLMAIL_PILOT
from killboard.models import Token
from killboard.schema.killmail import Killmail


def index(request):
    killmails = Killmail.objects.all().order_by('-km_date')[:10]  # type: [Killmail]
    return render(request, 'index.html', context={'killmails': killmails})


def base(request):
    return render(request, 'base.html')


def write_killmail(km_dict, client):
    km_id = km_dict['killmail_id']
    create = False
    if Killmail.objects.filter(id=km_id).exists():
        km = Killmail.objects.get(id=km_id)
        km.update_mail(km_dict, client)
    else:
        create = True
        km = Killmail()
        km.create_mail(km_dict, client)
    km.save()
    return create


def get_killmail_data(k_hash, k_id, client):
    data = client.Killmails.get_killmails_killmail_id_killmail_hash(
        killmail_hash=k_hash, killmail_id=k_id)
    return data.result()


def download_killmails(killmails, client):
    for km in killmails:
        yield write_killmail(get_killmail_data(km['killmail_hash'], km['killmail_id'], client), client)


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

