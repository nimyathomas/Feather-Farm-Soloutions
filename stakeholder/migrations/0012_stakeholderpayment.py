# Generated by Django 5.0.8 on 2025-03-02 06:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stakeholder', '0011_chickbatch_actual_fcr_chickbatch_target_fcr'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StakeholderPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('base_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fcr_bonus', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('mortality_penalty', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('payment_method', models.CharField(blank=True, choices=[('bank_transfer', 'Bank Transfer'), ('upi', 'UPI'), ('cash', 'Cash'), ('check', 'Check'), ('razorpay', 'Razorpay')], max_length=20, null=True)),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True)),
                ('notes', models.TextField(blank=True)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='stakeholder.chickbatch')),
                ('processed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='processed_payments', to=settings.AUTH_USER_MODEL)),
                ('stakeholder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-payment_date'],
            },
        ),
    ]
