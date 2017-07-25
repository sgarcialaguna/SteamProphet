import datetime

import django
from django.contrib.auth.models import User
from django.test import TestCase
from freezegun import freeze_time

from SteamProphet.apps.SteamProphet.models import Player, Game, VotingPeriod, Week, Pick
from ..forms import CreatePicksForm


@freeze_time('2017-07-15')
class TestCreatePicksForm(TestCase):
    def setUp(self):
        super(TestCreatePicksForm, self).setUp()
        self.user = User.objects.create(username='user')
        self.player = Player.objects.create(name='user', user=self.user)
        releaseDate = datetime.date.today()
        self.week = Week.objects.create(week=1)
        self.games = [Game.objects.create(appID=i, releaseDate=releaseDate) for i in range(1, 5)]
        for game in self.games:
            game.week = [self.week]
            game.save()

        self.validFormData = {
            'joker': self.games[0].appID,
            'pick1': self.games[1].appID,
            'pick2': self.games[2].appID,
            'pick3': self.games[3].appID
        }
        start = django.utils.timezone.now()
        end = start + datetime.timedelta(days=4)
        self.votingPeriod = VotingPeriod.objects.create(week=self.week, start=start, end=end)

    def test_emptyForm_IsInvalid(self):
        form = CreatePicksForm(votingPeriod=self.votingPeriod, user=self.user)
        self.assertFalse(form.is_valid())

    def test_formMustHaveVotingPeriod(self):
        with self.assertRaises(KeyError):
            CreatePicksForm(self.validFormData, user=self.user)

    def test_formMustHaveUser(self):
        with self.assertRaises(KeyError):
            CreatePicksForm(self.validFormData, votingPeriod=self.votingPeriod)

    def test_gamesMustBeUnique(self):
        formData = {
            'joker': self.games[0].appID,
            'pick1': self.games[0].appID,
            'pick2': self.games[0].appID,
            'pick3': self.games[0].appID
        }
        form = CreatePicksForm(formData, votingPeriod=self.votingPeriod, user=self.user)
        self.assertFalse(form.is_valid())

    def test_gamesMustExist(self):
        formData = self.validFormData
        for key in formData:
            formData[key] += 42
        form = CreatePicksForm(formData, votingPeriod=self.votingPeriod, user=self.user)
        self.assertFalse(form.is_valid())

    def test_gamesMustBeFromTheCurrentWeek(self):
        formData = self.validFormData
        week2 = Week.objects.create(week=2)
        game = Game.objects.create(appID=42, releaseDate=datetime.date.today() + datetime.timedelta(days=7))
        game.week = [week2]
        game.save()
        formData['joker'] = game.appID
        votingPeriod2 = VotingPeriod.objects.create(week=week2, start=self.votingPeriod.start + datetime.timedelta(days=14),
                                                    end=self.votingPeriod.end + datetime.timedelta(days=14))
        form = CreatePicksForm(formData, votingPeriod=votingPeriod2, user=self.user)
        self.assertFalse(form.is_valid())

    def test_gamesCanBeFromTheCurrentWeekAndAnotherWeek(self):
        formData = self.validFormData
        week2 = Week.objects.create(week=2)
        for game in Game.objects.all():
            game.week = [self.week, week2]
            game.save()
        votingPeriod2 = VotingPeriod.objects.create(week=week2,
                                                    start=self.votingPeriod.start + datetime.timedelta(days=14),
                                                    end=self.votingPeriod.end + datetime.timedelta(days=14))
        form = CreatePicksForm(formData, votingPeriod=votingPeriod2, user=self.user)
        self.assertTrue(form.is_valid())

    def test_disallowLapsedReleasesPickedInAPreviousWeek(self):
        formData = self.validFormData
        week2 = Week.objects.create(week=2)
        for game in Game.objects.all():
            game.week = [self.week, week2]
            game.save()
        Pick.objects.create(player=self.player, game=Game.objects.first(), week=self.week)
        votingPeriod2 = VotingPeriod.objects.create(week=week2,
                                                    start=self.votingPeriod.start + datetime.timedelta(days=14),
                                                    end=self.votingPeriod.end + datetime.timedelta(days=14))
        form = CreatePicksForm(formData, votingPeriod=votingPeriod2, user=self.user)
        self.assertFalse(form.is_valid(), form.errors)

    def test_ignorePreviousPicksFromOtherPlayers(self):
        formData = self.validFormData
        week2 = Week.objects.create(week=2)
        for game in Game.objects.all():
            game.week = [self.week, week2]
            game.save()
        user2 = User.objects.create(username='user2')
        player2 = Player.objects.create(name='user2', user=user2)
        Pick.objects.create(player=player2, game=Game.objects.first(), week=self.week)
        votingPeriod2 = VotingPeriod.objects.create(week=week2,
                                                    start=self.votingPeriod.start + datetime.timedelta(days=14),
                                                    end=self.votingPeriod.end + datetime.timedelta(days=14))
        form = CreatePicksForm(formData, votingPeriod=votingPeriod2, user=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_validFormData(self):
        form = CreatePicksForm(self.validFormData, votingPeriod=self.votingPeriod, user=self.user)
        self.assertTrue(form.is_valid(), form.errors)