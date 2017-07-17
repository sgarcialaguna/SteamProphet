import datetime

import django
from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase

from SteamProphet.apps.SteamProphet.models import VotingPeriod
from ..views import CreatePicksView


class TestCreatePicksView(TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user('user')

    def test_userNeedsToBeAuthenticated_GET(self):
        request = self.factory.get('')
        request.user = AnonymousUser()
        with self.assertRaises(PermissionDenied):
            CreatePicksView.as_view()(request)

    def test_userNeedsToBeAuthenticated_POST(self):
        request = self.factory.post('')
        request.user = AnonymousUser()
        with self.assertRaises(PermissionDenied):
            CreatePicksView.as_view()(request)

    def test_view_is_inaccessible_if_there_is_no_voting_period(self):
        self.assertViewIsInaccessible()

    def test_view_is_inaccessible_before_voting_period(self):
        now = django.utils.timezone.now()
        start = now + datetime.timedelta(days=10)
        end = start + datetime.timedelta(days=10)
        VotingPeriod.objects.create(week=1, start=start, end=end)
        self.assertViewIsInaccessible()

    def test_view_is_inaccessible_after_voting_period(self):
        now = django.utils.timezone.now()
        start = now - datetime.timedelta(days=10)
        end = start + datetime.timedelta(days=5)
        VotingPeriod.objects.create(week=1, start=start, end=end)
        self.assertViewIsInaccessible()

    def test_view_is_accessible_during_voting_period(self):
        now = django.utils.timezone.now()
        start = now - datetime.timedelta(days=10)
        end = now + datetime.timedelta(days=10)
        VotingPeriod.objects.create(week=1, start=start, end=end)
        self.assertViewIsAccessible()

    def assertViewIsAccessible(self):
        request = self.factory.get('')
        request.user = self.user
        response = CreatePicksView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def assertViewIsInaccessible(self):
        get_request = self.factory.get('')
        get_request.user = self.user
        get_response = CreatePicksView.as_view()(get_request)

        post_request = self.factory.post('')
        post_request.user = self.user
        post_response = CreatePicksView.as_view()(post_request)

        self.assertEqual(get_response.status_code, 400)
        self.assertEqual(post_response.status_code, 400)
