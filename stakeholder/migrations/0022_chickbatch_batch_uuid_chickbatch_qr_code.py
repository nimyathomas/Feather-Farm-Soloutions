# Generated by Django 5.0.8 on 2025-02-10 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stakeholder', '0021_diseaseanalysis'),
    ]

    operations = [
        migrations.AddField(
            model_name='chickbatch',
            name='batch_uuid',
            field=models.UUIDField(editable=False, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='chickbatch',
            name='qr_code',
            field=models.ImageField(blank=True, upload_to='batch_qr_codes/'),
        ),
    ]
