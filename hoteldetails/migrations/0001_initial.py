# Generated by Django 5.0.8 on 2024-11-02 15:37

import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stakeholder', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('one_kg_count', models.IntegerField(default=0, help_text='Number of 1 kg chickens ordered')),
                ('two_kg_count', models.IntegerField(default=0, help_text='Number of 2 kg chickens ordered')),
                ('three_kg_count', models.IntegerField(default=0, help_text='Number of 3 kg chickens ordered')),
                ('is_processed', models.BooleanField(default=False, help_text='True if fully dressed, False if live')),
                ('item_type', models.CharField(choices=[('live', 'Live'), ('processed', 'Processed')], default='live', help_text='Specify if the item is live or processed', max_length=10)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='hoteldetails.cart')),
                ('chick_batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stakeholder.chickbatch')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('one_kg_count', models.IntegerField(default=0, help_text='Number of 1 kg chickens ordered')),
                ('two_kg_count', models.IntegerField(default=0, help_text='Number of 2 kg chickens ordered')),
                ('three_kg_count', models.IntegerField(default=0, help_text='Number of 3 kg chickens ordered')),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('delivery_date', models.DateField(blank=True, help_text='Expected delivery date', null=True)),
                ('price', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Total order price', max_digits=10)),
                ('payment_method', models.CharField(choices=[('cod', 'Cash On Delivery'), ('online', 'Online Transfer'), ('upi', 'UPI')], default='cod', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending', max_length=20)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stakeholder.chickbatch')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
