# Generated by Django 5.0.4 on 2024-05-18 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountss', '0002_alter_custom_user_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custom_user',
            name='profile_picture',
            field=models.ImageField(blank=True, default='static/default_profile_picture.png', null=True, upload_to='accountss/media'),
        ),
    ]