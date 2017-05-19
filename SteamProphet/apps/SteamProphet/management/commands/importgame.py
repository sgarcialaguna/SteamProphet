import requests
from django.core.management.base import BaseCommand
from django.db import transaction

from SteamProphet.apps.SteamProphet.models import Game


class Command(BaseCommand):
    help = 'Imports the specified game'

    def add_arguments(self, parser):
        parser.add_argument('steam_id', nargs='+', type=int)

    @transaction.atomic
    def handle(self, *args, **options):
        for steam_id in options['steam_id']:
            game = requests.get('https://steamspy.com/api.php?request=appdetails&appid={}'.format(steam_id)).json()
            price = game['price']
            try:
                price = float(price)
                price /= 100.0
            except (ValueError, TypeError):
                price = 0.0
            Game.objects.create(appID=game['appid'], name=game['name'], owners=game['owners'],
                                ownersVariance=game['owners_variance'], price=price)
