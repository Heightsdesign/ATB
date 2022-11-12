import pandas as pd
import pandas_ta as ta
import numpy as np
from datetime import datetime
import pprint
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
            if self.df.iloc[i][self.macds] < self.df.iloc[i][self.macd] < 0\
                    and self.df.iloc[i][self.macdh] > 0.0001:

                # if self.df.iloc[i][self.ema] > self.df.iloc[i]['Close']:
                if self.strat.get_angle_two_points(
                        self.df.iloc[i - self.trend_win][self.ema], self.df.iloc[i][self.ema]
                ) > 10:

                    self.df.iloc[i, self.df.columns.get_loc('buy')] = 1

                    sl = rsf(self.df, self.rsf_vals[0], self.rsf_vals[1], 0).find_strongest(self.df.iloc[i]['Close'], 2)
                    if sl:
                        self.df.iloc[i, self.df.columns.get_loc('sl')] = sl
                    else:
                        sl = rsf(self.df, self.rsf_vals[0] - 1, self.rsf_vals[1] - 1, 0).find_strongest(
                            self.df.iloc[i]['Close'], 2)
                        self.df.iloc[i, self.df.columns.get_loc('sl')] = sl

                    tp = self.df.iloc[i]['Close'] + (self.df.iloc[i]['Close'] - sl) * 2
                    self.df.iloc[i, self.df.columns.get_loc('tp')] = tp

            """Selling position logic"""

            # if self.df.iloc[i][self.xa] == 1 and self.df.iloc[i - 1][self.xa] == 0:
            if self.df.iloc[i][self.macds] > self.df.iloc[i][self.macd] > 0\
                    and self.df.iloc[i][self.macdh] < -0.0001:

                # if self.df.iloc[i][self.ema] < self.df.iloc[i]['Close']:
                if self.strat.get_angle_two_points(
                        self.df.iloc[i - self.trend_win][self.ema], self.df.iloc[i][self.ema]
                ) < -10:

                    self.df.iloc[i, self.df.columns.get_loc('sell')] = 1

                    sl = rsf(self.df, self.rsf_vals[0], self.rsf_vals[1], 1).find_strongest(self.df.iloc[i]['Close'], 2)
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
        self.df = self.df.reset_index().rename(columns={"Datetime": "Date"})
        print(self.df.tail(200))
        num_position = 0
        positions = []
        results = []

        for i in range(len(self.df)):
            if self.df.iloc[i]['buy'] == 1:
                if i < len(self.df) - 30:
                    for close_idx in range(1, 30):
                        self.df.iloc[i + close_idx, self.df.columns.get_loc('buy')] = 0

                    num_position += 1
                    position = {
                        "idx": i,
                        "num_pos": num_position,
                        "date": self.df.iloc[i]["Date"],
                        "direction": "buy",
                        "open_val": self.df.iloc[i + 1]['Open'],
                        "sl": self.df.iloc[i]['sl'],
                        "tp": self.df.iloc[i]['tp'],
                    }
                    positions.append(position)

            if self.df.iloc[i]['sell'] == 1:
                if i < len(self.df) - 30:
                    for close_idx in range(1, 30):

                            self.df.iloc[i + close_idx, self.df.columns.get_loc('sell')] = 0

                    num_position += 1
                    position = {
                        "idx": i,
                        "num_pos": num_position,
                        "date": self.df.iloc[i]["Date"],
                        "direction": "sell",
                        "open_val": self.df.iloc[i + 1]['Open'],
                        "sl": self.df.iloc[i]['sl'],
                        "tp": self.df.iloc[i]['tp'],
                    }
                    positions.append(position)

            for pos in positions:
                if pos["direction"] == "buy":
                    if self.df.iloc[i]["High"] >= pos["tp"]:
                        profit = pos["tp"] - pos['open_val']
                        res = {
                            "idx": i,
                            "num_pos": pos["num_pos"],
                            "direction": pos["direction"],
                            "open_val": pos["open_val"],
                            "close_val": pos["tp"],
                            "win": 1,
                            "loss": 0,
                            "profit/loss": profit,
                            "date": pos["date"]
                        }
                        results.append(res)
                        positions.remove(pos)

                    elif self.df.iloc[i]["Low"] <= pos["sl"]:
                        loss = pos["sl"] - pos["open_val"]
                        res = {
                            "idx": i,
                            "num_pos": pos["num_pos"],
                            "direction": pos["direction"],
                            "open_val": pos["open_val"],
                            "close_val": pos["sl"],
                            "win": 0,
                            "loss": 1,
                            "profit/loss": loss,
                            "dat": pos["date"]
                        }
                        results.append(res)
                        positions.remove(pos)

                if pos["direction"] == "sell":
                    if self.df.iloc[i]["Low"] <= pos["tp"]:
                        profit = pos['open_val'] - pos["tp"]
                        res = {
                            "idx": i,
                            "num_pos": pos["num_pos"],
                            "direction": pos["direction"],
                            "open_val": pos["open_val"],
                            "close_val": pos["tp"],
                            "win": 1,
                            "loss": 0,
                            "profit/loss": profit,
                            "date": pos["date"]
                        }
                        results.append(res)
                        positions.remove(pos)

                    elif self.df.iloc[i]["High"] >= pos["sl"]:
                        loss = pos["open_val"] - pos["sl"]
                        res = {
                            "idx": i,
                            "num_pos": pos["num_pos"],
                            "direction": pos["direction"],
                            "open_val": pos["open_val"],
                            "close_val": pos["sl"],
                            "win": 0,
                            "loss": 1,
                            "profit/loss": loss,
                            "date": pos["date"]
                        }
                        results.append(res)
                        positions.remove(pos)
        pprint.pprint(results)
        return results

    def get_stats(self):

        results = self.simulate()
        num_positions = len(results)
        num_wins = 0
        num_losses = 0
        win_ratio = 0
        total_profit = 0



"""__________________________________________________________________________________________________________________"""

# print(Simulator().simulate_df().tail(650))
print(Simulator().simulate())
