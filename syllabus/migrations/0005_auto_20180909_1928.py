# Generated by Django 2.1.1 on 2018-09-09 16:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('syllabus', '0004_auto_20180907_2116'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='content',
            options={'ordering': ('syllabus', 'week', 'name')},
        ),
    ]
