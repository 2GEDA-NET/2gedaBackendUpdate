# Generated by Django 4.2.5 on 2023-12-14 19:14

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0113_ticket_is_free_alter_ticket_ticket_key_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='ticket_key',
            field=models.UUIDField(default=uuid.UUID('ed34560d-77fc-490f-af4c-e38db792720f')),
        ),
        migrations.AlterField(
            model_name='ticket_issues',
            name='error_key',
            field=models.UUIDField(default=uuid.UUID('c47833e5-fbc1-42f3-a2bd-a2094aff4895')),
        ),
        migrations.AlterField(
            model_name='ticket_payment',
            name='payment_id',
            field=models.UUIDField(default=uuid.UUID('571ae28e-3f05-490c-9141-ef85a51a16f2')),
        ),
    ]
