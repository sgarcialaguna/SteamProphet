import random

import requests
import time
from django.core.management.base import BaseCommand
from django.db import transaction

from SteamProphet.apps.SteamProphet.models import Game, Player, Pick



def assignPicks(player):
    games = list(Game.objects.all())
    random.shuffle(games)
    for game in games[:4]:
        Pick.objects.create(game=game, player=player, joker=False)
    Pick.objects.create(game=games[4], player=player, joker=True)


class Command(BaseCommand):
    help = 'Creates random data'

    @transaction.atomic
    def handle(self, *args, **options):
        for player in Player.objects.all():
            assignPicks(player)
