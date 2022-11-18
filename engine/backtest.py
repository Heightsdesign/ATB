import pandas as pd
import pandas_ta as ta
import numpy as np
from datetime import datetime
import pprint
from strategies import Strat
from res_sup_finder import ResSupFinder as rsf
from models import Results

class Simulator:

    def __init__(self, strategy_id):

        self.strategy_id = strategy_id
        self.strat = Strat(self.strategy_id).obj
        self.tst = Strat(self.strategy_id)
        self.df = self.tst.create_strategy_df()

        # Choose resistance, support parameters.
        # The number of candles to consider before [0] and after [1] direction switch
        self.rsf_vals = [4, 3]

        # Setups string indexes
        self.macd_con = f"{self.strat.macd_fast}_{self.strat.macd_slow}_{self.strat.macd_fast}"
        self.macd = f"MACD_{self.macd_con}"
        self.macds = f"MACDs_{self.macd_con}"
        self.macdh = f"MACDh_{self.macd_con}"
        self.xa = f"RSI_14_A_{self.strat.rsi_high}"
        self.xb = f"RSI_14_B_{self.strat.rsi_low}"
        self.rsi_len = str(self.strat.rsi_length)
        self.ema = f"EMA_{self.strat.ema_length}"
        self.trend_win = self.strat.trend_line_win
        # self.trend_lever = self.strat.trend_lever

    def add_cols(self, col_names):
        """Adds empty columns"""

        for col in col_names:
            self.df[col] = np.nan

        return self.df

    def simulate_df(self):

        self.add_cols(["sell", "buy", "sl", "tp"])
        print(self.trend_win)
        print(self.ema)
        print(self.df.iloc[-1][self.ema])
        print(self.df.tail(150))

        for i in range(len(self.df)):

            """Buying position logic"""

            # if self.df.iloc[i][self.xb] == 1 and self.df.iloc[i - 1][self.xb] == 0:
            if self.df.iloc[i][self.macds] < self.df.iloc[i][self.macd] < 0\
                    and self.df.iloc[i][self.macdh] >= 0.0001:

                # if self.df.iloc[i][self.ema] > self.df.iloc[i]['Close']:

                # print(self.df.iloc[i - self.trend_win])
                # print(self.df.iloc[i])
                if i > self.strat.ema_length * 2:
                    if self.tst.get_angle_two_points(
                            self.df.iloc[i - self.trend_win][self.ema], self.df.iloc[i][self.ema]
                    ) > self.strat.trend_angle:

                        self.df.iloc[i, self.df.columns.get_loc('buy')] = 1

                        """Parameters to identify supports and resistances
                        to set sl"""
                        sl = rsf(self.df, self.rsf_vals[0], self.rsf_vals[1], 0).find_strongest(self.df.iloc[i]['Close'], 4)
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
                    and self.df.iloc[i][self.macdh] <= -0.0001:

                # if self.df.iloc[i][self.ema] < self.df.iloc[i]['Close']:
                print(self.df.iloc[i - self.trend_win])
                print(self.df.iloc[i])

                if i > self.strat.ema_length * 2:
                    if self.tst.get_angle_two_points(
                            self.df.iloc[i - self.trend_win][self.ema], self.df.iloc[i][self.ema]
                    ) < self.strat.trend_angle * -1:

                        self.df.iloc[i, self.df.columns.get_loc('sell')] = 1

                        """Parameters to identify supports and resistances
                        to set sl"""
                        sl = rsf(self.df, self.rsf_vals[0], self.rsf_vals[1], 1).find_strongest(self.df.iloc[i]['Close'], 4)
                        if sl:
                            self.df.iloc[i, self.df.columns.get_loc('sl')] = sl
                        else:
                            sl = rsf(self.df, self.rsf_vals[0] - 1, self.rsf_vals[1] - 1, 1).find_strongest(
                                self.df.iloc[i]['Close'], 4)
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

            # Code block make sure algo doesn't create position for
            # next 30 values.
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

            # Code block make sure algo doesn't create position for
            # next 30 values.
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
                        res = Results(
                            direction=1,
                            open_val=round(pos["open_val"], 9),
                            close_val=round(pos["tp"], 9),
                            win=1,
                            loss=0,
                            profit=round(profit, 9),
                            date=pos["date"],
                            strategy=self.strategy_id
                        )
                        # results.append(res)
                        res.save()
                        positions.remove(pos)

                    elif self.df.iloc[i]["Low"] <= pos["sl"]:
                        loss = pos["sl"] - pos["open_val"]
                        res = Results(
                            direction=1,
                            open_val=round(pos["open_val"], 9),
                            close_val=round(pos["tp"], 9),
                            win=0,
                            loss=1,
                            profit=round(loss, 9),
                            date=pos["date"],
                            strategy=self.strategy_id
                        )
                        # results.append(res)
                        res.save()
                        positions.remove(pos)

                if pos["direction"] == "sell":
                    if self.df.iloc[i]["Low"] <= pos["tp"]:
                        profit = pos['open_val'] - pos["tp"]
                        res = Results(
                            direction=0,
                            open_val=round(pos["open_val"], 9),
                            close_val=round(pos["tp"], 9),
                            win=1,
                            loss=0,
                            profit=round(profit, 9),
                            date=pos["date"],
                            strategy=self.strategy_id
                        )
                        # results.append(res)
                        res.save()
                        positions.remove(pos)

                    elif self.df.iloc[i]["High"] >= pos["sl"]:
                        loss = pos["open_val"] - pos["sl"]
                        res = Results(
                            direction=0,
                            open_val=round(pos["open_val"], 9),
                            close_val=round(pos["tp"], 9),
                            win=0,
                            loss=1,
                            profit=round(loss, 9),
                            date=pos["date"],
                            strategy=self.strategy_id
                        )
                        # results.append(res)
                        res.save()
                        positions.remove(pos)

        pprint.pprint(results)
        return results

    def make_stats(self):

        positions = Results.select().where(Results.strategy == self.strategy_id)
        num_positions = len(positions)
        num_wins = 0
        num_losses = 0
        total_profit = 0

        for pos in positions:
            if pos.win == True:
                num_wins += 1
            elif pos.loss == True:
                num_losses += 1
            total_profit += pos.profit

        win_ratio = num_wins / num_losses * 100

        res = {
            "num_positions": num_positions,
            "num_wins": num_wins,
            "num_losses": num_losses,
            "win_ratio" : win_ratio,
            "total_profit": total_profit
        }

        return res


"""__________________________________________________________________________________________________________________"""

# print(Simulator().simulate_df().tail(650))
print(Simulator(5).make_stats())
