from django.db import models


class AllianceAllies(models.Model):
    id = models.IntegerField(primary_key=True)

    class Meta:
        verbose_name = 'Alliance Ally'
        verbose_name_plural = 'Alliance Allies'


class CorporationAllies(models.Model):
    id = models.IntegerField(primary_key=True)

    class Meta:
        verbose_name = 'Corporation Ally'
        verbose_name_plural = 'Corporation Allies'


class CharacterAllies(models.Model):
    id = models.IntegerField(primary_key=True)

    class Meta:
        verbose_name = 'Character Ally'
        verbose_name_plural = 'Character Allies'
