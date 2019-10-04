# Generated by Django 2.2.5 on 2019-09-29 16:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('killboard', '0004_auto_20190928_2024'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='allianceallies',
            options={'verbose_name': 'Alliance Ally', 'verbose_name_plural': 'Alliance Allies'},
        ),
        migrations.AlterModelOptions(
            name='characterallies',
            options={'verbose_name': 'Character Ally', 'verbose_name_plural': 'Character Allies'},
        ),
        migrations.AlterModelOptions(
            name='corporationallies',
            options={'verbose_name': 'Corporation Ally', 'verbose_name_plural': 'Corporation Allies'},
        ),
        migrations.AddField(
            model_name='attacker',
            name='alliance',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='killboard.Alliance'),
        ),
        migrations.AddField(
            model_name='attacker',
            name='corporation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='killboard.Corporation'),
        ),
    ]
