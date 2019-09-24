from django.db import models


class SolarSystem(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    security_status = models.FloatField(null=True)
    security_class = models.CharField(max_length=5, null=True)

    def process(self, json_data, client):
        ss = client.api.Universe.get_universe_systems_system_id(system_id=self.id).result()
        self.name = ss['name']
        self.security_status = ss['security_status']
        self.security_class = ss['security_class']
        self.save()
