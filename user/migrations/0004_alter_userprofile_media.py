# Generated by Django 4.2.5 on 2023-11-11 15:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_userprofileimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='media',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_media', to='user.userprofileimage'),
        ),
    ]