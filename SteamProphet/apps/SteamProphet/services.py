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
    return 1