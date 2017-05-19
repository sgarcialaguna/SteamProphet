from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.PlayerListView.as_view(), name='player_list'),
    url(r'^game/(?P<pk>\d+)/$', views.GameDetailView.as_view(), name='game'),
    url(r'^player/(?P<pk>\d+)/$', views.PlayerDetailView.as_view(), name='player'),
]
