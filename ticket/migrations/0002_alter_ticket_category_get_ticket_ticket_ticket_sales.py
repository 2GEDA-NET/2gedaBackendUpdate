# Generated by Django 4.2.5 on 2023-11-18 17:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ticket', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='category',
            field=models.CharField(blank=True, choices=[('VIP', 'VIP'), ('Stock', 'Stock'), ('Regular', 'Regular')], max_length=250, null=True),
        ),
        migrations.CreateModel(
            name='Get_Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=256)),
                ('last_name', models.CharField(max_length=256)),
                ('email', models.CharField(blank=True, max_length=256, null=True)),
                ('quantity', models.IntegerField(default=0)),
                ('address', models.CharField(max_length=256)),
                ('ticket_type', models.CharField(choices=[('FREE TICKET', 'FREE TICKET'), ('PAID TICKET', 'PAID TICKET')], default='FREE TICKET', max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='ticket',
            name='ticket_sales',
            field=models.ManyToManyField(to='ticket.get_ticket'),
        ),
    ]