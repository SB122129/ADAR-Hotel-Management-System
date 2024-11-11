# Generated by Django 5.0.4 on 2024-06-09 13:13

import django_countries.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accountss', '0010_custom_user_telegram_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='custom_user',
            name='city',
        ),
        migrations.AlterField(
            model_name='custom_user',
            name='country',
            field=django_countries.fields.CountryField(max_length=2),
        ),
    ]