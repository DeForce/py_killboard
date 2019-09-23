from killboard.schema.alliance import Alliance
from killboard.schema.character import Character
from killboard.schema.corporation import Corporation
from killboard.schema.ship import Ship
from killboard.schema.solar_system import SolarSystem


class APIHelper(object):
    def __init__(self, client):
        self.api = client

    def process_class(self, json_data, cls, pk):
        obj, created = getattr(cls, 'objects').get_or_create(id=pk)
        if created:
            obj.process(json_data, self)
            obj.save()
        return obj

    def process_character(self, json_data):
        return self.process_class(json_data, Character, json_data['character_id'])

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
