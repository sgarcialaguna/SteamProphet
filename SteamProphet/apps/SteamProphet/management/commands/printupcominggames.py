from django.core.management.base import BaseCommand
from django.db import transaction

from SteamProphet.apps.SteamProphet.models import Game, Week


class Command(BaseCommand):
    help = 'Print the upcoming games for the forum'

    def getWeek(self):
        for week in Week.objects.order_by('-week'):
            if week.game_set.exists():
                return week

    @transaction.atomic
    def handle(self, *args, **options):
        for game in Game.objects.filter(week=self.getWeek()):
            print('[URL=https://store.steampowered.com/app/{}/]{}[/URL]'.format(game.appID, game.name))
