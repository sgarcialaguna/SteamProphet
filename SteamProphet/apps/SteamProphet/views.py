from operator import attrgetter

from django.views.generic import DetailView, ListView

from SteamProphet.apps.SteamProphet import services
from SteamProphet.apps.SteamProphet.models import Game, Player


class GameDetailView(DetailView):
    model = Game

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = context['object']
        game.score = services.computeGameScore(game)
        game.steamspyURL = 'https://steamspy.com/app/{}/'.format(game.appID)
        game.steamURL = 'https://store.steampowered.com/app/{}/'.format(game.appID)
        game.ownersLowerBound = game.owners - game.ownersVariance
        game.unroundedScore = game.price * game.ownersLowerBound
        return context


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


class PlayerListView(ListView):
    model = Player

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        players = context['player_list']
        for player in players:
            player.score = services.computePlayerScore(player)
        context['player_list'] = sorted(players, key=attrgetter('score'), reverse=True)
        return context


class GameListView(ListView):
    model = Game

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        games = context['game_list']
        for game in games:
            game.score = services.computeGameScore(game)
        context['game_list'] = sorted(games, key=attrgetter('score'), reverse=True)
        return context



