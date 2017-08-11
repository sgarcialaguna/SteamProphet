import datetime
import django
from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase

from SteamProphet.apps.SteamProphet.models import Player, Pick, Game, Week, VotingPeriod
from ..views import PickOverviewView


class TestPickOverviewView(TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user('user')
        self.player = Player.objects.create(name='player', user=self.user)
        self.user2 = User.objects.create_user('user2')
        self.player2 = Player.objects.create(name='player2', user=self.user2)

    def test_noPicks(self):
        request = self.factory.get('')
        request.user = AnonymousUser()
        view = PickOverviewView(request=request)
        self.assertEqual(view.get_games(), [])

    def test_onePick(self):
        week = Week.objects.create(week=1)
        game = Game.objects.create(appID=1, name='Noun of Nouns')
        game.week.add(week)
        Pick.objects.create(week=week, game=game, player=self.player)

        request = self.factory.get('')
        request.user = AnonymousUser()
        view = PickOverviewView(request=request)

        games = view.get_games()
        self.assertEqual(len(games), 1)
        game = games[0]
        self.assertEqual(game, game)
        self.assertEqual(game.picked, 1)
        self.assertEqual(game.pickedAsJoker, 0)

    def test_two_picks_and_a_joker(self):
        week = Week.objects.create(week=1)
        game = Game.objects.create(appID=1, name='Noun of Nouns')
        game.week.add(week)
        Pick.objects.create(week=week, game=game, player=self.player)
        Pick.objects.create(week=week, game=game, player=self.player2, joker=True)

        request = self.factory.get('')
        request.user = AnonymousUser()
        view = PickOverviewView(request=request)

        games = view.get_games()
        self.assertEqual(len(games), 1)
        game = games[0]
        self.assertEqual(game, game)
        self.assertEqual(game.picked, 2)
        self.assertEqual(game.pickedAsJoker, 1)

    def test_do_not_show_picks_from_current_votingPeriod(self):
        week = Week.objects.create(week=1)
        game = Game.objects.create(appID=1, name='Noun of Nouns')
        game.week.add(week)
        Pick.objects.create(week=week, game=game, player=self.player)
        now = django.utils.timezone.now()
        VotingPeriod.objects.create(week=week, start=now - datetime.timedelta(days=2),
                                    end=now + datetime.timedelta(days=2))

        request = self.factory.get('')
        request.user = AnonymousUser()
        view = PickOverviewView(request=request)

        self.assertEqual(view.get_games(), [])

    def test_staff_user_sees_all_the_picks(self):
        week = Week.objects.create(week=1)
        game = Game.objects.create(appID=1, name='Noun of Nouns')
        game.week.add(week)
        Pick.objects.create(week=week, game=game, player=self.player)
        now = django.utils.timezone.now()
        VotingPeriod.objects.create(week=week, start=now - datetime.timedelta(days=2),
                                    end=now + datetime.timedelta(days=2))

        request = self.factory.get('')
        request.user = User.objects.create_user('staff', is_staff=True)
        view = PickOverviewView(request=request)

        self.assertEqual(view.get_games(), [game])

    def test_games_are_sorted_descending_by_number_of_picks(self):
        week = Week.objects.create(week=1)
        game = Game.objects.create(appID=1, name='Noun of Nouns')
        game.week.add(week)
        Pick.objects.create(week=week, game=game, player=self.player)

        game2 = Game.objects.create(appID=2, name='Noun of Nouns 2 - The Sequel')
        game2.week.add(week)
        Pick.objects.create(week=week, game=game2, player=self.player)
        Pick.objects.create(week=week, game=game2, player=self.player2)

        request = self.factory.get('')
        request.user = AnonymousUser()
        view = PickOverviewView(request=request)

        games = view.get_games()
        self.assertEqual(games, [game2, game])
