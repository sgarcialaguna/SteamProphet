import calendar
import json
from functools import lru_cache
from operator import attrgetter

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import now

from SteamProphet.apps.SteamProphet import services
from SteamProphet.apps.SteamProphet.models import Player


@lru_cache()
def computeOrderedListOfPlayers():
    allPlayers = list(Player.objects.all())
    for player in allPlayers:
        player.score = services.computePlayerScore(player)
    return sorted(allPlayers, key=attrgetter('score'), reverse=True)


def savePlayerHistory(player):
    if player.history:
        history = json.loads(player.history)
    else:
        history = []

    allPlayers = computeOrderedListOfPlayers()
    timestamp = calendar.timegm(now().date().timetuple())
    latestEntry = {
        'score': services.computePlayerScore(player),
        'timestamp': timestamp,
        'position': allPlayers.index(player) + 1
    }
    if history and history[-1]['timestamp'] == timestamp:
        history[-1] = latestEntry
    else:
        history.append(latestEntry)
    player.history = json.dumps(history)


class Command(BaseCommand):
    help = 'Updates all players'

    @transaction.atomic
    def handle(self, *args, **options):
        for player in Player.objects.all():
            savePlayerHistory(player)
            player.save()
