# Generated by Django 2.2.5 on 2019-09-28 17:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('killboard', '0003_killmail'),
    ]

    operations = [
        migrations.CreateModel(
            name='AllianceAllies',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Attacker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('damage_done', models.FloatField()),
                ('final_blow', models.BooleanField()),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='killboard.Character')),
            ],
        ),
        migrations.CreateModel(
            name='CharacterAllies',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='CorporationAllies',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='killmail',
            name='attackers_dict',
        ),
        migrations.AddField(
            model_name='ship',
            name='high',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ship',
            name='low',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ship',
            name='medium',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ship',
            name='other_slots',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ship',
            name='rigs',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='killmail',
            name='attackers',
            field=models.ManyToManyField(related_name='attackers', to='killboard.Attacker'),
        ),
        migrations.CreateModel(
            name='Constellations',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('region', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='killboard.Region')),
            ],
        ),
        migrations.AddField(
            model_name='attacker',
            name='ship',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='killboard.Ship'),
        ),
        migrations.AddField(
            model_name='attacker',
            name='weapon',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='killboard.ItemType'),
        ),
        migrations.AddField(
            model_name='solarsystem',
            name='constellation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='killboard.Constellations'),
        ),
        migrations.AddField(
            model_name='solarsystem',
            name='region',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='killboard.Region'),
        ),
    ]