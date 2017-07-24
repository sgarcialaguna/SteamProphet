from django.contrib.auth.models import User
from django.db import models


class Player(models.Model):
    name = models.CharField(unique=True, max_length=255)
    history = models.TextField(blank=True, null=True)
    user = models.OneToOneField(User)

    def __str__(self):
        return self.name


class Week(models.Model):
    week = models.PositiveSmallIntegerField(primary_key=True)

    def __str__(self):
        return 'Week {}'.format(self.week)


class Game(models.Model):
    appID = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    releaseDate = models.DateField(null=True, blank=True)
    players = models.PositiveIntegerField(default=0)
    playersVariance = models.PositiveIntegerField(default=0)
    price = models.DecimalField(decimal_places=2, max_digits=6, default=0)
    week = models.ManyToManyField(Week)
    matured = models.BooleanField(default=False)
    history = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name or str(self.appID)

    def weeks(self):
        return [week.week for week in self.week.all()]


class Pick(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    joker = models.BooleanField(default=False)
    fallback = models.BooleanField(default=False)
    week = models.ForeignKey(Week)

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
    week = models.ForeignKey(Week)
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self):
        return 'Voting Period {} : {} - {}'.format(self.week, self.start, self.end)