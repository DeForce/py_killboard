from django.db import models

from killboard.managers import EVEClassManager
from killboard.schema.alliance import Alliance
from killboard.schema.corporation import Corporation
from killboard.schema.ship import Ship, ItemType


class Character(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    alliance = models.ForeignKey(Alliance, related_name='char_alliance', on_delete=models.DO_NOTHING, null=True)
    corporation = models.ForeignKey(
        Corporation, related_name='char_corporation', on_delete=models.DO_NOTHING, null=True)

    objects = EVEClassManager()
    api = None

    def process(self, json_data, client):
        self.api = client
        char = client.api.Character.get_characters_character_id(character_id=self.id).result()
        self.name = char['name']
        self.save()

        corp = self.api.process_corporation(json_data)
        if corp:
            self.corporation = corp

        alliance = self.api.process_alliance(json_data)
        if alliance:
            self.alliance = alliance


class Attacker(models.Model):
    character = models.ForeignKey(Character, on_delete=models.DO_NOTHING, null=True)
    corporation = models.ForeignKey(Corporation, on_delete=models.DO_NOTHING, null=True)
    alliance = models.ForeignKey(Alliance, on_delete=models.DO_NOTHING, null=True)

    ship = models.ForeignKey(Ship, on_delete=models.DO_NOTHING)
    weapon = models.ForeignKey(ItemType, on_delete=models.DO_NOTHING, null=True)
    damage_done = models.FloatField()
    final_blow = models.BooleanField()

    objects = EVEClassManager()

    def process(self, item, api):
        if item['character_id']:
            self.character = Character.objects.get(id=item['character_id'])
        self.corporation = self.character.corporation
        if self.character.alliance:
            self.alliance = self.character.alliance

        self.ship, _ = Ship.objects.get_or_create_from_code(item['ship_type_id'], item, api)
        self.weapon, _ = ItemType.objects.get_or_create_from_code(item['weapon_type_id'], item, api)
        self.damage_done = item['damage_done']
        self.final_blow = item['final_blow']
