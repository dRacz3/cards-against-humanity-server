# Generated by Django 3.1.1 on 2020-09-04 15:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cardstore', '0008_auto_20200904_1649'),
        ('game_engine', '0003_auto_20200904_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameround',
            name='active_black_card',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='cardstore.blackcard'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gameround',
            name='tzar',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.DO_NOTHING, to='game_engine.profile'),
            preserve_default=False,
        ),
    ]