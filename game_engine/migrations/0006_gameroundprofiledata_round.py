# Generated by Django 3.1.1 on 2020-09-04 15:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game_engine', '0005_remove_profile_room'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameroundprofiledata',
            name='round',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='game_engine.gameroom'),
        ),
    ]
