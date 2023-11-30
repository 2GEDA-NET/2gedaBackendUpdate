# Generated by Django 4.2.5 on 2023-11-26 07:56

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0024_alter_ticket_ticket_key_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='ticket_key',
            field=models.UUIDField(default=uuid.UUID('d8af4899-4323-4eb2-8e77-101eed205b27')),
        ),
        migrations.AlterField(
            model_name='ticket_issues',
            name='error_key',
            field=models.UUIDField(default=uuid.UUID('7e80a3be-2126-4cf0-aad0-1930fa4de584')),
        ),
        migrations.AlterField(
            model_name='ticket_payment',
            name='payment_id',
            field=models.UUIDField(default=uuid.UUID('d58cebd8-4ffe-419d-bb83-edd3f794c4cb')),
        ),
    ]
