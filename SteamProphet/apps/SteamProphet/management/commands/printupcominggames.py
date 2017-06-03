import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from SteamProphet.apps.SteamProphet.models import Game


class Command(BaseCommand):
    help = 'Print the upcoming games for the forum'

    @transaction.atomic
    def handle(self, *args, **options):
        startDate = datetime.date(month=6, day=5, year=2017)
        endDate = datetime.date(month=6, day=11, year=2017)
        games = Game.objects.filter(releaseDate__range=(startDate, endDate))
        for game in games:
            print('[URL=https://store.steampowered.com/app/{}/]{}[/URL]'.format(game.appID, game.name))
