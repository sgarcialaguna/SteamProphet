from django.core.management.base import BaseCommand
from django.db import transaction

from SteamProphet.apps.SteamProphet.models import Game


class Command(BaseCommand):
    help = 'Print the upcoming games for the forum'

    @transaction.atomic
    def handle(self, *args, **options):
        # week = Game.objects.order_by('-week__week').first().week.first()
        # games = Game.objects.filter(week=week)
        for game in Game.objects.all():
            print('[URL=https://store.steampowered.com/app/{}/]{}[/URL]'.format(game.appID, game.name))
