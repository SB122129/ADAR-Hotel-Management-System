# Generated by Django 5.0.4 on 2024-09-21 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0013_socialmediapost_posted_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='role',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
