# Generated by Django 5.0.4 on 2024-06-29 20:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Hall', '0002_hall_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.RenameField(
            model_name='hall',
            old_name='price_per_hour',
            new_name='price_per_day',
        ),
        migrations.RemoveField(
            model_name='hall',
            name='name',
        ),
        migrations.RemoveField(
            model_name='hall_booking',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='hall_booking',
            name='start_time',
        ),
        migrations.AddField(
            model_name='hall',
            name='hall_number',
            field=models.CharField(default='000', max_length=20),
        ),
        migrations.AddField(
            model_name='hall',
            name='hall_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Hall.category'),
        ),
    ]
