# Generated by Django 4.2.5 on 2023-12-07 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0020_replymedia_reply_media'),
    ]

    operations = [
        migrations.AddField(
            model_name='postmedia',
            name='Reaction',
            field=models.ManyToManyField(to='feed.reaction'),
        ),
    ]
