from models import Strategy, Stats, Results


def del_losses():

    all_strats = Strategy.select()
    for strat in all_strats:
        print(strat.id)

        try:
            stat = Stats.get(strategy=strat.id)
            volume = stat.wins + stat.losses
            results = Results.select().join(Strategy).where(Strategy.id == strat.id)
            if stat.profit < 0.0 or volume < 10:
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


def del_unwanted(tick_file):

    indexes = []
    with open(tick_file, 'r') as f:
        for line in f:
            indexes.append(line.replace('\n', ''))
    strats = Strategy.select()

    for strat in strats:
        if strat.ticker not in indexes:
            stat = Stats.get(strategy=strat.id)
            results = Results.select().join(Strategy).where(Strategy.id == strat.id)

            stat.delete_instance()
            for res in results:

                res.delete_instance()
            strat.delete_instance()



def analyser(n):
    """Gets n best strategies ids (by score)"""

    stats = Stats.select()
    parsed_strats = []
    ticks = []
    res = []

    sorted_stats = sorted(stats, key=lambda x: x.win_ratio, reverse=True)

    for stat in sorted_stats:
        strat = Strategy.get(id=stat.strategy)
        volume = stat.wins + stat.losses
        parsed_strat = {
            "strat_id": stat.strategy,
            "win_ratio": stat.win_ratio,
            "ticker": strat.ticker,
            "volume": volume
        }
        parsed_strats.append(parsed_strat)

        if strat.ticker not in ticks:
            ticks.append(strat.ticker)

    for strat in parsed_strats:
        if strat["ticker"] in ticks:
            print(f'Ratio : {strat["win_ratio"]} / Volume : {strat["volume"]}')
            res.append(strat["strat_id"])
            ticks.remove(strat["ticker"])

    return res[:n]


"""__________________________________________________________________________________________________________________"""

# del_losses()
# del_unwanted('D:\Predictive Financial Tools\currency_tickers.txt')
# print(analyser(10))


