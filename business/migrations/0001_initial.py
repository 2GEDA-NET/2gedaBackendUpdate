# Generated by Django 4.2.5 on 2023-11-11 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street', models.CharField(max_length=250)),
                ('city', models.CharField(max_length=250)),
                ('state', models.CharField(max_length=250)),
                ('country', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='BusinessDirectory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('about', models.TextField()),
                ('email', models.EmailField(max_length=254)),
                ('website', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BusinessDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_type', models.CharField(max_length=100)),
                ('document_file', models.FileField(upload_to='business_documents/')),
            ],
        ),
        migrations.CreateModel(
            name='BusinessOwnerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number1', models.BigIntegerField(blank=True, null=True)),
                ('phone_number2', models.BigIntegerField(blank=True, null=True)),
                ('phone_number3', models.BigIntegerField(blank=True, null=True)),
                ('phone_number4', models.BigIntegerField(blank=True, null=True)),
            ],
        ),
    ]
