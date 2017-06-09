import datetime

from dateutil import relativedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import now

from SteamProphet.apps.SteamProphet.models import Game


class Command(BaseCommand):
    help = 'Print the upcoming games for the forum'

    @transaction.atomic
    def handle(self, *args, **options):
        nextMonday = now().date() + relativedelta.relativedelta(weekday=relativedelta.MO)
        nextSunday = nextMonday + relativedelta.relativedelta(weekday=relativedelta.SU)
        games = Game.objects.filter(releaseDate__range=(nextMonday, nextSunday))
        for game in games:
            print('[URL=https://store.steampowered.com/app/{}/]{}[/URL]'.format(game.appID, game.name))
