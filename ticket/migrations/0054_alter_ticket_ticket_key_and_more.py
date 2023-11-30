# Generated by Django 4.2.5 on 2023-11-28 10:14

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0053_alter_ticket_ticket_key_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='ticket_key',
            field=models.UUIDField(default=uuid.UUID('32bcf371-c62b-42ba-914c-af246d1629bf')),
        ),
        migrations.AlterField(
            model_name='ticket_issues',
            name='error_key',
            field=models.UUIDField(default=uuid.UUID('af29e692-c446-4180-9dc2-bfc7b4e881c1')),
        ),
        migrations.AlterField(
            model_name='ticket_payment',
            name='payment_id',
            field=models.UUIDField(default=uuid.UUID('979e0372-a01e-4d09-9f94-96e5c44e07b6')),
        ),
    ]
