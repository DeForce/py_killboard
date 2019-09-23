from django.db import models


class SolarSystem(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(max_length=100)

    def process(self, json_data, client):
        ss = client.api.Universe.get_universe_systems_system_id(system_id=self.id).result()
        self.name = ss['name']
        self.save()
