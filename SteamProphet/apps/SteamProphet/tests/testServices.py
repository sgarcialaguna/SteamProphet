import datetime

import pytz
from django.test import TestCase
from freezegun import freeze_time

from SteamProphet.apps.SteamProphet.models import Game
from ..import services


class TestServices(TestCase):
    def test_getPrecedingFriday(self):
        friday = datetime.date(year=2017, month=7, day=14)
        self.assertEqual(datetime.date(year=2017, month=7, day=7), services.getPrecedingFriday(friday))
        self.assertEqual(friday, services.getPrecedingFriday(friday + datetime.timedelta(days=1)))
        self.assertEqual(friday, services.getPrecedingFriday(friday + datetime.timedelta(days=2)))
        self.assertEqual(friday, services.getPrecedingFriday(friday + datetime.timedelta(days=3)))
        self.assertEqual(friday, services.getPrecedingFriday(friday + datetime.timedelta(days=4)))
        self.assertEqual(friday, services.getPrecedingFriday(friday + datetime.timedelta(days=5)))
        self.assertEqual(friday, services.getPrecedingFriday(friday + datetime.timedelta(days=6)))
        self.assertEqual(datetime.date(year=2017, month=7, day=14),
                         services.getPrecedingFriday(friday + datetime.timedelta(days=7)))

    def test_getCurrentWeekReturnsOneIfThereAreNoGames(self):
        self.assertEqual(1, services.getCurrentWeek())

    @freeze_time('2017-07-20')
    def test_getCurrentWeekReturnsOneUntilBeforeFridayFollowingTheFirstGamesRelease(self):
        Game.objects.create(appID=1, week=1, releaseDate=datetime.date(year=2017, month=7, day=17))
        self.assertEqual(1, services.getCurrentWeek())

    @freeze_time('2017-07-21')
    def test_theNextWeekDoesNotStartBeforeTheFollowingFriday(self):
        Game.objects.create(appID=1, week=42, releaseDate=datetime.date(year=2017, month=7, day=17))
        self.assertEqual(42, services.getCurrentWeek())

    def test_theNextWeekDoesNotStartBeforeTheFollowingFriday1900CET(self):
        Game.objects.create(appID=1, week=1, releaseDate=datetime.date(year=2017, month=7, day=17))
        tz = pytz.timezone('CET')
        dt = datetime.datetime(year=2017, month=7, day=21, hour=18, minute=59, second=59)
        dt = tz.localize(dt)
        with freeze_time(dt):
            self.assertEqual(1, services.getCurrentWeek())

    def test_theNextWeekStartsOnTheFollowingFriday1900CET(self):
        Game.objects.create(appID=1, week=1, releaseDate=datetime.date(year=2017, month=7, day=17))
        tz = pytz.timezone('CET')
        dt = datetime.datetime(year=2017, month=7, day=21, hour=19)
        dt = tz.localize(dt)
        with freeze_time(dt):
            self.assertEqual(2, services.getCurrentWeek())
