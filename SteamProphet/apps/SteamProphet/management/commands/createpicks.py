import requests
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from django.db import transaction

from SteamProphet.apps.SteamProphet.models import Game, Player, Pick


def parsePage(page):
    source = requests.get(page, 'html5lib').text
    soup = BeautifulSoup(source, "html.parser")
    picks = []
    for post in soup.select('.post'):
        picks.extend(parsePost(post))
    Pick.objects.bulk_create(picks)


def parsePost(post):
    playername = post.select('[class^="username"]')[0].text
    if playername == 'Santiago Garcia':
        return []
    player = Player.objects.get_or_create(name=playername)[0]
    postbody = post.select('.content')[0]
    joker = postbody.select('span[style="font-weight: bold"]')[0].text
    picks = []
    for string in postbody.stripped_strings:
        picks.append(Pick(player=player, game=Game.objects.get(name=string), joker=string == joker))
    return picks


class Command(BaseCommand):
    help = 'Creates random data'

    @transaction.atomic
    def handle(self, *args, **options):
        basepage = 'https://forum.gamespodcast.de/viewtopic.php?f=4&t=2178'
        soup = BeautifulSoup(requests.get(basepage).text, 'html5lib')
        pages = len(soup.select('.pagination'))
        for i in range(pages):
            parsePage('{}&start={}'.format(basepage, 20 * i))
