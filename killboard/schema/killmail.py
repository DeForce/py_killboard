import json

from django.db import models

from killboard.esi_api.client_helper import APIHelper
from killboard.schema.alliance import Alliance
from killboard.schema.character import Character
from killboard.schema.corporation import Corporation
from killboard.schema.faction import Faction
from killboard.schema.ship import Ship
from killboard.schema.solar_system import SolarSystem


class Killmail(models.Model):
    # Base Info
    id = models.IntegerField(primary_key=True)
    km_date = models.DateTimeField()

    # Ship Info
    solar_system = models.ForeignKey(SolarSystem, related_name='solar_system', on_delete=models.DO_NOTHING)
    items_dict = models.TextField()
    pos_x = models.FloatField()
    pos_y = models.FloatField()
    pos_z = models.FloatField()
    ship_type = models.ForeignKey(Ship, related_name='ship', on_delete=models.DO_NOTHING)
    damage_taken = models.IntegerField()

    # Miscellaneous Info
    moon = models.IntegerField(null=True)
    war = models.IntegerField(null=True)

    # Char Info
    victim = models.ForeignKey(Character, related_name='victim', on_delete=models.DO_NOTHING)
    alliance = models.ForeignKey(Alliance, related_name='alliance', on_delete=models.DO_NOTHING, null=True)
    corporation = models.ForeignKey(Corporation, related_name='corporation', on_delete=models.DO_NOTHING)
    faction = models.ForeignKey(Faction, related_name='faction', on_delete=models.DO_NOTHING, null=True)

    attackers_dict = models.TextField()
    attackers = models.ManyToManyField(Character, related_name='attackers')

    api_helper = None

    @property
    def attackers_info(self):
        return json.loads(self.attackers_dict)

    @property
    def items(self):
        return json.loads(self.items_dict)

    def update_mail(self, mail, client):
        self.create_mail(mail, client)

    def create_mail(self, mail, client):
        self.api = APIHelper(client)

        self.id = mail['killmail_id']
        self.km_date = mail['killmail_time']
        self.items_dict = json.dumps(mail['victim']['items'])
        self.pos_x = mail['victim']['position']['x']
        self.pos_y = mail['victim']['position']['y']
        self.pos_z = mail['victim']['position']['z']
        self.damage_taken = mail['victim']['damage_taken']
        self.moon = mail['moon_id']
        self.war = mail['war_id']
        self.attackers_dict = json.dumps(mail['attackers'])

        self.solar_system = self.api.process_solar_system(mail)
        self.ship_type = self.api.process_ship(mail['victim'])

        victim = self.api.process_character(mail['victim'])
        self.victim = victim

        corp = self.api.process_corporation(mail['victim'])
        if corp:
            self.corporation = corp

        alliance = self.api.process_alliance(mail['victim'])
        if alliance:
            self.alliance = alliance

        # self.faction = mail['victim']['faction_id']

        self.save()
        for attacker in mail['attackers']:
            attacker_obj = self.api.process_character(attacker)
            if attacker_obj:
                self.attackers.add(attacker_obj)
        self.save()
