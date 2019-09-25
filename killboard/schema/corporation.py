from django.db import models

from killboard.managers import EVEClassManager
from killboard.schema.alliance import Alliance


class Corporation(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    alliance = models.ForeignKey(Alliance, on_delete=models.DO_NOTHING, null=True)

    objects = EVEClassManager()

    def process(self, json_data, client):
        corp = client.api.Corporation.get_corporations_corporation_id(corporation_id=self.id).result()
        self.name = corp['name']
        self.save()
