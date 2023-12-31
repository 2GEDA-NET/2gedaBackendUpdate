# Generated by Django 4.2.5 on 2023-11-11 09:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
        ('stereo', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='usersongpreference',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.userprofile'),
        ),
        migrations.AddField(
            model_name='stereoaccount',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.userprofile'),
        ),
        migrations.AddField(
            model_name='song',
            name='album',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stereo.album'),
        ),
        migrations.AddField(
            model_name='song',
            name='genre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stereo.genre'),
        ),
        migrations.AddField(
            model_name='playlist',
            name='songs',
            field=models.ManyToManyField(blank=True, related_name='playlists', to='stereo.song'),
        ),
        migrations.AddField(
            model_name='playlist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stereo.musicprofile'),
        ),
        migrations.AddField(
            model_name='musicprofile',
            name='favorite_genre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stereo.genre'),
        ),
        migrations.AddField(
            model_name='musicprofile',
            name='listening_history',
            field=models.ManyToManyField(blank=True, related_name='listeners', to='stereo.song'),
        ),
        migrations.AddField(
            model_name='musicprofile',
            name='playlists',
            field=models.ManyToManyField(blank=True, related_name='users', to='stereo.playlist'),
        ),
        migrations.AddField(
            model_name='musicprofile',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stereo.stereoaccount'),
        ),
        migrations.AddField(
            model_name='downloadrecord',
            name='song',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stereo.song'),
        ),
        migrations.AddField(
            model_name='downloadrecord',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chart',
            name='song',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stereo.song'),
        ),
        migrations.AddField(
            model_name='album',
            name='artist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stereo.artist'),
        ),
        migrations.AlterUniqueTogether(
            name='usersongpreference',
            unique_together={('user', 'song')},
        ),
    ]
