# Generated by Django 4.2.5 on 2023-11-11 09:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ticket', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='withdrawalrequest',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='withdrawalhistory',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='withdraw',
            name='details',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticket.payoutinfo'),
        ),
        migrations.AddField(
            model_name='ticketpurchase',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticket.event'),
        ),
        migrations.AddField(
            model_name='ticketpurchase',
            name='ticket',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticket.ticket'),
        ),
        migrations.AddField(
            model_name='ticketpurchase',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='payoutinfo',
            name='bank_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticket.bank'),
        ),
        migrations.AddField(
            model_name='payoutinfo',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='eventpromotionrequest',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticket.event'),
        ),
        migrations.AddField(
            model_name='eventpromotionrequest',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='attendees',
            field=models.ManyToManyField(blank=True, related_name='attended_events', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticket.eventcategory'),
        ),
        migrations.AddField(
            model_name='event',
            name='ticket',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticket.ticket'),
        ),
        migrations.AddField(
            model_name='event',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
