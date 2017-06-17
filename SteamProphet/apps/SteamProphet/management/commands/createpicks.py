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
    jokers = postbody.select('span[style="font-weight: bold"]')
    fallbacks = postbody.select('span[style="font-style: italic"]')
    joker = jokers[0].text.strip()
    fallback = fallbacks[0].text.strip()
    stripped_strings = list(postbody.stripped_strings)
    assert(len(stripped_strings) == 7)
    assert(len(jokers) == 1)
    assert(len(fallbacks) == 1)
    assert(joker != fallback)
    picks = []
    for string in stripped_strings:
        try:
            picks.append(Pick(player=player, game=Game.objects.get(name__iexact=string),
                              joker=string == joker,
                              fallback=string == fallback))
        except:
            print('Could not create Pick {} picks {}'.format(player, string))
            raise
    return picks


class Command(BaseCommand):
    help = 'Creates random data'

    @transaction.atomic
    def handle(self, *args, **options):
        basepage = 'https://forum.gamespodcast.de/viewtopic.php?f=9&p=37084'
        soup = BeautifulSoup(requests.get(basepage).text, 'html5lib')
        pages = len(soup.select('.pagination')[0].select('a'))
        if pages:
            for i in range(pages):
                parsePage('{}&start={}'.format(basepage, 20 * i))
        else:
            parsePage(basepage)
