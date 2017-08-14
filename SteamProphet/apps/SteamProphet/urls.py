from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.PlayerListView.as_view(), name='player_list'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^privacy/$', views.PrivacyView.as_view(), name='privacy'),
    url(r'^games/$', views.GameListView.as_view(), name='games_list'),
    url(r'^game/(?P<pk>\d+)/$', views.GameDetailView.as_view(), name='game'),
    url(r'^player/(?P<pk>\d+)/$', views.PlayerDetailView.as_view(), name='player'),
    url(r'^delete_game/(?P<pk>\d+)/$', views.DeleteGameView.as_view(), name='delete_game'),
    url(r'^create_picks/$', views.CreatePicksView.as_view(), name='create_picks'),
    url(r'^player_profile/$', views.PlayerProfileView.as_view(), name='player_profile'),
    url(r'^pick_overview/$', views.PickOverviewView.as_view(), name='pick_overview'),
    url(r'^pick_overview/(?P<week>\d)/$', views.PickOverviewByWeekView.as_view(), name='pick_overview_by_week')
]
