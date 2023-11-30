# Generated by Django 4.2.5 on 2023-11-26 07:52

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0023_alter_ticket_ticket_key_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='ticket_key',
            field=models.UUIDField(default=uuid.UUID('da482f3f-c076-43be-9cde-78681b95f5ea')),
        ),
        migrations.AlterField(
            model_name='ticket_issues',
            name='error_key',
            field=models.UUIDField(default=uuid.UUID('60ac86b2-cf22-4d77-a4ba-9faff55c7296')),
        ),
        migrations.AlterField(
            model_name='ticket_payment',
            name='payment_id',
            field=models.UUIDField(default=uuid.UUID('bed53344-4573-43ac-9572-05f2437d17c3')),
        ),
    ]
