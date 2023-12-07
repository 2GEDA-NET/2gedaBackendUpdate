import os
import json
from user.models import UserGeoInformation
import csv
import requests 
from django.core.management.base import BaseCommand 



class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(current_dir, 'worldcities.csv')

        data = []

        with open(csv_file_path, newline='', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                data.append(row)

        print(data)

        for entry in data:
            print(entry["admin_name"])
            if not UserGeoInformation.objects.filter(
                city_ascii = entry["city_ascii"],
                lat = entry["lat"],
                lng = entry["lng"],
                country = entry["country"],
                iso2 = entry["iso2"],
                iso3 = entry["iso3"],
                admin_name = entry["admin_name"],
                capital = entry["capital"],
                population = entry["population"],
                mid = entry["id"]
            ).exists():
                print("populating...")
                UserGeoInformation.objects.create(
                    city_ascii = entry["city_ascii"],
                    lat = entry["lat"],
                    lng = entry["lng"],
                    country = entry["country"],
                    iso2 = entry["iso2"],
                    iso3 = entry["iso3"],
                    admin_name = entry["admin_name"],
                    capital = entry["capital"],
                    population = entry["population"],
                    mid = entry["id"]
                )

        print("done")
    