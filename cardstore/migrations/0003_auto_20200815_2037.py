# Generated by Django 3.1 on 2020-08-15 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cardstore', '0002_auto_20200815_1927'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blackcard',
            old_name='package',
            new_name='deck',
        ),
        migrations.RenameField(
            model_name='blackcard',
            old_name='card_text',
            new_name='text',
        ),
        migrations.RenameField(
            model_name='whitecard',
            old_name='package',
            new_name='deck',
        ),
        migrations.RenameField(
            model_name='whitecard',
            old_name='card_text',
            new_name='text',
        ),
        migrations.AddField(
            model_name='blackcard',
            name='icon',
            field=models.CharField(default=' ', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='whitecard',
            name='icon',
            field=models.CharField(default=' ', max_length=200),
            preserve_default=False,
        ),
    ]
