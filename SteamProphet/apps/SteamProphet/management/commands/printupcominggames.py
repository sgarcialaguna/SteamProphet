from operator import attrgetter

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.db import transaction

from SteamProphet.apps.SteamProphet.models import Game, Week


def getFollowers(game):
    text = requests.get('https://steamspy.com/app/{}'.format(game.appID)).text
    soup = BeautifulSoup(text, 'html5lib')
    strings = soup.stripped_strings
    for s in strings:
        if s == 'Followers':
            # example: ": 34,586
            return int(next(strings)[2:].replace(',', ''))

    return 0


class Command(BaseCommand):
    help = 'Print the upcoming games for the forum'

    def getWeek(self):
        for week in Week.objects.order_by('-week'):
            if week.game_set.exists():
                return week

    @transaction.atomic
    def handle(self, *args, **options):
        games = []
        for game in Game.objects.filter(week=self.getWeek()):
            game.url = 'https://store.steampowered.com/app/{}/'.format(game.appID)
            game.followers = getFollowers(game)
            games.append(game)
        games = sorted(games, key=attrgetter('followers'), reverse=True)
        for game in games:
            print('[URL="{url}"]{name}[/URL] ({followers})'.format(
                url=game.url,
                name=game.name,
                followers=game.followers
            ))
