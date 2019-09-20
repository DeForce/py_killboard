from __future__ import unicode_literals

from django.db import migrations

SCOPES = {
    'esi-planets.manage_planets.v1':
        "Allows reading a list of a character's planetary colonies, and the details of those colonies.",
    'esi-ui.open_window.v1': "Allows open window in game client remotely.",
    'esi-assets.read_assets.v1': "Allows reading a list of assets that the character owns.",
    'esi-calendar.read_calendar_events.v1': "Allows reading a character's calendar, including corporate events.",
    'esi-bookmarks.read_character_bookmarks.v1': "Allows reading of a character's bookmarks and bookmark folders.",
    'esi-wallet.read_character_wallet.v1': "Allows reading of a character's wallet, journal and transaction history.",
    'esi-clones.read_clones.v1': "Allows reading the locations of a character's jump clones and their implants.",
    'esi-characters.read_contacts.v1':
        "Allows reading of a character's contacts list, and calculation of CSPA charges.",
    'esi-corporations.read_corporation_membership.v1':
        "Allows reading a list of the ID's and roles of a character's fellow corporation members.",
    'esi-fleets.read_fleet.v1': "Allows reading information about fleets.",
    'esi-killmails.read_killmails.v1': "Allows reading of a character's kills and losses.",
    'esi-location.read_location.v1': "Allows reading of a character's active ship location.",
    'esi-location.read_ship_type.v1': "Allows reading of a character's active ship class.",
    'esi-skills.read_skillqueue.v1': "Allows reading of a character's currently training skill queue.",
    'esi-skills.read_skills.v1': "Allows reading of a character's currently known skills.",
    'esi-universe.read_structures.v1':
        "Allows querying the location and type of structures that the character has docking access at.",
    'esi-calendar.respond_calendar_events.v1': "Allows updating of a character's calendar event responses.",
    'esi-search.search_structures.v1':
        "Allows searching over all structures that a character can see in the structure browser.",
    'esi-fleets.write_fleet.v1': "Allows manipulating fleets.",
    'esi-ui.write_waypoint.v1': "Allows manipulating waypoints in game client remotely."
}


def generate_scopes(apps, schema_editor):
    scope = apps.get_model('killboard', 'Scope')
    for s in SCOPES:
        scope.objects.update_or_create(name=s, defaults={'help_text': SCOPES[s]})


def delete_scopes(apps, schema_editor):
    scope = apps.get_model('killboard', 'Scope')
    for s in SCOPES:
        try:
            scope.objects.get(name=s).delete()
        except scope.DoesNotExist:
            pass


class Migration(migrations.Migration):
    dependencies = [
        ('killboard', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(generate_scopes, delete_scopes)
    ]