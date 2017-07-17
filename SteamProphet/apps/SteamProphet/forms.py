from django import forms
from django.core.exceptions import ValidationError

from SteamProphet.apps.SteamProphet.models import Game


class CreatePicksForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.votingPeriod = kwargs.pop('votingPeriod', None)
        eligibleGames = Game.objects.filter(week=self.votingPeriod)
        super().__init__(*args, **kwargs)
        self.fields['joker'] = forms.ModelChoiceField(queryset=eligibleGames,
                                                      widget=forms.Select(attrs={'class': 'form-control'}))
        self.fields['pick1'] = forms.ModelChoiceField(queryset=eligibleGames,
                                                      widget=forms.Select(attrs={'class': 'form-control'}))
        self.fields['pick2'] = forms.ModelChoiceField(queryset=eligibleGames,
                                                      widget=forms.Select(attrs={'class': 'form-control'}))
        self.fields['pick3'] = forms.ModelChoiceField(queryset=eligibleGames,
                                                      widget=forms.Select(attrs={'class': 'form-control'}))

    def clean(self):
        if self.votingPeriod is None:
            raise ValidationError('Voted outside of voting period.')
        cleaned_data = super().clean()
        values = cleaned_data.values()
        if len(set(values)) < len(values):
            raise ValidationError('Every pick needs to be unique.')