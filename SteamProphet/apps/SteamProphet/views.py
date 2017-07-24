import itertools
from collections import OrderedDict
from operator import attrgetter

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView, DetailView, FormView, ListView, TemplateView

from SteamProphet.apps.SteamProphet import forms, services
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
        picks = player.pick_set.order_by('-week').all()
        for pick in picks:
            pick.score = services.computePickScore(pick)
        grouped_picks = {k: list(v) for k, v in itertools.groupby(picks, attrgetter('week.week'))}
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
            player.scoreFromMaturedGames = services.computePlayerScore(player, onlyMaturedGames=True)
            player.scoreFromInFlightGames = player.score - player.scoreFromMaturedGames
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
            matchingFallback = Pick.objects.filter(week=pick.week, player=pick.player, fallback=True).first()
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
    # TODO: Handle lapsed releases from a previous voting period
    form_class = forms.CreatePicksForm
    template_name = 'SteamProphet/create_picks.html'
    success_url = reverse_lazy('player_list')

    def get_form_kwargs(self):
        kwargs = super(CreatePicksView, self).get_form_kwargs()
        kwargs.update({
            'votingPeriod': self.currentVotingPeriod,
            'user': self.request.user
        })
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('login')

        self.currentVotingPeriod = services.getCurrentVotingPeriod()
        if self.currentVotingPeriod is None:
            return render(self.request, self.template_name,
                          context={'errorMessage': 'You cannot enter your picks at this time'},
                          status=400)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        player = Player.objects.get_or_create(user=self.request.user, defaults={'name': self.request.user.username})[0]
        Pick.objects.filter(week=self.currentVotingPeriod, player=player).delete()
        Pick.objects.create(week=self.currentVotingPeriod, player=player, joker=True, game=form.cleaned_data['joker'])
        Pick.objects.create(week=self.currentVotingPeriod, player=player, game=form.cleaned_data['pick1'])
        Pick.objects.create(week=self.currentVotingPeriod, player=player, game=form.cleaned_data['pick2'])
        Pick.objects.create(week=self.currentVotingPeriod, player=player, game=form.cleaned_data['pick3'])
        return super(CreatePicksView, self).form_valid(form)


class PlayerProfileView(FormView):
    form_class = forms.PlayerProfileForm
    template_name = 'SteamProphet/player_profile.html'
    success_url = reverse_lazy('player_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'player': self.request.user.player
        })
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect(reverse('login'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        player = self.request.user.player
        player.name = form.cleaned_data['name']
        player.save()
        return super().form_valid(form)


class LoginView(TemplateView):
    template_name = 'SteamProphet/login.html'


class PrivacyView(TemplateView):
    template_name = 'SteamProphet/privacy.html'
