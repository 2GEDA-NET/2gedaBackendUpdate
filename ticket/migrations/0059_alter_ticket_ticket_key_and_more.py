# Generated by Django 4.2.5 on 2023-11-28 17:49

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0058_alter_ticket_ticket_key_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='ticket_key',
            field=models.UUIDField(default=uuid.UUID('0a4ebef1-8b6e-49f3-8bf1-7575a4c0f958')),
        ),
        migrations.AlterField(
            model_name='ticket_issues',
            name='error_key',
            field=models.UUIDField(default=uuid.UUID('f46d9671-e4da-44bc-b348-23641567761b')),
        ),
        migrations.AlterField(
            model_name='ticket_payment',
            name='payment_id',
            field=models.UUIDField(default=uuid.UUID('729203ad-2b07-423c-b600-f62ce0ef5373')),
        ),
    ]
