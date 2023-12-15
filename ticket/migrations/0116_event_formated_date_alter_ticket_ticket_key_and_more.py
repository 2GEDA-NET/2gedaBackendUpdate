# Generated by Django 4.2.5 on 2023-12-15 11:22

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0115_remove_event_is_free_alter_ticket_ticket_key_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='formated_date',
            field=models.CharField(default='15 Dec, 2023'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='ticket_key',
            field=models.UUIDField(default=uuid.UUID('1404013b-8f61-49b8-877c-22283efb3d8d')),
        ),
        migrations.AlterField(
            model_name='ticket_issues',
            name='error_key',
            field=models.UUIDField(default=uuid.UUID('b74811e1-631d-438e-a938-ad062bd9cfe1')),
        ),
        migrations.AlterField(
            model_name='ticket_payment',
            name='payment_id',
            field=models.UUIDField(default=uuid.UUID('d777c73d-ebb0-49d7-9814-8b3200f3bfe2')),
        ),
    ]
