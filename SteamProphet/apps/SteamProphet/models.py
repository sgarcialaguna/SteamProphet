from django.contrib.auth.models import User
from django.db import models


class Player(models.Model):
    name = models.CharField(unique=True, max_length=255)
    history = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User)

    def __str__(self):
        return self.name


class Game(models.Model):
    appID = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    releaseDate = models.DateField(null=True, blank=True)
    players = models.PositiveIntegerField(default=0)
    playersVariance = models.PositiveIntegerField(default=0)
    price = models.DecimalField(decimal_places=2, max_digits=6, default=0)
    week = models.PositiveIntegerField()
    matured = models.BooleanField(default=False)
    history = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name or str(self.appID)


class Pick(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    joker = models.BooleanField(default=False)
    fallback = models.BooleanField(default=False)

    class Meta:
        unique_together = ('player', 'game')

    def __str__(self):
        string = '{} picks {}'.format(self.player, self.game)
        if self.joker:
            string += ' (Joker)'
        elif self.fallback:
            string += ' (Fallback)'
        return string


class VotingPeriod(models.Model):
    week = models.PositiveSmallIntegerField(primary_key=True)
    start = models.DateTimeField()
    end = models.DateTimeField()