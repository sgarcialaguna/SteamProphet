from operator import attrgetter

from django.views.generic import DetailView, TemplateView

from SteamProphet.apps.SteamProphet import services
from SteamProphet.apps.SteamProphet.models import Game, Player


class GameDetailView(DetailView):
    model = Game


class PlayerDetailView(DetailView):
    model = Player

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player = context['object']
        player.score = services.computePlayerScore(player)
        picks = player.pick_set.all()
        for pick in picks:
            pick.score = services.computePickScore(pick)
        context['picks'] = picks
        return context


class PlayerListView(TemplateView):
    template_name = 'SteamProphet/player_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        players = Player.objects.all().prefetch_related('pick_set__game')
        for player in players:
            player.score = services.computePlayerScore(player)
        players = sorted(players, key=attrgetter('score'), reverse=True)
        context['players'] = players
        return context
