import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import now

from SteamProphet.apps.SteamProphet.models import Game


class Command(BaseCommand):
    help = 'Updates all games'

    @transaction.atomic
    def handle(self, *args, **options):
        for game in Game.objects.filter(matured=False).filter(releaseDate__lt=now().date()):
            gameJSON = requests.get('http://store.steampowered.com/api/appdetails/?appids={}&l=english&cc=us'.
                                    format(game.appID)).json()
            gameData = gameJSON[str(game.appID)]['data']
            comingSoon = gameData['release_date']['coming_soon']
            if comingSoon:
                print('{} is overdue'.format(game.name))