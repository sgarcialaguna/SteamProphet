import itertools
from collections import OrderedDict
from datetime import datetime
from operator import attrgetter

import pytz
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView, DetailView, ListView, FormView

from SteamProphet.apps.SteamProphet import services, forms
from SteamProphet.apps.SteamProphet.models import Game, Pick, Player


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
        grouped_picks = {k: list(v) for k, v in itertools.groupby(picks, attrgetter('game.week'))}
        grouped_picks = OrderedDict(sorted(grouped_picks.items(), reverse=True))
        context['groupedPicks'] = grouped_picks
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
    template_name = 'SteamProphet/game_list.html'

    def get_queryset(self):
        # Perform the computation of score in SQL so the list comes out correctly sorted for pagination.
        # Floor is not supported by Django so we need to use raw SQL
        return list(Game.objects.raw(
            'SELECT *, FLOOR("SteamProphet_game1"."price" * "playersLowerBound" / 1000) * 1000 AS "score"'
            ' FROM (SELECT *, GREATEST(0, "players" - "playersVariance") AS "playersLowerBound"'
            ' FROM "SteamProphet_game") AS "SteamProphet_game1" ORDER BY "score" DESC, "releaseDate" ASC;'))


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


class CreatePicksView(FormView):
    form_class = forms.CreatePicksForm
    template_name = 'SteamProphet/create_picks.html'
    success_url = reverse_lazy('player_list')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        tz = pytz.timezone('CET')
        berlin_now = datetime.now(tz)
        if berlin_now.isoweekday() not in [5, 6, 7, 1]:  # Friday through Monday
            return HttpResponse('You cannot enter your picks at this time.', status=400)
        if berlin_now.isoweekday() == 5 and berlin_now.hour < 19:  # Friday
            return HttpResponse('You cannot enter your picks at this time.', status=400)
        if berlin_now.isoweekday() == 1 and berlin_now.hour >= 19:  # Monday
            return HttpResponse('You cannot enter your picks at this time.', status=400)
        return super().dispatch(request, *args, **kwargs)
