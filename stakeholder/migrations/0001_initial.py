# Generated by Django 5.0.8 on 2024-11-02 15:37

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChickBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initial_chick_count', models.IntegerField(help_text='Initial number of chicks in the batch')),
                ('batch_date', models.DateField(default=django.utils.timezone.now, help_text='Date the batch started')),
                ('duration', models.IntegerField(default=40, help_text='Duration of the batch in days')),
                ('batch_status', models.CharField(choices=[('active', 'Active'), ('completed', 'Completed'), ('uplifted', 'Uplifted'), ('terminated', 'Terminated')], default='active', help_text='Current status of the batch', max_length=10)),
                ('batch_type', models.CharField(choices=[('broiler', 'Broiler'), ('organic', 'Organic'), ('kada', 'Kada')], default='broiler', help_text='Type of chickens in the batch', max_length=10)),
                ('available_chickens', models.IntegerField(default=0, help_text='Count of live chickens available')),
                ('batch_size', models.FloatField(default=50.0, help_text='Standard weight of a batch (in kg)')),
                ('price_per_kg', models.DecimalField(decimal_places=2, help_text='Price per kg of chicken', max_digits=10, null=True)),
                ('price_per_batch', models.DecimalField(decimal_places=2, help_text='Price per batch of chicken', max_digits=10, null=True)),
                ('one_kg_count', models.IntegerField(default=0, help_text='Number of 1 kg chickens available')),
                ('two_kg_count', models.IntegerField(default=0, help_text='Number of 2 kg chickens available')),
                ('three_kg_count', models.IntegerField(default=0, help_text='Number of 3 kg chickens available')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chick_batches', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DailyData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('alive_count', models.IntegerField(help_text='Number of chicks alive on this day')),
                ('sick_chicks', models.IntegerField(default=0, help_text='Number of sick chicks')),
                ('weight_gain', models.FloatField(help_text='Weight gain per chick (in grams)')),
                ('feed_uplifted', models.FloatField(help_text='Feed consumed (in kg)')),
                ('water_consumption', models.FloatField(help_text='Water consumed (in liters)')),
                ('temperature', models.FloatField(help_text='Housing temperature')),
                ('mortality_count', models.IntegerField(default=0, help_text='Number of chicks that died')),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_data', to='stakeholder.chickbatch')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_data_records', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('batch', 'date')},
            },
        ),
        migrations.CreateModel(
            name='FeedMonitoring',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('feed_consumed', models.FloatField(default=0.0)),
                ('feed_forecast', models.FloatField(default=0.0)),
                ('feed_wastage', models.FloatField(default=0.0)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stakeholder.chickbatch')),
            ],
            options={
                'verbose_name': 'Feed Monitoring',
                'verbose_name_plural': 'Feed Monitoring',
                'unique_together': {('batch', 'date')},
            },
        ),
    ]
