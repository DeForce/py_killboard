from django.db import models

from killboard.managers import EVEClassManager


class ItemType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    objects = EVEClassManager()

    def process(self, json_data, client):
        item = client.api.Universe.get_universe_types_type_id(type_id=self.id).result()
        self.name = item['name']


class ShipType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    objects = EVEClassManager()


class Ship(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.ForeignKey(ShipType, related_name='corporation', on_delete=models.DO_NOTHING)

    objects = EVEClassManager()

    def process(self, json_data, client):
        ship = client.api.Universe.get_universe_types_type_id(type_id=self.id).result()
        self.name = ship['name']

        ship_type_dict = client.api.Universe.get_universe_groups_group_id(group_id=ship['group_id']).result()
        ship_type, created = ShipType.objects.get_or_create(id=ship_type_dict['group_id'], name=ship_type_dict['name'])

        self.type = ship_type
