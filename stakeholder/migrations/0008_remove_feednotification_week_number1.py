# Generated by Django 5.0.8 on 2025-03-01 04:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stakeholder', '0007_feednotification_week_number1'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feednotification',
            name='week_number1',
        ),
    ]
