# Generated by Django 5.0.8 on 2025-03-01 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stakeholder', '0004_feednotification'),
    ]

    operations = [
        migrations.AddField(
            model_name='feednotification',
            name='week_number',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
