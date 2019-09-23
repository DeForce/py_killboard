from django.db import models


class Ship(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(max_length=100)
    type = models.TextField(max_length=100)

    def process(self, json_data, client):
        ship = client.api.Universe.get_universe_types_type_id(type_id=self.id).result()
        self.name = ship['name']
        self.save()
