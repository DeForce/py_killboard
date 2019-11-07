from django.contrib import admin

from killboard.schema.admin.allies import AllianceAllies, CorporationAllies, CharacterAllies


@admin.register(AllianceAllies, CorporationAllies, CharacterAllies)
class AlliesAdmin(admin.ModelAdmin):
    fields = ['name']
