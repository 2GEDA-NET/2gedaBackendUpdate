# Generated by Django 4.2.1 on 2023-10-12 12:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0004_remove_university_university_question_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='university',
            old_name='university_name',
            new_name='name',
        ),
    ]
