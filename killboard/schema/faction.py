from django.db import models

from killboard.managers import EVEClassManager


class Faction(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    objects = EVEClassManager()

    def process(self, client):
        pass
