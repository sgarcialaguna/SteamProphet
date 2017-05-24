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
            gameJSON = requests.get('http://store.steampowered.com/api/appdetails/?appids={}&l=english&cc=us'.
                                    format(game.appID)).json()
            gameData = gameJSON[str(game.appID)]['data']
            releaseDateString = gameData['release_date']['date']
            newPrice = gameData.get('price_overview', {}).get('final', 0)
            self.setPrice(game, newPrice)
            self.setReleaseDate(game, releaseDateString)
            game.save()
            # Rate limiter
            time.sleep(0.5)

    def setPrice(self, game, newPrice):
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

    def setReleaseDate(self, game, releaseDateString):
        try:
            game.releaseDate = parse(releaseDateString).date()
        except ValueError:
            print('{} has invalid release date {}'.format(game.name, releaseDateString))
            game.releaseDate = None
