# Generated by Django 3.1 on 2020-08-15 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cardstore', '0003_auto_20200815_2037'),
    ]

    operations = [
        migrations.AddField(
            model_name='blackcard',
            name='pick',
            field=models.IntegerField(default='1'),
            preserve_default=False,
        ),
    ]
