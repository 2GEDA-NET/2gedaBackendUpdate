# Generated by Django 4.2.5 on 2023-11-29 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0004_alter_demovideo_video_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='Geopraphical_Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50, verbose_name='')),
                ('platform', models.CharField(max_length=50, verbose_name='')),
                ('websiteurl', models.CharField(max_length=50, verbose_name='')),
                ('location', models.CharField(max_length=50, verbose_name='')),
                ('address', models.CharField(max_length=50, verbose_name='')),
                ('ticket_name', models.CharField(max_length=50, verbose_name='')),
                ('category', models.CharField(max_length=50, verbose_name='')),
                ('fee_settings_category', models.CharField(max_length=50, verbose_name='')),
                ('quantity', models.CharField(max_length=50, verbose_name='')),
                ('price', models.CharField(max_length=50, verbose_name='')),
                ('IsPrivate', models.CharField(max_length=50, verbose_name='')),
                ('IsPublic', models.CharField(max_length=50, verbose_name='')),
                ('show_remaining_ticket', models.CharField(max_length=50, verbose_name='')),
            ],
        ),
    ]