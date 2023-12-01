# Generated by Django 4.2.5 on 2023-11-24 09:30

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0012_alter_ticket_ticket_key_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='ticket_key',
            field=models.UUIDField(default=uuid.UUID('782e1032-a545-4a05-adca-891dbdf0c544')),
        ),
        migrations.AlterField(
            model_name='ticket_issues',
            name='error_key',
            field=models.UUIDField(default=uuid.UUID('efe47c5d-b2d5-48fc-8088-881b9f1686a7')),
        ),
        migrations.AlterField(
            model_name='ticket_payment',
            name='payment_id',
            field=models.UUIDField(default=uuid.UUID('3385f982-a9a5-4bc8-83c7-8ca1bdaa3b3e')),
        ),
    ]