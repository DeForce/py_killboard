from django.db import models

from killboard.schema.alliance import Alliance
from killboard.schema.corporation import Corporation


class Character(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(max_length=100)

    alliance = models.ForeignKey(Alliance, related_name='char_alliance', on_delete=models.DO_NOTHING, null=True)
    corporation = models.ForeignKey(
        Corporation, related_name='char_corporation', on_delete=models.DO_NOTHING, null=True)

    api = None

    def process(self, json_data, client):
        self.api = client
        char = client.api.Character.get_characters_character_id(character_id=self.id).result()
        self.name = char['name']
        self.save()

        corp = self.api.process_corporation(json_data)
        if corp:
            self.corporation = corp

        alliance = self.api.process_alliance(json_data)
        if alliance:
            self.alliance = alliance
