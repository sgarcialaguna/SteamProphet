import datetime

from dateutil import relativedelta
import pytz

from SteamProphet.apps.SteamProphet.models import Game


def computeGameScore(game):
    if not game.price:
        return 0
    players = max(0, game.players - game.playersVariance)
    score = players * game.price
    score = score - score % 1000
    return int(score)


def computePlayerScore(player):
    score = 0
    for pick in player.pick_set.all():
        gameScore = computePickScore(pick)
        score += gameScore
    return score


def computePickScore(pick):
    if pick.fallback:
        return 0
    gameScore = computeGameScore(pick.game)
    if pick.joker:
        gameScore *= 2
    return gameScore


def getCurrentWeek():
    if not Game.objects.exists():
        return 1
    tz = pytz.timezone('CET')
    berlin_now = datetime.datetime.now(tz)
    firstGame = Game.objects.order_by('releaseDate').exclude(releaseDate__isnull=True).first()
    fridayPrecedingFirstWeek = getPrecedingFriday(firstGame.releaseDate)
    referenceDateTime = datetime.datetime(year=fridayPrecedingFirstWeek.year, month=fridayPrecedingFirstWeek.month,
                                          day=fridayPrecedingFirstWeek.day, hour=19)
    referenceDateTime = tz.localize(referenceDateTime)
    return firstGame.week + int((berlin_now - referenceDateTime).days / 7)


def getPrecedingFriday(aDate):
    return aDate - datetime.timedelta(days=7) + relativedelta.relativedelta(weekday=relativedelta.FR)