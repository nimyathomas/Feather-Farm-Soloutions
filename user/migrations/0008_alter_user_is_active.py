# Generated by Django 5.0.8 on 2024-10-24 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_user_coopcapacity_user_plan_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
