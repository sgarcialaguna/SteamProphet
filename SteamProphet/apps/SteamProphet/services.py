def computeGameScore(game):
    if not game.price:
        return 0
    owners = max(0, game.owners - game.ownersVariance)
    score = owners * game.price
    score = score - score % 1000
    return int(score)


def computePlayerScore(player):
    score = 0
    for pick in player.pick_set.all():
        gameScore = computeGameScore(pick.game)
        if pick.joker:
            gameScore *= 2
        score += gameScore
    return score