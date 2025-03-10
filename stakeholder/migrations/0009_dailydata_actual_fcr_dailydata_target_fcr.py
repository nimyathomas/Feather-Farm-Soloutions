# Generated by Django 5.0.8 on 2025-03-01 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stakeholder', '0008_remove_feednotification_week_number1'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailydata',
            name='actual_fcr',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name='dailydata',
            name='target_fcr',
            field=models.DecimalField(decimal_places=2, default=1.5, max_digits=4),
        ),
    ]
