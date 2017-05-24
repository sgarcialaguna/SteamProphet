from dateutil.parser import *
import requests
import time
from django.core.management.base import BaseCommand
from django.db import transaction

from SteamProphet.apps.SteamProphet.models import Game


class Command(BaseCommand):
    help = 'Updates all games'

    @transaction.atomic
    def handle(self, *args, **options):
        for game in Game.objects.all():
            gameJSON = requests.get('https://steamspy.com/api.php?request=appdetails&appid={}'.
                                    format(game.appID)).json()
            game.players = gameJSON['players_forever']
            game.playersVariance = gameJSON['players_forever_variance']
            newPrice = gameJSON['price']
            try:
                newPrice = float(newPrice)
                newPrice /= 100.0
            except (ValueError, TypeError):
                newPrice = 0.0
            if game.price != newPrice:
                if game.price == 0:
                    game.price = newPrice
                else:
                    game.price = min(game.price, newPrice)
            gameJSON = requests.get('http://store.steampowered.com/api/appdetails/?appids={}&l=english'.
                                    format(game.appID)).json()
            releaseDateString = gameJSON[str(game.appID)]['data']['release_date']['date']
            try:
                game.releaseDate = parse(releaseDateString).date()
            except ValueError:
                print('{} has invalid release date {}'.format(game.name, releaseDateString))
                game.releaseDate = None
            game.save()
            # Rate limiter
            time.sleep(0.5)
