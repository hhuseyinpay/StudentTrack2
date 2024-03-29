# Generated by Django 2.1.8 on 2019-04-30 14:40

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='area',
            name='executives',
            field=models.ManyToManyField(blank=True, related_name='area_executive', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='classroom',
            name='teachers',
            field=models.ManyToManyField(blank=True, related_name='classroom_teacher', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='region',
            name='admins',
            field=models.ManyToManyField(blank=True, related_name='region_admin', to=settings.AUTH_USER_MODEL),
        ),
    ]
