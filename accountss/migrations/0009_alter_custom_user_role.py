# Generated by Django 5.0.4 on 2024-05-27 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountss', '0008_alter_custom_user_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custom_user',
            name='role',
            field=models.CharField(choices=[('owner', 'Owner'), ('manager', 'Manager'), ('customer', 'Customer'), ('admin', 'Admin')], default='customer', max_length=20),
        ),
    ]
