from killboard.schema.alliance import Alliance
from killboard.schema.character import Character, Attacker
from killboard.schema.corporation import Corporation
from killboard.schema.ship import Ship, ItemType
from killboard.schema.solar_system import SolarSystem


class APIHelper(object):
    def __init__(self, client):
        self.api = client

    def process_class(self, json_data, cls, pk):
        obj, created = getattr(cls, 'objects').get_or_create_from_code(pk, json_data, self)
        return obj

    def process_character(self, json_data):
        return self.process_class(json_data, Character, json_data['character_id'])

    def process_attacker(self, json_data):
        character = self.process_character(json_data)
        ship = self.process_ship(json_data)
        weapon, _ = ItemType.objects.get_or_create_from_code(json_data['weapon_type_id'], json_data, self)
        obj, _ = Attacker.objects.get_or_create(
            character=character,
            ship=ship,
            weapon=weapon,
            damage_done=json_data['damage_done'],
            final_blow=json_data['final_blow']
        )
        obj.save()
        return obj

    def process_corporation(self, json_data):
        if json_data['corporation_id']:
            return self.process_class(json_data, Corporation, json_data['corporation_id'])

    def process_alliance(self, json_data):
        if json_data['alliance_id']:
            return self.process_class(json_data, Alliance, json_data['alliance_id'])

    def process_solar_system(self, json_data):
        if json_data['solar_system_id']:
            return self.process_class(json_data, SolarSystem, json_data['solar_system_id'])

    def process_ship(self, json_data):
        if json_data['ship_type_id']:
            return self.process_class(json_data, Ship, json_data['ship_type_id'])
