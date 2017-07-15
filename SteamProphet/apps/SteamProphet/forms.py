from django import forms
from django.core.exceptions import ValidationError

from SteamProphet.apps.SteamProphet import services
from SteamProphet.apps.SteamProphet.models import Game


class CreatePicksForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        eligibleGames = Game.objects.filter(week=services.getCurrentWeek())
        self.fields['joker'] = forms.ModelChoiceField(queryset=eligibleGames)
        self.fields['fallback'] = forms.ModelChoiceField(queryset=eligibleGames)
        self.fields['pick1'] = forms.ModelChoiceField(queryset=eligibleGames)
        self.fields['pick2'] = forms.ModelChoiceField(queryset=eligibleGames)

    def clean(self):
        cleaned_data = super().clean()
        values = cleaned_data.values()
        if len(set(values)) < len(values):
            raise ValidationError('Every pick needs to be unique.')