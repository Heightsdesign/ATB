from models import Strategy, Stats, Results


def del_losses():

    all_strats = Strategy.select()
    for strat in all_strats:
        print(strat.id)

        try:
            stat = Stats.get(strategy=strat.id)
            results = Results.select().join(Strategy).where(Strategy.id == strat.id)
            if stat.profit < 0.0:
                stat.delete_instance()
                for res in results:
                    res.delete_instance()
                strat.delete_instance()

        except:
            results = Results.select().join(Strategy).where(Strategy.id == strat.id)
            print(results)
            if results:
                for res in results:
                    res.delete_instance()

            strat.delete_instance()
            continue


def scorer(stat):
    """Applies a score out of 20 to statistics of a strategy."""
    score = 0
    volume = stat.wins + stat.losses
    if volume > 10:
        if 55 <= stat.win_ratio < 100:
            score += 5
        if 65 <= stat.win_ratio < 100:
            score += 5
        if 75 <= stat.win_ratio < 100:
            score += 5
        if 85 <= stat.win_ratio < 100:
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
    for i in range(n):
        res.append(scores[i]["strat_id"])

    print(res)
    return res


del_losses()








