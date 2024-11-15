# Generated by Django 5.0.4 on 2024-09-18 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0027_payment_receipt_pdf'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='email2',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='id_image',
            field=models.ImageField(blank=True, null=True, upload_to='media/id_images/'),
        ),
    ]
