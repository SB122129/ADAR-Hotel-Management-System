# Generated by Django 5.0.4 on 2024-09-10 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0012_alter_socialmediapost_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialmediapost',
            name='posted_by',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
