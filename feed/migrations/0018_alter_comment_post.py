# Generated by Django 4.2.5 on 2023-12-04 12:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0017_commentmedia_user_reaction_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_media_fields', to='feed.postmedia'),
        ),
    ]
