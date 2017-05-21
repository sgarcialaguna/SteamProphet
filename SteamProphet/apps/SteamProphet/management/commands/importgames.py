import requests
from django.core.management.base import BaseCommand
from django.db import transaction

from SteamProphet.apps.SteamProphet.models import Game


class Command(BaseCommand):
    help = 'Imports the upcoming games'

    @transaction.atomic
    def handle(self, *args, **options):
        upcomingGamesJSON = requests.get('https://www.steamprophet.com/api/upcoming').json()
        for gameJSON in upcomingGamesJSON:
            Game.objects.create(appID=gameJSON['steam_id'], name=gameJSON['name'])