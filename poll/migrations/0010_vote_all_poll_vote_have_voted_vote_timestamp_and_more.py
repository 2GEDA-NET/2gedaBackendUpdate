# Generated by Django 4.2.5 on 2023-11-28 10:13

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0009_remove_vote_poll_alter_vote_vote_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='all_poll',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='each_poll', to='poll.poll'),
        ),
        migrations.AddField(
            model_name='vote',
            name='have_Voted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vote',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='vote',
            name='vote_id',
            field=models.UUIDField(default=uuid.UUID('98679a82-4dd7-49ce-886d-9ece9c2ebf73')),
        ),
    ]