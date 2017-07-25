import datetime

import django
from django.contrib.auth.models import User, AnonymousUser
from django.test import RequestFactory, TestCase

from SteamProphet.apps.SteamProphet.models import Week, Game, Player, Pick, VotingPeriod
from ..views import PlayerDetailView


class TestPlayerDetailView(TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user('user')
        self.user2 = User.objects.create_user('user2')
        self.player = Player.objects.create(user=self.user)
        self.week = Week.objects.create(week=1)
        self.game = Game.objects.create(appID=1, name='Noun of Nouns')
        self.pick = Pick.objects.create(game=self.game, week=self.week, player=self.player)

    def test_anonymousUserCanSeePicks(self):
        request = self.factory.get('')
        request.user = AnonymousUser()
        response = PlayerDetailView.as_view()(request, pk=self.player.pk)
        self.assertContains(response, 'Noun of Nouns')

    def test_viewShowsPicksOfOtherPlayer(self):
        request = self.factory.get('')
        request.user = self.user2
        response = PlayerDetailView.as_view()(request, pk=self.player.pk)
        self.assertContains(response, 'Noun of Nouns')

    def test_viewDoesNotShowsPicksOfOtherPlayerForActiveVotingPeriod(self):
        now = django.utils.timezone.now()
        VotingPeriod.objects.create(week=self.week,
                                    start=now - datetime.timedelta(days=2),
                                    end=now + datetime.timedelta(days=2))
        request = self.factory.get('')
        request.user = self.user2
        response = PlayerDetailView.as_view()(request, pk=self.player.pk)
        self.assertNotContains(response, 'Noun of Nouns')

    def test_playersCanAlwaysSeeTheirOwnPicks(self):
        now = django.utils.timezone.now()
        VotingPeriod.objects.create(week=self.week,
                                    start=now - datetime.timedelta(days=2),
                                    end=now + datetime.timedelta(days=2))
        request = self.factory.get('')
        request.user = self.user
        response = PlayerDetailView.as_view()(request, pk=self.player.pk)
        self.assertContains(response, 'Noun of Nouns')

    def test_staffUserCanSeeAllThePicks(self):
        now = django.utils.timezone.now()
        VotingPeriod.objects.create(week=self.week,
                                    start=now - datetime.timedelta(days=2),
                                    end=now + datetime.timedelta(days=2))
        request = self.factory.get('')
        request.user = User.objects.create_superuser('admin', 'admin@example.com', 'secret')
        response = PlayerDetailView.as_view()(request, pk=self.player.pk)
        self.assertContains(response, 'Noun of Nouns')
