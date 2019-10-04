from django.db import models
from django.db.models import DO_NOTHING

from killboard.managers import EVEClassManager


class Region(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    objects = EVEClassManager()


class Constellations(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=DO_NOTHING, null=True)

    objects = EVEClassManager()


class SolarSystem(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    security_status = models.FloatField(null=True)
    security_class = models.CharField(max_length=5, null=True)

    constellation = models.ForeignKey(Constellations, on_delete=DO_NOTHING, null=True)
    region = models.ForeignKey(Region, on_delete=DO_NOTHING, null=True)

    objects = EVEClassManager()

    def process(self, json_data, client):
        ss = client.api.Universe.get_universe_systems_system_id(system_id=self.id).result()
        constellation_api = client.api.Universe.get_universe_constellations_constellation_id(
            constellation_id=ss['constellation_id']).result()
        region_api = client.api.Universe.get_universe_regions_region_id(region_id=constellation_api['region_id']).result()

        region, _ = Region.objects.get_or_create(id=region_api['region_id'], name=region_api['name'])
        constellation, _ = Constellations.objects.get_or_create(
            id=constellation_api['constellation_id'], name=constellation_api['name'], region=region)

        self.constellation = constellation
        self.region = region

        self.name = ss['name']
        self.security_status = ss['security_status']
        self.security_class = ss['security_class']
