# Generated by Django 5.0.8 on 2025-03-01 03:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stakeholder', '0005_feednotification_week_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feednotification',
            name='week_number',
        ),
    ]
