# Generated by Django 4.2.5 on 2023-12-09 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_user_bio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='media',
        ),
        migrations.AddField(
            model_name='user',
            name='media',
            field=models.ManyToManyField(related_name='user_profile_media', to='user.userprofileimage'),
        ),
    ]