# Generated by Django 5.0.1 on 2024-01-08 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="date_updated",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="post",
            name="slug",
            field=models.SlugField(max_length=255, unique=True),
        ),
    ]
