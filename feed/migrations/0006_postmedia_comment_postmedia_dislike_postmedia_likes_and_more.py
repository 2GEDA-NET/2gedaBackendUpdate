# Generated by Django 4.2.5 on 2023-11-16 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0005_postmedia_time_stamp_postmedia_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='postmedia',
            name='comment',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='postmedia',
            name='dislike',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='postmedia',
            name='likes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='postmedia',
            name='love',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='postmedia',
            name='other_reactions',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='postmedia',
            name='shares',
            field=models.IntegerField(default=0),
        ),
    ]