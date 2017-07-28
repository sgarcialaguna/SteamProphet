import requests
from dateutil import relativedelta, parser
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import now

from SteamProphet.apps.SteamProphet.models import Game, Week


class Command(BaseCommand):
    help = 'Imports the upcoming games'

    @transaction.atomic
    def handle(self, *args, **options):
        latestGame = Game.objects.order_by('-week').first()
        latestWeek = latestGame.week if latestGame else None
        weekNumber = latestWeek.week + 1 if latestWeek else 1
        weekObject = Week.objects.get_or_create(week=weekNumber)[0]
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
                game = Game.objects.create(appID=gameJSON['steam_id'], name=gameJSON['name'])
                game.week.add(weekObject)
            else:
                game = Game.objects.get(appID=gameJSON['steam_id'])
                game.week.add(weekObject)
