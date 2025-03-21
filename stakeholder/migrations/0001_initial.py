# Generated by Django 5.0.8 on 2025-02-28 07:27

import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChickBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initial_chick_count', models.IntegerField(help_text='Initial number of chicks in the batch')),
                ('batch_date', models.DateField(default=django.utils.timezone.now, help_text='Date the batch started')),
                ('duration', models.IntegerField(default=40, help_text='Duration of the batch in days')),
                ('batch_status', models.CharField(choices=[('active', 'Active'), ('completed', 'Completed')], default='active', help_text='Current status of the batch', max_length=10)),
                ('batch_type', models.CharField(choices=[('broiler', 'Broiler'), ('organic', 'Organic'), ('kada', 'Kada')], default='broiler', help_text='Type of chickens in the batch', max_length=10)),
                ('available_chickens', models.IntegerField(default=0, help_text='Count of live chickens available')),
                ('batch_size', models.FloatField(default=50.0, help_text='Standard weight of a batch (in kg)')),
                ('price_per_kg', models.DecimalField(decimal_places=2, help_text='Price per kg of chicken', max_digits=10, null=True)),
                ('price_per_batch', models.DecimalField(decimal_places=2, help_text='Price per batch of chicken', max_digits=10, null=True)),
                ('one_kg_count', models.IntegerField(default=0, help_text='Number of 1 kg chickens available')),
                ('two_kg_count', models.IntegerField(default=0, help_text='Number of 2 kg chickens available')),
                ('three_kg_count', models.IntegerField(default=0, help_text='Number of 3 kg chickens available')),
                ('food_token', models.IntegerField(default=0, help_text='Reward token for good FCR performance')),
                ('reward_claimed', models.BooleanField(default=False)),
                ('reward_claimed_date', models.DateTimeField(blank=True, null=True)),
                ('completion_date', models.DateTimeField(blank=True, null=True)),
                ('reward_amount', models.DecimalField(decimal_places=2, default=0, help_text='Reward amount based on FCR performance', max_digits=10)),
                ('reward_status', models.BooleanField(default=False)),
                ('batch_uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('qr_code', models.ImageField(blank=True, upload_to='batch_qr_codes/')),
                ('total_feed_sacks', models.IntegerField(default=0)),
                ('assigned_feed_sacks', models.IntegerField(default=0)),
                ('remaining_feed_sacks', models.IntegerField(default=0)),
                ('starter_feed_consumed', models.IntegerField(default=0)),
                ('grower_feed_consumed', models.IntegerField(default=0)),
                ('finisher_feed_consumed', models.IntegerField(default=0)),
                ('starter_feed_sacks', models.IntegerField(default=0, help_text='Number of starter feed sacks assigned')),
                ('grower_feed_sacks', models.IntegerField(default=0)),
                ('finisher_feed_sacks', models.IntegerField(default=0)),
                ('current_feed_type', models.CharField(choices=[('Starter Feed', 'Starter Feed'), ('Grower Feed', 'Grower Feed'), ('Finisher Feed', 'Finisher Feed')], default='Starter Feed', max_length=50)),
                ('last_feed_transition', models.DateTimeField(blank=True, null=True)),
                ('feed_transition_notified', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ChickSupply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('chicks_supplied', models.IntegerField(help_text='Number of chicks supplied on this day')),
                ('chicken_type', models.CharField(choices=[('broiler', 'Broiler'), ('organic', 'Organic'), ('kada', 'Kada')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
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
            ],
        ),
        migrations.CreateModel(
            name='DailyFeedConsumption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('day_number', models.IntegerField()),
                ('morning_consumption', models.DecimalField(decimal_places=2, default=0, max_digits=4)),
                ('evening_consumption', models.DecimalField(decimal_places=2, default=0, max_digits=4)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='DiseaseAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(help_text='Upload image of the chicken for analysis', upload_to='disease_analysis/')),
                ('analyzed_date', models.DateTimeField(auto_now_add=True)),
                ('predicted_disease', models.CharField(choices=[('healthy', 'Healthy'), ('coccidiosis', 'Coccidiosis'), ('salmonella', 'Salmonella'), ('aspergillosis', 'Aspergillosis'), ('colibacillosis', 'Colibacillosis'), ('marek', "Marek's Disease"), ('newcastle', 'Newcastle Disease'), ('infectious_bronchitis', 'Infectious Bronchitis')], help_text='Predicted disease based on image analysis', max_length=50)),
                ('confidence_score', models.FloatField(help_text='Confidence score of the prediction (0-1)')),
                ('confidence_level', models.CharField(choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low'), ('Error', 'Error')], max_length=20)),
                ('needs_review', models.BooleanField(default=False)),
                ('symptoms_detected', models.JSONField(default=list, help_text='List of symptoms detected in the analysis')),
                ('warning_message', models.TextField(blank=True, null=True)),
                ('temperature', models.FloatField(blank=True, help_text='Body temperature if measured', null=True)),
                ('behavior_notes', models.TextField(blank=True, help_text='Notes about chicken behavior')),
                ('recommendations', models.JSONField(default=dict, help_text='Treatment recommendations and precautions')),
                ('veterinary_referral', models.BooleanField(default=False, help_text='Whether veterinary consultation is recommended')),
                ('is_critical', models.BooleanField(default=False, help_text='Indicates if immediate attention is required')),
                ('follow_up_date', models.DateField(blank=True, help_text='Recommended date for follow-up analysis', null=True)),
            ],
            options={
                'verbose_name': 'Disease Analysis',
                'verbose_name_plural': 'Disease Analyses',
                'db_table': 'stakeholder_diseaseanalysis',
                'ordering': ['-analyzed_date'],
            },
        ),
        migrations.CreateModel(
            name='Farm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('farm_image', models.ImageField(blank=True, max_length=255, null=True, upload_to='images/')),
                ('length', models.FloatField(blank=True, default=None, null=True)),
                ('breadth', models.FloatField(blank=True, default=None, null=True)),
                ('size', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('established_date', models.DateField(blank=True, null=True)),
                ('coopcapacity', models.IntegerField(default=0)),
                ('is_recommended', models.BooleanField(default=False)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('plan_file', models.FileField(blank=True, null=True, upload_to='farm_plan/')),
                ('expiry_date', models.DateField(blank=True, default=None, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('pollution_certificate', models.FileField(blank=True, null=True, upload_to='certificates/')),
                ('certification_type', models.CharField(blank=True, choices=[('ORGANIC', 'Organic Certified'), ('STANDARD', 'Standard'), ('PREMIUM', 'Premium Quality')], max_length=20, null=True)),
                ('certification_file', models.FileField(blank=True, null=True, upload_to='certifications/')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='FeedAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week_number', models.IntegerField()),
                ('feed_type', models.CharField(choices=[('Starter Feed', 'Starter Feed'), ('Grower Feed', 'Grower Feed'), ('Finisher Feed', 'Finisher Feed')], max_length=50)),
                ('sacks_assigned', models.DecimalField(decimal_places=2, max_digits=10)),
                ('sacks_consumed', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cost_per_sack', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_late', models.BooleanField(default=False)),
                ('assigned_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('acknowledged', 'Acknowledged'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('acknowledgment_date', models.DateTimeField(blank=True, null=True)),
                ('acknowledgment_notes', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'feed_assignment',
            },
        ),
        migrations.CreateModel(
            name='FeedCalculator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_of_chicks', models.IntegerField()),
                ('calculated_feed_kg', models.FloatField()),
                ('calculated_sacks', models.FloatField()),
                ('safety_margin_sacks', models.FloatField()),
                ('starter_feed_sacks', models.FloatField()),
                ('grower_feed_sacks', models.FloatField()),
                ('finisher_feed_sacks', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='FeedMonitoring',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('feed_consumed', models.FloatField(default=0.0)),
                ('feed_forecast', models.FloatField(default=0.0)),
                ('feed_wastage', models.FloatField(default=0.0)),
            ],
            options={
                'verbose_name': 'Feed Monitoring',
                'verbose_name_plural': 'Feed Monitoring',
            },
        ),
        migrations.CreateModel(
            name='GrowthPrediction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('day_number', models.IntegerField()),
                ('feed_consumed', models.FloatField()),
                ('water_consumed', models.FloatField()),
                ('temperature', models.FloatField()),
                ('alive_count', models.IntegerField()),
                ('predicted_weight', models.FloatField()),
                ('actual_weight', models.FloatField(blank=True, null=True)),
                ('weight_difference', models.FloatField(blank=True, null=True)),
                ('growth_status', models.CharField(choices=[('On Track', 'On Track'), ('Under-Growing', 'Under-Growing'), ('Over-Growing', 'Over-Growing'), ('Pending', 'Pending Verification')], default='Pending', max_length=20)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('category', models.CharField(choices=[('fcr', 'FCR Discussion'), ('health', 'Health & Safety'), ('best_practices', 'Best Practices'), ('general', 'General Discussion')], default='general', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SuccessStory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('category', models.CharField(choices=[('FCR', 'Improved FCR'), ('Scaling Up', 'Successfully Scaling Up'), ('Collaboration', 'Collaboration with Hoteliers')], max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='VaccinationAuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=100)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='VaccinationSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vaccination_date', models.DateField()),
                ('status', models.CharField(choices=[('assigned', 'Assigned'), ('qr_scanned', 'QR Scanned'), ('evidence_uploaded', 'Evidence Uploaded'), ('administered', 'Administered'), ('verified', 'Verified'), ('rejected', 'Rejected')], default='assigned', max_length=20)),
                ('qr_code', models.ImageField(blank=True, upload_to='vaccination_qr_codes/')),
                ('verification_code', models.CharField(blank=True, max_length=20, unique=True)),
                ('farm_coordinates', models.CharField(blank=True, max_length=100, null=True)),
                ('scan_coordinates', models.CharField(blank=True, max_length=100, null=True)),
                ('vaccine_vial_photo', models.ImageField(blank=True, null=True, upload_to='vaccination_evidence/vials/')),
                ('flock_photo', models.ImageField(blank=True, null=True, upload_to='vaccination_evidence/flocks/')),
                ('administration_photo', models.ImageField(blank=True, null=True, upload_to='vaccination_evidence/admin/')),
                ('temperature', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('humidity', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True)),
                ('rejection_reason', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['-vaccination_date'],
            },
        ),
    ]
