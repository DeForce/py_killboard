import logging
from itertools import chain

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render

from helpers.eve_api_scopes import READ_KILLMAIL_PILOT
from helpers.static import INVENTORY_POSITIONS, INV_FLAGS
from killboard.killmails.process import download_killmails
from killboard.models import Token
from killboard.schema.admin.allies import AllianceAllies, CorporationAllies, CharacterAllies
from killboard.schema.alliance import Alliance
from killboard.schema.character import Character
from killboard.schema.corporation import Corporation
from killboard.schema.killmail import Killmail
from killboard.schema.solar_system import SolarSystem


def create_top_list():
    alliances = AllianceAllies.objects.all()
    alliances = [Alliance.objects.get_or_create_from_code(ally.id, None) for ally in alliances]

    kills = Killmail.objects.filter(attackers__character__alliance__in=AllianceAllies.objects.all()).aggregate(
        dcount=Count('attackers__character'))
    pass


def index(request):
    killmails = Killmail.objects.all().order_by('-km_date')[:10]  # type: [Killmail]
    alliance = list(item.id for item in AllianceAllies.objects.all())
    corporations = list(item.id for item in CorporationAllies.objects.all())
    characters = list(item.id for item in CharacterAllies.objects.all())

    top_list = create_top_list()

    return render(request, 'killmails.html', context={'killmails': killmails,
                                                      'allies': alliance + corporations + characters})


def open_killmail(request, killmail_id):
    killmail = Killmail.objects.get(id=killmail_id)
    return render(request, 'killmail.html',
                  context={'killmail': killmail, 'inventory_positions': INVENTORY_POSITIONS, 'flags': INV_FLAGS})


def get_mails(kill_keys, loss_keys):
    kills = Killmail.objects.filter(**kill_keys).order_by('-km_date').distinct()[:30]
    losses = Killmail.objects.filter(**loss_keys).order_by('-km_date').distinct()[:30]
    killmails = sorted(chain(kills, losses), key=lambda x: x.km_date)[:30]

    return kills, losses, killmails


def open_character(request, character_id):
    kills, losses, killmails = get_mails({'attackers__character': character_id}, {'victim': character_id})

    stats = {
        'kills': kills.count(),
        'losses': losses.count()
    }
    character = Character.objects.get(id=character_id)
    return render(
        request, 'character.html',
        context={'killmails': killmails, 'character': character, 'stats': stats, 'allies': [character_id]})


def open_corporation(request, corporation_id):
    kills, losses, killmails = get_mails({'attackers__corporation': corporation_id}, {'corporation': corporation_id})

    stats = {
        'kills': kills.count(),
        'losses': losses.count()
    }
    corporation = Corporation.objects.get(id=corporation_id)
    return render(
        request, 'corporation.html',
        context={'killmails': killmails, 'corporation': corporation, 'stats': stats, 'allies': [corporation_id]})


def open_alliance(request, alliance_id):
    kills, losses, killmails = get_mails({'attackers__alliance': alliance_id}, {'alliance': alliance_id})

    stats = {
        'kills': kills.count(),
        'losses': losses.count()
    }
    alliance = Alliance.objects.get(id=alliance_id)
    return render(
        request, 'alliance.html',
        context={'killmails': killmails, 'alliance': alliance, 'stats': stats, 'allies': [alliance_id]})


def open_system(request, solar_system_id):
    kills = Killmail.objects.filter(solar_system=solar_system_id).order_by('-km_date').distinct()[:30]
    stats = {
        'kills': kills.count()
    }
    solar_system = SolarSystem.objects.get(id=solar_system_id)
    return render(
        request, 'solar_system.html',
        context={'killmails': kills, 'stats': stats, 'solar_system': solar_system})


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

