# Generated by Django 5.0.4 on 2024-07-21 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0010_remove_membership_full_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='start_date',
            field=models.DateField(),
        ),
    ]