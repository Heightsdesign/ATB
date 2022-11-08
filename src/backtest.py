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
                              14, 60, 40,
                              9, 26,
                              200,
                              200, 100)

        self.df = self.strat.create_strategy_df()
        self.rsf_vals = [4,3]

        # Setup string indexes
        self.macd_con = f"{self.strat.macd_fast}_{self.strat.macd_slow}_{self.strat.macd_fast}"
        self.macd = f"MACD_{self.macd_con}"
        self.macds = f"MACDs_{self.macd_con}"
        self.macdh = f"MACDh_{self.macd_con}"
        self.xa = f"RSI_14_A_{self.strat.xa}"
        self.xb = f"RSI_14_B_{self.strat.xb}"
        self.rsi_len = str(self.strat.rsi_length)
        self.ema = f"EMA_{self.strat.ema_length}"
        self.trend_win = self.strat.trend_line_win
        self.trend_lever = self.strat.trend_lever

    def add_cols(self, col_names):
        """Adds empty columns"""

        for col in col_names:
            self.df[col] = np.nan

        return self.df

    def simulate_df(self):

        self.add_cols(["sell", "buy", "sl", "tp"])
        # print(self.df.tail(20))

        positions = []

        for i in range(len(self.df)):

            """Buying position logic"""

            # if self.df.iloc[i][self.xb] == 1 and self.df.iloc[i - 1][self.xb] == 0:
            if self.df.iloc[i][self.macds] < self.df.iloc[i][self.macd] < 0:

                # if self.df.iloc[i][self.ema] > self.df.iloc[i]['Close']:
                if self.strat.get_angle_two_points(
                        self.df.iloc[i - self.trend_win][self.ema], self.df.iloc[i][self.ema]
                ) > 10:

                    self.df.iloc[i, self.df.columns.get_loc('buy')] = 1

                    sl = rsf(self.df, self.rsf_vals[0], self.rsf_vals[1], 0).find_strongest(self.df.iloc[i]['Close'], 3)
                    if sl:
                        self.df.iloc[i, self.df.columns.get_loc('sl')] = sl
                    else:
                        sl = rsf(self.df, self.rsf_vals[0] - 1, self.rsf_vals[1] - 1, 0).find_strongest(
                            self.df.iloc[i]['Close'])
                        self.df.iloc[i, self.df.columns.get_loc('sl')] = sl

                    tp = self.df.iloc[i]['Close'] + (self.df.iloc[i]['Close'] - sl) * 2
                    self.df.iloc[i, self.df.columns.get_loc('tp')] = tp

            """Selling position logic"""

            # if self.df.iloc[i][self.xa] == 1 and self.df.iloc[i - 1][self.xa] == 0:
            if self.df.iloc[i][self.macds] > self.df.iloc[i][self.macd] > 0:

                # if self.df.iloc[i][self.ema] < self.df.iloc[i]['Close']:
                if self.strat.get_angle_two_points(
                        self.df.iloc[i - self.trend_win][self.ema], self.df.iloc[i][self.ema]
                ) < -10:

                    self.df.iloc[i, self.df.columns.get_loc('sell')] = 1

                    sl = rsf(self.df, self.rsf_vals[0], self.rsf_vals[1], 1).find_strongest(self.df.iloc[i]['Close'], 3)
                    if sl:
                        self.df.iloc[i, self.df.columns.get_loc('sl')] = sl
                    else:
                        sl = rsf(self.df, self.rsf_vals[0] - 1, self.rsf_vals[1] - 1, 1).find_strongest(
                            self.df.iloc[i]['Close'], 3)
                        self.df.iloc[i, self.df.columns.get_loc('sl')] = sl

                    tp = self.df.iloc[i]['Close'] + (self.df.iloc[i]['Close'] - sl) * 2
                    self.df.iloc[i, self.df.columns.get_loc('tp')] = tp

        return self.df

    def simulate(self):

        self.df = self.simulate_df()
        return self.df


"""__________________________________________________________________________________________________________________"""

# print(Simulator().simulate_df().tail(650))
print(Simulator().simulate().tail(200))
