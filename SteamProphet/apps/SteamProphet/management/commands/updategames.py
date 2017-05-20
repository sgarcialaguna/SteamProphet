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
            gameJSON = requests.get('https://steamspy.com/api.php?request=appdetails&appid={}'.format(game.appID))
            game.players = gameJSON['players']
            game.playersVariance = gameJSON['players_variance']
            if game.price != gameJSON['price']:
                if game.price == 0:
                    game.price = gameJSON['price']
                else:
                    game.price = min(game.price, gameJSON['price'])
            game.save()
            # Rate limiter
            time.sleep(0.5)
