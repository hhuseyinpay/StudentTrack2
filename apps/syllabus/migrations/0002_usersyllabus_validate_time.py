# Generated by Django 2.1.3 on 2018-12-03 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syllabus', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersyllabus',
            name='validate_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]