# Generated by Django 2.1.1 on 2018-10-20 23:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('daily_study', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='study',
            old_name='studies',
            new_name='daily_study',
        ),
    ]
