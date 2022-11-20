import pandas as pd
import pandas_ta as ta
import numpy as np
from datetime import datetime
import pprint
from strategies import Strat
from res_sup_finder import ResSupFinder as rsf
from models import Results, Stats, Strategy


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
        self.sma = f"EMA_{self.strat.sma_length}"
        self.trend_win = self.strat.trend_line_win

    def add_cols(self, col_names):
        """Adds empty columns"""

        for col in col_names:
            self.df[col] = np.nan

        return self.df

    def rsi_buy_condition(self, i):
        if self.df.iloc[i][self.xb] == 1 and self.df.iloc[i - 1][self.xb] == 0:
            return True

    def macd_buy_condition(self, i):
        if self.df.iloc[i][self.macds] < self.df.iloc[i][self.macd] < 0 \
                and self.df.iloc[i][self.macdh] >= 0.0001:
            return True

    def ema_trend_buy_condition(self, i):
        if i > self.strat.ema_length * 2:
            if self.tst.get_angle_two_points(
                    self.df.iloc[i - self.trend_win][self.ema], self.df.iloc[i][self.ema]
            ) > self.strat.trend_angle:
                return True

    def sma_trend_buy_condition(self, i):
        if i > self.strat.sma_length * 2:
            if self.tst.get_angle_two_points(
                    self.df.iloc[i - self.trend_win][self.sma], self.df.iloc[i][self.sma]
            ) > self.strat.trend_angle:
                return True

    def rsi_sell_condition(self, i):
        if self.df.iloc[i][self.xa] == 1 and self.df.iloc[i - 1][self.xa] == 0
            return True

    def macd_sell_condition(self, i):
        if self.df.iloc[i][self.macds] > self.df.iloc[i][self.macd] > 0 \
                and self.df.iloc[i][self.macdh] <= -0.0001:
            return True

    def ema_trend_sell_condition(self, i):
        if i > self.strat.ema_length * 2:
            if self.tst.get_angle_two_points(
                    self.df.iloc[i - self.trend_win][self.ema], self.df.iloc[i][self.ema]
            ) < self.strat.trend_angle * -1:
                return True

    def sma_trend_sell_condition(self, i):
        if i > self.strat.sma_length * 2:
            if self.tst.get_angle_two_points(
                    self.df.iloc[i - self.trend_win][self.sma], self.df.iloc[i][self.sma]
            ) < self.strat.trend_angle * -1:
                return True

    def conditions_getter(self):

        conditions = []
        if self.strat.rsi_high:
            conditions.append("rsi")
        elif self.strat.macd_fast:
            conditions.append("macd")
        elif self.strat.ema_length:
            conditions.append("ema")
        elif self.strat.sma_length:
            conditions.append("sma")
        elif self.strat.trend_line_win:
            conditions.append("tl")

        return conditions
    
    def simulate_df(self):

        self.add_cols(["sell", "buy", "sl", "tp"])

        for i in range(len(self.df)):

            """Buying position logic"""

            # UNCOMMENT TO USE RSI
            # if self.df.iloc[i][self.xb] == 1 and self.df.iloc[i - 1][self.xb] == 0:

            # UNCOMMENT TO USE MACD
            if self.df.iloc[i][self.macds] < self.df.iloc[i][self.macd] < 0\
                    and self.df.iloc[i][self.macdh] >= 0.0001:

                # UNCOMMENT TO USE TREND EMA TREND ANGLE
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

            # UNCOMMENT TO USE RSI
            # if self.df.iloc[i][self.xa] == 1 and self.df.iloc[i - 1][self.xa] == 0:

            # UNCOMMENT TO USE MACD
            if self.df.iloc[i][self.macds] > self.df.iloc[i][self.macd] > 0\
                    and self.df.iloc[i][self.macdh] <= -0.0001:

                # UNCOMMENT TO USE TREND EMA TREND ANGLE
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
                    print(position)
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
                    print(position)
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

        # pprint.pprint(results)
        return results

    def make_stats(self):

        positions = Results.select().where(Results.strategy == self.strategy_id)

        num_positions = len(positions)
        num_wins = 0
        num_losses = 0
        total_profit = 0

        for pos in positions:
            if pos.win:
                num_wins += 1
            elif pos.loss:
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

        stats = Stats(
            start_time=datetime.now(),
            win_ratio=win_ratio,
            wins=num_wins,
            losses=num_losses,
            profit=total_profit,
            strategy=self.strategy_id,
        )
        stats.save()

        return res


"""__________________________________________________________________________________________________________________"""

# print(Simulator(2).simulate())
# print(Simulator(2).make_stats())

"""__________________________________________________________________________________________________________________"""


class Launcher:
    def __init__(self, indexes, params):

        # Indexes should be a list of tickers like "EURUSD=X"
        self.indexes = indexes
        # Parameters should be a dict of the parameters to use.
        self.params = params

    def name_creator(self, ticker):
        res=f'{ticker}-{self.params["period"]}-{self.params["interval"]}'
        if self.params["rsi_length"]:
            res += f'-rsi-{self.params["rsi_length"]}-{self.params["rsi_high"]}-{self.params["rsi_low"]}'
        if self.params["macd_fast"]:
            res +=f'-macd-{self.params["macd_fast"]}-{self.params["macd_slow"]}'
        if self.params["ema_length"]:
            res +=f'-ema-{self.params["ema_length"]}'
        if self.params["sma_length"]:
            res += f'-sma-{self.params["sma_length"]}'
        if self.params["trend_line_win"]:
            res += f'-tl-{self.params["trend_line_win"]}-{self.params["trend_lever"]}-{self.params["trend_angle"]}'

        return res

    def check_duplicates(self, ticker):

        strat_name = self.name_creator(ticker)
        strat_exists = Strategy.select().where(Strategy.name == strat_name)
        if strat_exists:
            return True
        else:
            return False

    def strategies_creator(self):
        strat_names= []
        for ticker in self.indexes:
            if not self.check_duplicates(ticker):
                strat = Strategy(
                    name=self.name_creator(ticker),
                    ticker=ticker,
                    period=self.params["period"],
                    interval=self.params["interval"],
                    rsi_length=self.params["rsi_length"],
                    rsi_high=self.params["rsi_high"],
                    rsi_low=self.params["rsi_low"],
                    macd_fast=self.params["macd_fast"],
                    macd_slow=self.params["macd_slow"],
                    ema_length=self.params["ema_length"],
                    sma_length=self.params["sma_length"],
                    trend_line_win=self.params["trend_line_win"],
                    trend_lever=self.params["trend_lever"],
                    trend_angle=self.params["trend_angle"],
                    description=self.params["description"],
                )
                strat.save()
                strat_names.append(self.name_creator(ticker))
        print(strat_names)
        return strat_names

    def launch(self):
        strat_names = self.strategies_creator()

        for name in strat_names:
            strat = Strategy.get(name=name)
            print(strat.id, strat.ticker)
            Simulator(strat.id).simulate()
            Simulator(strat.id).make_stats()


"""__________________________________________________________________________________________________________________"""

launcher = Launcher(
    ["msft", "aapl", "tsla"],
    {
        "period": "50d",
        "interval": "5m",
        "rsi_length": None,
        "rsi_high": None,
        "rsi_low": None,
        "macd_fast": 9,
        "macd_slow": 26,
        "ema_length": 200,
        "sma_length": None,
        "trend_line_win": 100,
        "trend_lever": 1,
        "trend_angle": 16,
        "description": "res:sup finder strength = 4"
    }
)

# print(launcher.strategies_creator())
print(launcher.launch())


"""__________________________________________________________________________________________________________________"""
