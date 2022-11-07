import pandas as pd
import pandas_ta as ta
import numpy as np
from strategies import Strategy
from res_sup_finder import ResSupFinder as rsf

class Simulator:

    def __init__(self):

        """
        strategy parameters in order :
        (ticker, period, interval,
        rsi_length, rsi_high, rsi_low,
        macd_fast, macd_slow,
        ema_length,
        trend_line_window, # number of candles to consider
        trend_lever, # change accordingly to average ticker shift)
        """

        self.strat = Strategy("EURUSD=X", "5d", "5m",
                        14, 65, 35,
                        9, 26,
                        200,
                        200, 100)

        self.df = self.strat.create_strategy_df()

        # Setup
        self.macd_con = f"{self.strat.macd_fast}_{self.strat.macd_slow}_{self.strat.macd_fast}"
        self.xa = str(self.strat.xa)
        self.xb = str(self.strat.xb)
        self.rsi_len = str(self.strat.rsi_length)
        self.ema_len = str(self.strat.ema_length)

    def add_cols(self, col_names):
        """Adds empty columns"""

        for col in col_names:
            self.df[col] = np.nan

        return self.df

    def simulate(self):

        self.add_cols(["sell", "buy", "sl", "tp"])

        positions = []

        for i in range(len(self.df)):
            if self.df[i]['RSI_14_B_'+self.xb] == 1 and self.df[i-1]['RSI_14_B_' + self.xb] == 0:
                if self.df[i]['MACDs_'+self.macd_con] < self.df[i]['MACD_'+self.macd_con] < 0:
                    if self.df[i]['EMA_'+self.ema_len] > self.df[i]['Close'] and self.strat.get_trend_line_angle() > 20:
                        self.df[i]['buy'] = 1
                        sl = rsf(self.df, 4, 3, 0).find_closest(self.df[i]['Close'])
                        self.df[i]['sl'] = sl
                        tp = self.df[i]['Close'] + (self.df[i]['Close'] - sl) * 2
                        self.df[i]['tp'] = tp

        return self.df


"""__________________________________________________________________________________________________________________"""


