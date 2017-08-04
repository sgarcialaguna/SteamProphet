import datetime

import django
from django.test import TestCase

from SteamProphet.apps.SteamProphet.models import VotingPeriod, Week
from .. import services


class TestServices(TestCase):
    def test_getCurrentVotingPeriodReturnsNoneIfThereIsNoTimePeriod(self):
        self.assertIsNone(services.getCurrentVotingPeriod())

    def test_getCurrentVotingPeriodReturnsNoneIfAllVotingPeriodsAreInTheFuture(self):
        now = django.utils.timezone.now()
        week1 = Week.objects.create(week=1)
        week2 = Week.objects.create(week=2)
        VotingPeriod.objects.create(
            week=week1,
            start=now + datetime.timedelta(days=7),
            end=now + datetime.timedelta(days=10)
        )
        VotingPeriod.objects.create(
            week=week2,
            start=now + datetime.timedelta(days=14),
            end=now + datetime.timedelta(days=17)
        )
        self.assertIsNone(services.getCurrentVotingPeriod())

    def test_getCurrentVotingPeriodReturnsNoneIfAllVotingPeriodsAreInThePast(self):
        now = django.utils.timezone.now()
        week1 = Week.objects.create(week=1)
        week2 = Week.objects.create(week=2)
        VotingPeriod.objects.create(
            week=week1,
            start=now - datetime.timedelta(days=14),
            end=now - datetime.timedelta(days=17)
        )
        VotingPeriod.objects.create(
            week=week2,
            start=now - datetime.timedelta(days=7),
            end=now - datetime.timedelta(days=10)
        )
        self.assertIsNone(services.getCurrentVotingPeriod())

    def test_getCurrentVotingPeriodsReturnsTheCurrentVotingPeriodIfVotingPeriodIsNow(self):
        now = django.utils.timezone.now()
        week1 = Week.objects.create(week=1)
        week2 = Week.objects.create(week=2)
        VotingPeriod.objects.create(
            week=week1,
            start=now - datetime.timedelta(days=7),
            end=now - datetime.timedelta(days=10)
        )
        votingPeriod2 = VotingPeriod.objects.create(
            week=week2,
            start=now - datetime.timedelta(days=2),
            end=now + datetime.timedelta(days=1),
        )
        self.assertEqual(votingPeriod2, services.getCurrentVotingPeriod())
