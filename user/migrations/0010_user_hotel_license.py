# Generated by Django 5.1.1 on 2024-10-28 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_user_location_user_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='hotel_license',
            field=models.FileField(blank=True, null=True, upload_to='hotel_license/'),
        ),
    ]
