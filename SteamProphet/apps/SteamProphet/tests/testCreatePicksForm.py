from django.contrib.auth.models import User
from django.test import TestCase

from SteamProphet.apps.SteamProphet import services
from SteamProphet.apps.SteamProphet.models import Player, Game

from ..forms import CreatePicksForm


class TestCreatePicksForm(TestCase):
    def setUp(self):
        super(TestCreatePicksForm, self).setUp()
        self.user = User.objects.create(username='user')
        self.player = Player.objects.create(name='user')
        #self.userProfile = UserProfile.objects.create(user=self.user, player=self.player)
        self.games = [Game.objects.create(appID=i, week=services.getCurrentWeek()) for i in range(1, 5)]
        self.validFormData = {
            'joker': self.games[0].appID,
            'fallback': self.games[1].appID,
            'pick1': self.games[2].appID,
            'pick2': self.games[3].appID
        }

    def test_emptyForm_IsInvalid(self):
        form = CreatePicksForm()
        self.assertFalse(form.is_valid())

    # def test_formWithoutUser_IsInvalid(self):
    #     form = CreatePicksForm(data={'a': 'b'})
    #     self.assertFalse(form.is_valid())

    def test_gamesMustBeUnique(self):
        formData = {
            'joker': self.games[0].appID,
            'fallback': self.games[0].appID,
            'pick1': self.games[0].appID,
            'pick2': self.games[0].appID
        }
        form = CreatePicksForm(formData)
        self.assertFalse(form.is_valid())

    def test_gamesMustExist(self):
        formData = self.validFormData
        for key in formData:
            formData[key] += 42
        form = CreatePicksForm(formData)
        self.assertFalse(form.is_valid())

    def test_gamesMustBeFromTheCurrentWeek(self):
        formData = self.validFormData
        Game.objects.create(appID=42, week=2)
        formData['joker'] = 42
        form = CreatePicksForm(formData)
        self.assertFalse(form.is_valid())

    def test_validFormData(self):
        form = CreatePicksForm(self.validFormData)
        self.assertTrue(form.is_valid(), form.errors)