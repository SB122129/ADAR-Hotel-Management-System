# Generated by Django 5.0.4 on 2024-05-18 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountss', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custom_user',
            name='profile_picture',
            field=models.ImageField(default='default_profile_picture.png', upload_to='accountss/media'),
        ),
    ]