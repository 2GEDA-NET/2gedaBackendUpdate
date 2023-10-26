# Generated by Django 4.2.5 on 2023-10-26 09:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('bank_code', models.BigIntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='event-images/')),
                ('title', models.CharField(max_length=250)),
                ('desc', models.TextField()),
                ('platform', models.CharField(max_length=300)),
                ('date', models.DateTimeField(auto_now=True)),
                ('location', models.CharField(blank=True, max_length=250, null=True)),
                ('url', models.URLField(blank=True, max_length=250, null=True)),
                ('is_popular', models.BooleanField(default=False, verbose_name='Popular')),
                ('is_promoted', models.BooleanField(default=False, verbose_name='Promoted')),
            ],
        ),
        migrations.CreateModel(
            name='EventCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('image', models.ImageField(blank=True, null=True, upload_to='event-category-images/')),
            ],
        ),
        migrations.CreateModel(
            name='EventPromotionRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_date', models.DateTimeField(auto_now_add=True)),
                ('is_approved', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='PayOutInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_name', models.CharField(blank=True, max_length=250, null=True)),
                ('account_number', models.BigIntegerField()),
                ('account_type', models.CharField(choices=[('Savings', 'Savings'), ('Current', 'Current')], max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('VIP', 'VIP'), ('Stock', 'Stock')], max_length=250)),
                ('price', models.IntegerField()),
                ('quantity', models.IntegerField()),
                ('is_sold', models.BooleanField(default=False, verbose_name='Ticket Sold')),
            ],
        ),
        migrations.CreateModel(
            name='TicketPurchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_status', models.CharField(choices=[('Pending', 'Pending'), ('Successful', 'Successful'), ('Failed', 'Failed')], default='Pending', max_length=250)),
                ('payment_details', models.TextField(blank=True, null=True)),
                ('purchase_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Ticket Purchases',
            },
        ),
        migrations.CreateModel(
            name='Withdraw',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.BigIntegerField()),
                ('is_successful', models.BooleanField(default=False, verbose_name='SUCCESSFUL')),
                ('is_pending', models.BooleanField(default=False, verbose_name='PENDING')),
                ('is_failed', models.BooleanField(default=False, verbose_name='FAILED')),
            ],
        ),
        migrations.CreateModel(
            name='WithdrawalHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Successful', 'Successful'), ('Failed', 'Failed')], default='Pending', max_length=20)),
                ('withdrawal_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='WithdrawalRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Successful', 'Successful'), ('Failed', 'Failed')], default='Pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('details', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticket.payoutinfo')),
            ],
        ),
    ]