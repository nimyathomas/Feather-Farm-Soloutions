# Generated by Django 5.1.1 on 2024-10-25 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_alter_user_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='location',
            field=models.CharField(default='america', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='name',
            field=models.CharField(default='toritila farm', max_length=100),
            preserve_default=False,
        ),
    ]