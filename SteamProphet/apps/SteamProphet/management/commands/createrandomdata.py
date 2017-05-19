import random

import requests
import time
from django.core.management.base import BaseCommand
from django.db import transaction

from SteamProphet.apps.SteamProphet.models import Game, Player, Pick



def assignPicks(player):
    games = list(Game.objects.all())
    random.shuffle(games)
    for game in games[:5]:
        Pick.objects.create(game=game, player=player, joker=False)
    Pick.objects.create(game=games[5], player=player, joker=True)


class Command(BaseCommand):
    help = 'Creates random data'

    @transaction.atomic
    def handle(self, *args, **options):
        players = [Player.objects.create(name='André'),
                   Player.objects.create(name='Jochen'),
                   Player.objects.create(name='Sebastian Stange'),
                   Player.objects.create(name='Dr. Zoidberg[np]'),
                   Player.objects.create(name='goschi'),
                   Player.objects.create(name='Symm'),
                   Player.objects.create(name='Da Frenz'),
                   Player.objects.create(name='Varus'),
                   Player.objects.create(name='Maxi'),
                   Player.objects.create(name='NobodyJPH'),
                   Player.objects.create(name='Peter'),
                   Player.objects.create(name='quod'),
                   Player.objects.create(name='Seniorenzivi'),
                   Player.objects.create(name='Darkcloud'),
                   Player.objects.create(name='Axel'),
                   Player.objects.create(name='Simon'),
                   Player.objects.create(name='lnhh'),
                   Player.objects.create(name='Nebhotep'),
                   Player.objects.create(name='Peninsula'),
                   Player.objects.create(name='Nachtfischer'),
                   Player.objects.create(name='Magier1996'),
                   Player.objects.create(name='wudu'),
                   Player.objects.create(name='Vinter'),
                   Player.objects.create(name='NimaroKun')]
        for player in players:
            assignPicks(player)
