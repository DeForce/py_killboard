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

    rigs = models.SmallIntegerField(default=0)
    high = models.SmallIntegerField(default=0)
    medium = models.SmallIntegerField(default=0)
    low = models.SmallIntegerField(default=0)

    other_slots = models.SmallIntegerField(default=0)

    objects = EVEClassManager()

    def process(self, json_data, client):
        ship = client.api.Universe.get_universe_types_type_id(type_id=self.id).result()
        self.name = ship['name']

        ship_type_dict = client.api.Universe.get_universe_groups_group_id(group_id=ship['group_id']).result()
        ship_type, created = ShipType.objects.get_or_create(id=ship_type_dict['group_id'], name=ship_type_dict['name'])

        dogma_attributes = {item['attribute_id']: item for item in ship['dogma_attributes']}

        self.rigs = int(dogma_attributes.get(1137, {}).get('value', 0))
        self.low = int(dogma_attributes.get(12, {}).get('value', 0))
        self.medium = int(dogma_attributes.get(13, {}).get('value', 0))
        self.high = int(dogma_attributes.get(14, {}).get('value', 0))

        self.type = ship_type
