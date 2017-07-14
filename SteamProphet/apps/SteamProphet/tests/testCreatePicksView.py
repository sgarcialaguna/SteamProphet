from datetime import datetime

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from freezegun import freeze_time
import pytz

from ..views import CreatePicksView


class TestCreatePicksView(TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = User.objects.create_user('user')

    def test_userNeedsToBeAuthenticated_GET(self):
        request = self.factory.get('')
        request.user = AnonymousUser()
        response = CreatePicksView.as_view()(request)
        # TODO: use assert_redirects with proper view name
        self.assertEqual(response.status_code, 302)

    def test_userNeedsToBeAuthenticated_POST(self):
        request = self.factory.post('')
        request.user = AnonymousUser()
        response = CreatePicksView.as_view()(request)
        # TODO: use assert_redirects with proper view name
        self.assertEqual(response.status_code, 302)

    def test_view_is_inaccessible_before_friday_1900_CEST(self):
        self.assertViewIsInaccessible(year=2017, month=7, day=14, hour=18, minute=59, second=59)

    def test_view_is_accessible_between_monday_and_friday_CEST(self):
        self.assertViewIsAccessible(year=2017, month=7, day=14, hour=19)
        self.assertViewIsAccessible(year=2017, month=7, day=15, hour=19)
        self.assertViewIsAccessible(year=2017, month=7, day=16, hour=19)
        self.assertViewIsAccessible(year=2017, month=7, day=17, hour=18, minute=59, second=59)

    def test_view_is_inaccessible_after_monday_1900_CEST(self):
        self.assertViewIsInaccessible(year=2017, month=7, day=17, hour=19)

    def test_view_handles_dst_switch_correctly(self):
        # DST ends on Sunday, Oct 29th
        self.assertViewIsAccessible(year=2017, month=10, day=27, hour=19)
        self.assertViewIsAccessible(year=2017, month=10, day=30, hour=18)
        self.assertViewIsInaccessible(year=2017, month=10, day=30, hour=19)

        # DST starts again on Sunday, Mar 25th 2018
        self.assertViewIsAccessible(year=2018, month=3, day=23, hour=19)
        self.assertViewIsAccessible(year=2018, month=3, day=26, hour=18)
        self.assertViewIsInaccessible(year=2018, month=3, day=26, hour=19)

    def assertViewIsAccessible(self, **kwargs):
        tz = pytz.timezone('CET')
        dt = datetime(**kwargs)
        dt = tz.localize(dt)
        with freeze_time(dt):
            request = self.factory.get('')
            request.user = self.user
            response = CreatePicksView.as_view()(request)
            self.assertContains(response, 'YEAH')

    def assertViewIsInaccessible(self, **kwargs):
        tz = pytz.timezone('CET')
        dt = datetime(**kwargs)
        dt = tz.localize(dt)
        with freeze_time(dt):
            get_request = self.factory.get('')
            get_request.user = self.user
            get_response = CreatePicksView.as_view()(get_request)

            post_request = self.factory.post('')
            post_request.user = self.user
            post_response = CreatePicksView.as_view()(post_request)

            self.assertContains(get_response, 'NOPE')
            self.assertContains(post_response, 'NOPE')
