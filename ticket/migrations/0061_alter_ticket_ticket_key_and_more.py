# Generated by Django 4.2.5 on 2023-11-28 20:29

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0060_alter_ticket_ticket_key_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='ticket_key',
            field=models.UUIDField(default=uuid.UUID('9ca08af1-5c28-4b70-8ab3-1efce299cdff')),
        ),
        migrations.AlterField(
            model_name='ticket_issues',
            name='error_key',
            field=models.UUIDField(default=uuid.UUID('c4c8ea43-a118-414a-872d-f20c4d1a18d4')),
        ),
        migrations.AlterField(
            model_name='ticket_payment',
            name='payment_id',
            field=models.UUIDField(default=uuid.UUID('5fd50b77-e630-4ce3-8bd0-63bade2397fa')),
        ),
    ]
