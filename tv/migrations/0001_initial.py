# Generated by Django 4.2.5 on 2023-11-11 09:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_like', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='TVAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tv_username', models.CharField(max_length=250)),
                ('tv_password', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('video_file', models.FileField(upload_to='tv-videos/')),
                ('video_cover', models.ImageField(upload_to='video_cover/')),
                ('description', models.TextField()),
                ('duration', models.DurationField(blank=True, null=True, verbose_name='Duration')),
                ('date_of_release', models.DateField()),
                ('year_of_release', models.IntegerField()),
                ('visibility', models.CharField(choices=[('Public', 'Public'), ('Private', 'Private')], max_length=250)),
                ('is_top_movie', models.BooleanField(default=False, verbose_name='Top Movie')),
                ('is_new_release', models.BooleanField(default=False, verbose_name='New Release')),
                ('availbility', models.CharField(choices=[('All Ages', 'All Ages'), ('PG', 'PG (Parental Guidance)'), ('13+', '13 and older'), ('18+', '18 and older')], max_length=20)),
                ('is_movie_premiere', models.BooleanField(default=False, verbose_name='Movie Premiere')),
                ('download_count', models.PositiveIntegerField(default=0, verbose_name='Download Count')),
                ('hidden', models.BooleanField(default=False)),
                ('scheduled_date_time', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VideoCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('desc', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VideoTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=100)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tv.video')),
            ],
        ),
        migrations.CreateModel(
            name='VideoLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tv.tvaccount')),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tv.video')),
            ],
        ),
        migrations.AddField(
            model_name='video',
            name='video_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tv.videocategory'),
        ),
    ]
