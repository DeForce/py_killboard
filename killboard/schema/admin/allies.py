import requests
from django.core.exceptions import ValidationError
from django.db import models

from killboard.app_settings import ESI_API_URL


class Ally(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    key = None

    def full_clean(self, exclude=None, validate_unique=True):
        data = requests.get(f'{ESI_API_URL}latest/search/',
                            params={'categories': self.key, 'search': self.name}).json()
        alliance = data.get('alliance', [])
        if alliance:
            self.id = alliance[0]

            alliance = requests.get(f'{ESI_API_URL}latest/{self.key}s/{alliance[0]}/').json()
            self.name = alliance['name']
        elif len(alliance) > 1:
            alliance_names = [item['name']
                              for item in requests.get(f'{ESI_API_URL}latest/{self.key}s/{alliance[0]}/').json()]
            raise ValidationError(f'More that one {self.key} found, pick one: {alliance_names}')
        else:
            raise ValidationError(f'No {self.key} found, please check the name')

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.id} ({self.name})'


class AllianceAllies(Ally):
    key = 'alliance'

    class Meta:
        verbose_name = 'Alliance Ally'
        verbose_name_plural = 'Alliance Allies'


class CorporationAllies(Ally):
    key = 'corporation'

    class Meta:
        verbose_name = 'Corporation Ally'
        verbose_name_plural = 'Corporation Allies'


class CharacterAllies(Ally):
    key = 'character'

    class Meta:
        verbose_name = 'Character Ally'
        verbose_name_plural = 'Character Allies'
