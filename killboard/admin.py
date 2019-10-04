from django.contrib import admin

# Register your models here.
from killboard.schema.admin.allies import AllianceAllies, CorporationAllies, CharacterAllies


@admin.register(AllianceAllies, CorporationAllies, CharacterAllies)
class AlliesAdmin(admin.ModelAdmin):
    pass
