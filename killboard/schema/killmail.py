import json

from django.db import models


class Killmail(models.Model):
    # Base Info
    id = models.IntegerField(primary_key=True)
    km_date = models.DateTimeField()

    # Ship Info
    solar_system = models.IntegerField()
    items_dict = models.TextField()
    pos_x = models.FloatField()
    pos_y = models.FloatField()
    pos_z = models.FloatField()
    ship_type = models.IntegerField()
    damage_taken = models.IntegerField()

    # Miscellaneous Info
    moon = models.IntegerField(null=True)
    war = models.IntegerField(null=True)

    # Char Info
    victim = models.IntegerField()
    alliance = models.IntegerField(null=True)
    corporation = models.IntegerField(null=True)
    faction = models.IntegerField(null=True)

    attackers_dict = models.TextField()

    @property
    def attackers(self):
        return json.loads(self.attackers_dict)

    @property
    def items(self):
        return json.loads(self.items_dict)

    def update_mail(self, mail):
        pass

    def create_mail(self, mail):
        self.id = mail['killmail_id']
        self.km_date = mail['killmail_time']
        self.solar_system = mail['solar_system_id']
        self.items_dict = json.dumps(mail['victim']['items'])
        self.pos_x = mail['victim']['position']['x']
        self.pos_y = mail['victim']['position']['y']
        self.pos_z = mail['victim']['position']['z']
        self.ship_type = mail['victim']['ship_type_id']
        self.damage_taken = mail['victim']['damage_taken']
        self.moon = mail['moon_id']
        self.war = mail['war_id']

        self.victim = mail['victim']['character_id']
        self.alliance = mail['victim']['alliance_id']
        self.corporation = mail['victim']['corporation_id']
        self.faction = mail['victim']['faction_id']

        self.attackers_dict = json.dumps(mail['attackers'])
