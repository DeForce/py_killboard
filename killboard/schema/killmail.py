import collections
import json

from django.db import models

from helpers.static import INV_FLAGS
from killboard.esi_api.client_helper import APIHelper
from killboard.managers import EVEClassManager
from killboard.schema.alliance import Alliance
from killboard.schema.character import Character
from killboard.schema.comment import Comment
from killboard.schema.corporation import Corporation
from killboard.schema.faction import Faction
from killboard.schema.ship import Ship, ItemType
from killboard.schema.solar_system import SolarSystem


class Attacker(object):
    def __init__(self, item, api):
        self.character = Character.objects.get(id=item['character_id'])
        self.ship = Ship.objects.get(id=item['ship_type_id'])
        self.weapon = ItemType.objects.get(id=item['weapon_type_id'])
        self.damage_done = item['damage_done']
        self.final_blow = item['final_blow']


class KillmailItem(object):
    def __init__(self, item, api):
        self.flag = INV_FLAGS.get(item['flag'])
        self.flag_id = item['flag']
        self.flag_name_text = self.flag['flagText']
        self.name = ItemType.objects.get(id=item['item_type_id']).name
        self.quantity_dropped = item['quantity_dropped'] if item['quantity_dropped'] else 0
        self.quantity_destroyed = item['quantity_destroyed'] if item['quantity_destroyed'] else 0


class Killmail(models.Model):
    # Base Info
    id = models.IntegerField(primary_key=True)
    km_date = models.DateTimeField()

    # Ship Info
    solar_system = models.ForeignKey(SolarSystem, related_name='solar_system', on_delete=models.DO_NOTHING)
    items_dict = models.TextField()
    pos_x = models.FloatField()
    pos_y = models.FloatField()
    pos_z = models.FloatField()
    ship_type = models.ForeignKey(Ship, related_name='ship', on_delete=models.DO_NOTHING)
    damage_taken = models.IntegerField()

    # Miscellaneous Info
    moon = models.IntegerField(null=True)
    war = models.IntegerField(null=True)

    # Char Info
    victim = models.ForeignKey(Character, related_name='victim', on_delete=models.DO_NOTHING)
    alliance = models.ForeignKey(Alliance, related_name='alliance', on_delete=models.DO_NOTHING, null=True)
    corporation = models.ForeignKey(Corporation, related_name='corporation', on_delete=models.DO_NOTHING)
    faction = models.ForeignKey(Faction, related_name='faction', on_delete=models.DO_NOTHING, null=True)

    attackers_dict = models.TextField()
    attackers = models.ManyToManyField(Character, related_name='attackers')
    comments = models.ManyToManyField(Comment, related_name='comments')

    objects = EVEClassManager()

    api = None

    @property
    def attackers_info(self):
        attackers = json.loads(self.attackers_dict)
        return {key: Attacker(value, self.api) for key, value in attackers.items()}

    @property
    def items_info(self):
        items = json.loads(self.items_dict)

        fill_inventory = collections.defaultdict(list)
        for key, value in items.items():
            item = KillmailItem(value, self.api)
            fill_inventory[item.flag_id].append(item)
        return fill_inventory

    def upload_attackers(self, attackers):
        for attacker in attackers:
            self.api.process_ship(attacker)

        return json.dumps({
            item['character_id']: item
            for item in attackers
        })

    def upload_items(self, items):
        for item in items:
            ItemType.objects.get_or_create_from_code(item['item_type_id'], item, self.api)

        return json.dumps({
            f"{item['item_type_id']}_{item['flag']}": item
            for item in items
        })

    def update_mail(self, mail, client):
        self.create_mail(mail, client)

    def create_mail(self, mail, client):
        self.api = APIHelper(client)

        self.id = mail['killmail_id']
        self.km_date = mail['killmail_time']
        self.pos_x = mail['victim']['position']['x']
        self.pos_y = mail['victim']['position']['y']
        self.pos_z = mail['victim']['position']['z']
        self.damage_taken = mail['victim']['damage_taken']
        self.moon = mail['moon_id']
        self.war = mail['war_id']
        self.attackers_dict = self.upload_attackers(mail['attackers'])
        self.items_dict = self.upload_items(mail['victim']['items'])

        solar_system = self.api.process_solar_system(mail)
        self.solar_system = solar_system
        self.ship_type = self.api.process_ship(mail['victim'])

        victim = self.api.process_character(mail['victim'])
        self.victim = victim

        corp = self.api.process_corporation(mail['victim'])
        if corp:
            self.corporation = corp

        alliance = self.api.process_alliance(mail['victim'])
        if alliance:
            self.alliance = alliance

        # self.faction = mail['victim']['faction_id']

        self.save()
        for attacker in mail['attackers']:
            attacker_obj = self.api.process_character(attacker)
            if attacker_obj:
                self.attackers.add(attacker_obj)
                ItemType.objects.get_or_create_from_code(attacker['weapon_type_id'], attacker, self.api)
        self.save()
