# Generated by Django 2.1.1 on 2018-10-13 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20181012_2333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='is_student',
            field=models.BooleanField(default=False),
        ),
    ]
