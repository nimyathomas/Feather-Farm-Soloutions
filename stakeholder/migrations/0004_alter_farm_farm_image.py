# Generated by Django 5.1.5 on 2025-01-18 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stakeholder", "0003_farm"),
    ]

    operations = [
        migrations.AlterField(
            model_name="farm",
            name="farm_image",
            field=models.ImageField(
                blank=True, max_length=255, null=True, upload_to="images/"
            ),
        ),
    ]
