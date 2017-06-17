from operator import attrgetter

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, DeleteView

from SteamProphet.apps.SteamProphet import services
from SteamProphet.apps.SteamProphet.models import Game, Player, Pick


class GameDetailView(DetailView):
    model = Game

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = context['object']
        game.score = services.computeGameScore(game)
        game.steamspyURL = 'https://steamspy.com/app/{}/'.format(game.appID)
        game.steamURL = 'https://store.steampowered.com/app/{}/'.format(game.appID)
        game.playersLowerBound = max(0, game.players - game.playersVariance)
        game.unroundedScore = game.price * game.playersLowerBound
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
    queryset = Player.objects.all().prefetch_related('pick_set__game')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        players = context['player_list']
        for player in players:
            player.score = services.computePlayerScore(player)
        context['player_list'] = sorted(players, key=attrgetter('score'), reverse=True)
        return context


class GameListView(ListView):
    model = Game
    queryset = Game.objects.order_by('releaseDate')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        games = context['game_list']
        for game in games:
            game.playersLowerBound = max(0, game.players - game.playersVariance)
            game.score = services.computeGameScore(game)
        context['game_list'] = sorted(games, key=attrgetter('score'), reverse=True)
        return context


class DeleteGameView(DeleteView):
    model = Game

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        game = get_object_or_404(Game, pk=kwargs['pk'])
        lines = []
        for pick in game.pick_set.all():
            if pick.fallback:
                lines.append('{} picked {} as their fallback game.'.format(pick.player.name, pick.game.name))
                continue
            line = '{} picked {}.'.format(pick.player.name, pick.game.name)
            matchingFallback = Pick.objects.filter(game__week=game.week, player=pick.player, fallback=True).first()
            if matchingFallback:
                matchingFallback.fallback = False
                matchingFallback.save()
                line += ' {} becomes a regular pick.'.format(matchingFallback.game.name)
            else:
                line += ' They have no available fallback.'
            lines.append(line)
        game.delete()
        return render(request, 'SteamProphet/game_deleted.html', {'game': game, 'lines': lines})