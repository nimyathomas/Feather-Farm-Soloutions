# Generated by Django 5.1.5 on 2025-01-18 13:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="breadth",
        ),
        migrations.RemoveField(
            model_name="user",
            name="coopcapacity",
        ),
        migrations.RemoveField(
            model_name="user",
            name="distance_from_hotel",
        ),
        migrations.RemoveField(
            model_name="user",
            name="farm_image",
        ),
        migrations.RemoveField(
            model_name="user",
            name="is_recommended",
        ),
        migrations.RemoveField(
            model_name="user",
            name="latitude",
        ),
        migrations.RemoveField(
            model_name="user",
            name="length",
        ),
        migrations.RemoveField(
            model_name="user",
            name="longitude",
        ),
        migrations.RemoveField(
            model_name="user",
            name="plan_file",
        ),
    ]
