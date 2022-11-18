import yfinance as yf
from models import Strategy



class Fetcher:

    def __init__(self, market, period, interval):
        self.market = market
        self.period = period
        self.interval = interval

    def fetch_hist(self):
        ticker = yf.Ticker(self.market)
        data = ticker.history(period=self.period, interval=self.interval)
        return data


class MultiFetcher(Fetcher):

    def __init__(self, market, period, interval, market_list):
        super().__init__(market, period, interval)
        self.market_list = market_list

    def fetch_hist_list(self):

        data = yf.download(self.market_list, period=self.period, interval=self.interval)

        return data


def get_strategy(sid):
    strat = Strategy.get(id=sid)
    return strat.ticker


print(get_strategy(1))