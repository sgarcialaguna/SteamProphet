import datetime

import django
from django.test import TestCase

from SteamProphet.apps.SteamProphet.models import VotingPeriod
from .. import services


class TestServices(TestCase):
    def test_getCurrentVotingPeriodReturnsNoneIfThereIsNoTimePeriod(self):
        self.assertIsNone(services.getCurrentVotingPeriod())

    def test_getCurrentVotingPeriodReturnsNoneIfAllVotingPeriodsAreInTheFuture(self):
        now = django.utils.timezone.now()
        VotingPeriod.objects.create(
            week=1,
            start=now + datetime.timedelta(days=7),
            end=now + datetime.timedelta(days=10)
        )
        VotingPeriod.objects.create(
            week=2,
            start=now + datetime.timedelta(days=14),
            end=now + datetime.timedelta(days=17)
        )
        self.assertIsNone(services.getCurrentVotingPeriod())

    def test_getCurrentVotingPeriodReturnsNoneIfAllVotingPeriodsAreInThePast(self):
        now = django.utils.timezone.now()
        VotingPeriod.objects.create(
            week=1,
            start=now - datetime.timedelta(days=14),
            end=now - datetime.timedelta(days=17)
        )
        VotingPeriod.objects.create(
            week=2,
            start=now - datetime.timedelta(days=7),
            end=now - datetime.timedelta(days=10)
        )
        self.assertIsNone(services.getCurrentVotingPeriod())

    def test_getCurrentVotingPeriodsReturnsTheCurrentVotingPeriodIfVotingPeriodIsNow(self):
        now = django.utils.timezone.now()
        VotingPeriod.objects.create(
            week=1,
            start=now - datetime.timedelta(days=7),
            end=now - datetime.timedelta(days=10)
        )
        VotingPeriod.objects.create(
            week=2,
            start=now - datetime.timedelta(days=2),
            end=now + datetime.timedelta(days=1),
        )
        self.assertEqual(2, services.getCurrentVotingPeriod())
