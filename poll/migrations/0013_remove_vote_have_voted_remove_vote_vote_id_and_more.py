# Generated by Django 4.2.5 on 2023-11-28 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0012_vote_all_poll_alter_vote_vote_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vote',
            name='have_Voted',
        ),
        migrations.RemoveField(
            model_name='vote',
            name='vote_id',
        ),
        migrations.AlterField(
            model_name='vote',
            name='cost',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]