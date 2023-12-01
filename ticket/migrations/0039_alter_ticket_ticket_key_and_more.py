# Generated by Django 4.2.5 on 2023-11-28 08:46

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0038_alter_ticket_ticket_key_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='ticket_key',
            field=models.UUIDField(default=uuid.UUID('a5cba008-23dd-47d6-87c0-89545b66a55a')),
        ),
        migrations.AlterField(
            model_name='ticket_issues',
            name='error_key',
            field=models.UUIDField(default=uuid.UUID('99baa2a4-71ad-43dd-a851-2f3f3e80a89e')),
        ),
        migrations.AlterField(
            model_name='ticket_payment',
            name='payment_id',
            field=models.UUIDField(default=uuid.UUID('42ca9aca-6919-4336-a9e5-9ef1f8be1d33')),
        ),
    ]