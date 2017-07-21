import calendar
import json
import time

import requests
from dateutil.parser import *
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import now

from SteamProphet.apps.SteamProphet.models import Game


class Command(BaseCommand):
    help = 'Updates all games'

    @transaction.atomic
    def handle(self, *args, **options):
        for game in Game.objects.filter(matured=False):
            try:
                gameJSON = requests.get('https://steamspy.com/api.php?request=appdetails&appid={}'.
                                        format(game.appID)).json()
                game.players = gameJSON['players_forever']
                game.playersVariance = gameJSON['players_forever_variance']
                gameJSON = requests.get('http://store.steampowered.com/api/appdetails/?appids={}&l=english&cc=us'.
                                        format(game.appID)).json()
                gameData = gameJSON[str(game.appID)]['data']
                game.name = gameData['name']
                releaseDateString = gameData['release_date']['date']
                newPrice = gameData.get('price_overview', {}).get('final', 0)
                self.setPrice(game, newPrice)
                self.setReleaseDate(game, releaseDateString)
                self.setMaturedFlag(game, gameData)
                self.saveHistory(game)
                game.save()
                # Rate limiter
                time.sleep(0.5)
            except:
                print('Could not update game {}'.format(game.name))

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

    def setMaturedFlag(self, game, gameData):
        if not game.releaseDate or gameData['release_date']['coming_soon']:
            return
        today = now().date()
        if (today - game.releaseDate).days >= 28:
            game.matured = True

    def saveHistory(self, game):
        if game.history:
            history = json.loads(game.history)
        else:
            history = []

        timestamp = calendar.timegm(now().date().timetuple())
        if history and history[-1]['timestamp'] == timestamp:
            return

        history.append({
          'players': game.players,
          'playersVariance': game.playersVariance,
          'price': float(game.price),
          'timestamp': timestamp
        })
        game.history = json.dumps(history)
