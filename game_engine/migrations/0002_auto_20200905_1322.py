# Generated by Django 3.1.1 on 2020-09-05 11:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game_engine', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gamesession',
            name='playerlist',
        ),
        migrations.AddField(
            model_name='sessionplayerlist',
            name='session',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='game_engine.gamesession'),
            preserve_default=False,
        ),
    ]
