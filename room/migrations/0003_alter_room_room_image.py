# Generated by Django 5.0.4 on 2024-05-20 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0002_alter_payment_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='room_image',
            field=models.ImageField(blank=True, upload_to='media/room_images/'),
        ),
    ]
