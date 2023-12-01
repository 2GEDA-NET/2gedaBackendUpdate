# Generated by Django 4.2.5 on 2023-11-26 07:26

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0020_alter_ticket_ticket_key_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='ticket_key',
            field=models.UUIDField(default=uuid.UUID('f3d78cf6-5c69-4b09-a03c-fe3b444d106e')),
        ),
        migrations.AlterField(
            model_name='ticket_issues',
            name='error_key',
            field=models.UUIDField(default=uuid.UUID('a1788d98-a483-45fe-bd40-e8667092d30e')),
        ),
        migrations.AlterField(
            model_name='ticket_payment',
            name='payment_id',
            field=models.UUIDField(default=uuid.UUID('a8016a1a-9bf6-4d4c-809f-67d09481b403')),
        ),
    ]