# tasks.py

from celery import shared_task
from .utils import update_top_tracks

@shared_task
def update_top_tracks_periodically():
    update_top_tracks()
