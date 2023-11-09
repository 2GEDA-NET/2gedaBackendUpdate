# Generated by Django 4.2.5 on 2023-11-07 12:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Advert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=250, null=True)),
                ('duration', models.CharField(choices=[('24 hours', '24 hours'), ('48 hours', '48 hours'), ('72 hours', '72 hours'), ('1 week', '1 week'), ('2 week', '2 week'), ('1 month', '1 month'), ('3 months', '3 months'), ('1 year', '1 year')], max_length=250)),
                ('custom_duration_start', models.DateTimeField()),
                ('custom_duration_end', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='AdvertCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=250, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('timestamp', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='CommentMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media', models.FileField(blank=True, null=True, upload_to='comment_files/')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(blank=True, null=True)),
                ('content', models.TextField()),
                ('timestamp', models.TimeField()),
                ('hashtag', models.CharField(blank=True, max_length=250)),
                ('is_business_post', models.BooleanField(default=False, verbose_name='Business Post')),
                ('is_personal_post', models.BooleanField(default=True, verbose_name='Personal Post')),
            ],
        ),
        migrations.CreateModel(
            name='PostMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media', models.FileField(blank=True, null=True, upload_to='post_files/')),
            ],
        ),
        migrations.CreateModel(
            name='PromotedPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('promotion_status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PromotionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('duration', models.IntegerField(help_text='Duration in days')),
            ],
        ),
        migrations.CreateModel(
            name='Reaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reaction_type', models.CharField(choices=[('like', 'Like'), ('dislike', 'Dislike'), ('love', 'Love'), ('sad', 'Sad'), ('angry', 'Angry'), ('haha', 'Haha'), ('wow', 'Wow'), ('others', 'Others')], max_length=20, verbose_name='Reaction')),
            ],
        ),
        migrations.CreateModel(
            name='Reply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Repost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('timestamp', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='SavedPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='SharePost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.TextField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('shared_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feed.post')),
            ],
        ),
    ]
