# Generated by Django 5.0.4 on 2024-05-28 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0009_remove_payment_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
    ]