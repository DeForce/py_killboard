from django.db import models

from killboard.managers import EVEClassManager


class Comment(models.Model):
    id = models.IntegerField(primary_key=True)

    objects = EVEClassManager()
