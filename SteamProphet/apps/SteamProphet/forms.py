from django import forms
from django.core.exceptions import ValidationError

from SteamProphet.apps.SteamProphet.models import Game, Player, Pick


class CreatePicksForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.votingPeriod = kwargs.pop('votingPeriod')
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        picks = Pick.objects.filter(player__user=self.user, week=self.votingPeriod.week)
        jokerPick = picks.filter(joker=True).first()
        joker = jokerPick.game if jokerPick else None

        regularPicks = picks.exclude(joker=True)
        pick1 = regularPicks[0].game if len(regularPicks) > 0 else None
        pick2 = regularPicks[1].game if len(regularPicks) > 1 else None
        pick3 = regularPicks[2].game if len(regularPicks) > 2 else None

        eligibleGames = Game.objects.filter(week=self.votingPeriod.week)

        self.fields['joker'] = forms.ModelChoiceField(queryset=eligibleGames,
                                                      widget=forms.Select(attrs={'class': 'form-control'}),
                                                      initial=joker)
        self.fields['pick1'] = forms.ModelChoiceField(queryset=eligibleGames,
                                                      widget=forms.Select(attrs={'class': 'form-control'}),
                                                      initial=pick1)
        self.fields['pick2'] = forms.ModelChoiceField(queryset=eligibleGames,
                                                      widget=forms.Select(attrs={'class': 'form-control'}),
                                                      initial=pick2)
        self.fields['pick3'] = forms.ModelChoiceField(queryset=eligibleGames,
                                                      widget=forms.Select(attrs={'class': 'form-control'}),
                                                      initial=pick3)

    def clean(self):
        if self.votingPeriod is None:
            raise ValidationError('Voted outside of voting period.')
        cleaned_data = super().clean()
        values = cleaned_data.values()
        if len(set(values)) < len(values):
            raise ValidationError('Every pick needs to be unique.')


class PlayerProfileForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.player = kwargs.pop('player')
        super().__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(initial=self.player.name,
                                              max_length=150, required=True,
                                              widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_name(self):
        if Player.objects.filter(name=self.cleaned_data['name']).exists() and \
                Player.objects.get(name=self.cleaned_data['name']) != self.player:
            raise ValidationError('That name is already in use.')
        return self.cleaned_data['name']