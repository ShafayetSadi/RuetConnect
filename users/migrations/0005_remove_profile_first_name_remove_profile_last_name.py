# Generated by Django 5.0 on 2024-01-04 13:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_profile_first_name_profile_last_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='last_name',
        ),
    ]