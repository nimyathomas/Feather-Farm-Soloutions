# Generated by Django 5.0.8 on 2024-11-10 02:31

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stakeholder', '0002_alter_chickbatch_batch_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChickSupply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('chicks_supplied', models.IntegerField(help_text='Number of chicks supplied on this day')),
                ('chicken_type', models.CharField(choices=[('broiler', 'Broiler'), ('organic', 'Organic'), ('kada', 'Kada')], max_length=20)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chick_supplies', to='stakeholder.chickbatch')),
                ('stakeholder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chick_supplies', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]