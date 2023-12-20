# Generated by Django 4.2.5 on 2023-12-04 11:44

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0087_alter_ticket_ticket_key_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='ticket_key',
            field=models.UUIDField(default=uuid.UUID('b6c746d6-0ff2-42a6-9b62-d91634df6900')),
        ),
        migrations.AlterField(
            model_name='ticket_issues',
            name='error_key',
            field=models.UUIDField(default=uuid.UUID('ac83b538-4add-4ff2-b009-b14ba7e2d2bc')),
        ),
        migrations.AlterField(
            model_name='ticket_payment',
            name='payment_id',
            field=models.UUIDField(default=uuid.UUID('360f5038-79ca-4ed8-a8dc-bf81a91094b4')),
        ),
    ]