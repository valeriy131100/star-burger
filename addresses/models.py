import requests
from django.conf import settings
from django.db import models
from django.utils import timezone


class Address(models.Model):
    NULL_COORDINATES = (None, None)

    address = models.CharField(
        max_length=200,
        verbose_name='адрес',
        db_index=True,
        unique=True
    )

    longitude = models.FloatField(
        verbose_name='долгота',
        null=True,
        default=None
    )
    latitude = models.FloatField(
        verbose_name='широта',
        null=True,
        default=None
    )

    update_date = models.DateTimeField(
        verbose_name='дата последнего обновления',
        null=True,
        default=None
    )

    def update_coordinates(self):
        address = self.address

        api_key = settings.YANDEX_GEOCODER_API_KEY

        base_url = "https://geocode-maps.yandex.ru/1.x"
        response = requests.get(base_url, params={
            "geocode": address,
            "apikey": api_key,
            "format": "json",
        })
        response.raise_for_status()
        found_places = (
            response.json()['response']['GeoObjectCollection']['featureMember']
        )

        if not found_places:
            raise ValueError(f'Bad address "{self.address}"')

        most_relevant = found_places[0]
        self.longitude, self.latitude = (
            most_relevant['GeoObject']['Point']['pos'].split(" ")
        )

        self.update_date = timezone.now()

        self.save()

    @property
    def coordinates(self):
        return self.latitude, self.longitude
