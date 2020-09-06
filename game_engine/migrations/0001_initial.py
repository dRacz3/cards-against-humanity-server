# Generated by Django 3.1.1 on 2020-09-05 11:19

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cardstore', '0008_auto_20200904_1649'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GameRound',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roundNumber', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('active_black_card', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cardstore.blackcard')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.CharField(blank=True, max_length=240)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SessionPlayerList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profiles', models.ManyToManyField(to='game_engine.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='GameSession',
            fields=[
                ('session_id', models.CharField(max_length=120, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('has_started', models.BooleanField(default=False)),
                ('playerlist', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='game_engine.sessionplayerlist')),
            ],
        ),
        migrations.CreateModel(
            name='GameRoundProfileData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_points', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('cards', models.ManyToManyField(to='cardstore.WhiteCard')),
                ('round', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='GameRoundProfileData', to='game_engine.gameround')),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game_engine.profile')),
            ],
        ),
        migrations.AddField(
            model_name='gameround',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Round', to='game_engine.gamesession'),
        ),
        migrations.AddField(
            model_name='gameround',
            name='tzar',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='game_engine.profile'),
        ),
    ]
