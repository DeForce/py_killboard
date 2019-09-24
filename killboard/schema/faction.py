from django.db import models


class Faction(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    def process(self, client):
        pass
