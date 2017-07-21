import requests
from dateutil import relativedelta, parser
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import now

from SteamProphet.apps.SteamProphet.models import Game


class Command(BaseCommand):
    help = 'Imports the upcoming games'

    @transaction.atomic
    def handle(self, *args, **options):
        week = Game.objects.order_by('-week').first().week + 1
        upcomingGamesJSON = requests.get('https://www.steamprophet.com/api/upcoming').json()
        nextMonday = now().date() + relativedelta.relativedelta(weekday=relativedelta.MO)
        nextSunday = nextMonday + relativedelta.relativedelta(weekday=relativedelta.SU)
        for gameJSON in upcomingGamesJSON:
            try:
                releasedate = parser.parse(gameJSON['release_date']).date()
            except ValueError:
                continue
            if releasedate < nextMonday or releasedate > nextSunday:
                continue
            if not Game.objects.filter(appID=gameJSON['steam_id']).exists():
                Game.objects.create(appID=gameJSON['steam_id'], name=gameJSON['name'], week=week)
