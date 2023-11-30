# Generated by Django 4.2.5 on 2023-11-29 14:38

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0067_alter_ticket_ticket_key_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='ticket_key',
            field=models.UUIDField(default=uuid.UUID('beb27ee6-01a8-4267-b602-128ec08e3d82')),
        ),
        migrations.AlterField(
            model_name='ticket_issues',
            name='error_key',
            field=models.UUIDField(default=uuid.UUID('0265cf99-afd0-4b41-b863-d87fc24a8b1e')),
        ),
        migrations.AlterField(
            model_name='ticket_payment',
            name='payment_id',
            field=models.UUIDField(default=uuid.UUID('29b6e3e9-2b84-45ad-8988-affc593ad499')),
        ),
    ]
