import calendar
import json

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import now

from SteamProphet.apps.SteamProphet import services
from SteamProphet.apps.SteamProphet.models import Player


class Command(BaseCommand):
    help = 'Updates all players'

    @transaction.atomic
    def handle(self, *args, **options):
        for player in Player.objects.all():
            self.savePlayerHistory(player)
            player.save()

    def savePlayerHistory(self, player):
        if player.history:
            history = json.loads(player.history)
        else:
            history = []

        timestamp = calendar.timegm(now().date().timetuple())
        latestEntry = {
            'score': services.computePlayerScore(player),
            'timestamp': timestamp
        }
        if history and history[-1]['timestamp'] == timestamp:
            history[-1] = latestEntry
        else:
            history.append(latestEntry)
        player.history = json.dumps(history)
