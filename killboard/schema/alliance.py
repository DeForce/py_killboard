from django.db import models


class Alliance(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(max_length=100)

    def process(self, json_data, client):
        alliance = client.api.Alliance.get_alliances_alliance_id(alliance_id=self.id).result()
        self.name = alliance['name']
        self.save()
