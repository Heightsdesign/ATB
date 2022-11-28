from models import Strategy, Stats, Results


def scorer(stat):
    """Applies a score out of 30 to statistics of a strategy."""
    score = 0
    volume = stat.wins + stat.losses

    if 65 <= stat.win_ratio < 100:
        score += 5
    if 75 <= stat.win_ratio < 100:
        score += 5
    if 85 <= stat.win_ratio < 100:
        score += 5

    if 15 <= volume < 70:
        score += 5
    if 30 <= volume < 70:
        score += 5
    if 45 <= volume < 70:
        score += 5

    return {"score": score, "strat_id": stat.strategy.id}


def analyser(n):
    """Gets n best strategies ids (by score)"""

    scores = []
    stats = Stats.select()
    res = []
    for stat in stats:
        scores.append(scorer(stat))

    scores = sorted(scores, key=lambda x: x['score'], reverse=True)
    print(scores)
    for i in range(n):
        res.append(scores[i]["strat_id"])

    return res


print(analyser(3))









