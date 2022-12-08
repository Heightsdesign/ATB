import pandas as pd
import pandas_ta as ta
import numpy as np
from datetime import datetime
from decimal import Decimal
from strategies import Strat
from res_sup_finder import ResSupFinder as rsf
from models import Results, Stats, Strategy


class Simulator:

    """The simulator object simulates a given strategy
    created in the database and takes in its id as argument.
    The simulator is build like a toolbox with the conditions
    being the tools. You can easily create new ones by :

    1. Creating the needed argument the db for the Strategy model.
    2. inserting that data in Strat.create_df() method.
    3. Setting its string index. ** optional
    4. Create the condition as a simulator method.
    5. Insert condition in condition appliers"""

    def __init__(self, strategy_id):

        self.strategy_id = strategy_id

        self.tst = Strat(self.strategy_id)
        self.df = self.tst.create_strategy_df()
        self.strat = Strat(self.strategy_id).obj

        # Choose resistance, support parameters.
        # The number of candles to consider before [0] and after [1] direction switch
        self.rsf_vals = [self.strat.rsf_n1, self.strat.rsf_n1]
        self.lever = 1

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
        self.short_win = self.strat.short_trend_win

    def add_cols(self, col_names):
        """Adds empty columns."""

        for col in col_names:
            self.df[col] = np.nan

        return self.df

    def find_lever(self):
        """finds the lever for macdh and trend line angle."""
        shifts = 0
        percentile = 0
        df = self.df.head(600)
        for i in range(len(df) - 1):
            shift = df.iloc[i]["Close"] - df.iloc[i + 1]["Close"]
            shifts += abs(shift)

        avg_shifts = shifts / len(df)
        avg_shifts = str(round(avg_shifts, 6)).replace(".", "")

        for digit in avg_shifts:
            if digit == "0":
                percentile += 1
            else:
                break

        if percentile == 4:
            self.lever = 100
        elif percentile == 3:
            self.lever = 10
        elif self.lever == 2:
            self.lever = 1
        else:
            self.lever = 1

        return self.lever

    def rsi_buy_condition(self, i):
        """defines the rsi buying condition."""
        if self.df.iloc[i][self.xb] == 1 and self.df.iloc[i - 1][self.xb] == 0:
            return True

    def macd_buy_condition(self, i):
        """defines the macd buying condition."""
        if self.df.iloc[i][self.macds] < self.df.iloc[i][self.macd] < 0 \
                and self.df.iloc[i][self.macdh] >= 0.01 / self.lever:
            return True

    def ema_trend_buy_condition(self, i):
        """defines the ema buying condition."""
        long_trend = self.tst.get_angle_two_points(
                    self.df.iloc[i - self.trend_win][self.ema],
                    self.df.iloc[i][self.ema],
                    self.lever)

        short_trend = self.tst.get_angle_two_points(
                    self.df.iloc[i - self.short_win][self.ema],
                    self.df.iloc[i][self.ema],
                    self.lever)

        if i > self.strat.ema_length * 2:
            if long_trend > self.strat.trend_angle and short_trend > self.strat.short_trend_angle:
                return True

    def sma_trend_buy_condition(self, i):
        """defines the sma buying condition."""
        long_trend = self.tst.get_angle_two_points(
            self.df.iloc[i - self.trend_win][self.sma],
            self.df.iloc[i][self.sma],
            self.lever)

        short_trend = self.tst.get_angle_two_points(
            self.df.iloc[i - self.short_win][self.sma],
            self.df.iloc[i][self.sma],
            self.lever)

        if i > self.strat.ema_length * 2:
            if long_trend > self.strat.trend_angle and short_trend > self.strat.short_trend_angle:
                return True

    def rsf_buy_condition(self, i):
        """Identifies supports and resistances to set sl and tp
        for buying conditions."""

        sl = rsf(self.df, self.rsf_vals[0], self.rsf_vals[1], 0).find_strongest(self.df.iloc[i]['Close'], 4)
        if sl:
            self.df.iloc[i, self.df.columns.get_loc('sl')] = sl
        else:
            sl = rsf(self.df, self.rsf_vals[0] - 1, self.rsf_vals[1] - 1, 0).find_strongest(
                self.df.iloc[i]['Close'], 2)
            self.df.iloc[i, self.df.columns.get_loc('sl')] = sl

        tp = self.df.iloc[i]['Close'] + (self.df.iloc[i]['Close'] - sl) * 2
        self.df.iloc[i, self.df.columns.get_loc('tp')] = tp
        return [sl, tp]

    def retracement_bar_buy_condition(self, i):

        whole_bar = self.df.iloc[i]['High'] - self.df.iloc[i]['Low']

        if self.df.iloc[i]['Open'] > self.df.iloc[i]['Close']:
            retracement = self.df.iloc[i]['High'] - self.df.iloc[i]['Open']
            if retracement / whole_bar * 100 >= self.strat.retracement_bar_val:
                return True

        elif self.df.iloc[i]['Open'] < self.df.iloc[i]['Close']:
            retracement = self.df.iloc[i]['High'] - self.df.iloc[i]['Close']
            if retracement / whole_bar * 100 >= self.strat.retracement_bar_val:
                return True

    def vol_tp_condition(self, i, direction):

        shifts = 0
        for val in range(self.strat.n_vol_tp - 1):
            shift = self.df.iloc[i - self.strat.n_vol_tp + val]['Close'] - self.df.iloc[i - self.strat.n_vol_tp + val - 1]['Close']
            shifts += abs(shift)

        avg_shift = shifts / self.strat.n_vol_tp
        tp_val = avg_shift * self.strat.tp_percentage / 100

        if direction == 1:
            tp = self.df.iloc[i + 1]['Open'] + tp_val
            sl = self.df.iloc[i + 1]['Open'] - tp_val * self.strat.sl_percentage / 100

            self.df.iloc[i, self.df.columns.get_loc('tp')] = tp
            self.df.iloc[i, self.df.columns.get_loc('sl')] = sl

        elif direction == 2:
            tp = self.df.iloc[i + 1]['Open'] - tp_val
            sl = self.df.iloc[i + 1]['Open'] + tp_val * self.strat.sl_percentage / 100

            self.df.iloc[i, self.df.columns.get_loc('tp')] = tp
            self.df.iloc[i, self.df.columns.get_loc('sl')] = sl

        return [sl, tp]

    def ma_tp_condition(self, i, direction):

        sl = self.df.iloc[i][self.ema]
        tp = 0

        # buying direction
        if direction == 1:
            sl_shift = self.df.iloc[i]['Close'] - sl
            tp = self.df.iloc[i]['Close'] + sl_shift * float(self.strat.ma_tp)

        # selling direction
        elif direction == 2:
            sl_shift = sl - self.df.iloc[i]['Close']
            tp = self.df.iloc[i]['Close'] - sl_shift * float(self.strat.ma_tp)

        self.df.iloc[i, self.df.columns.get_loc('tp')] = tp
        self.df.iloc[i, self.df.columns.get_loc('sl')] = sl

        return[sl, tp]

    def rsi_sell_condition(self, i):
        """defines the rsi selling condition."""
        if self.df.iloc[i][self.xa] == 1 and self.df.iloc[i - 1][self.xa] == 0:
            return True

    def macd_sell_condition(self, i):
        """defines the macd selling condition."""
        if self.df.iloc[i][self.macds] > self.df.iloc[i][self.macd] > 0 \
                and self.df.iloc[i][self.macdh] <= -0.01 / self.lever:
            return True

    def ema_trend_sell_condition(self, i):
        """defines the ema sell condition."""
        long_trend = self.tst.get_angle_two_points(
            self.df.iloc[i - self.trend_win][self.ema],
            self.df.iloc[i][self.ema],
            self.lever)

        short_trend = self.tst.get_angle_two_points(
            self.df.iloc[i - self.short_win][self.ema],
            self.df.iloc[i][self.ema],
            self.lever)

        if i > self.strat.ema_length * 2:
            if long_trend < self.strat.trend_angle * -1 and short_trend < self.strat.short_trend_angle * -1:
                return True

    def sma_trend_sell_condition(self, i):
        """defines the sma sell condition."""
        long_trend = self.tst.get_angle_two_points(
            self.df.iloc[i - self.trend_win][self.sma],
            self.df.iloc[i][self.sma],
            self.lever)

        short_trend = self.tst.get_angle_two_points(
            self.df.iloc[i - self.short_win][self.sma],
            self.df.iloc[i][self.sma],
            self.lever)

        if i > self.strat.ema_length * 2:
            if long_trend < self.strat.trend_angle * -1 and short_trend < self.strat.short_trend_angle * -1:
                return True

    def rsf_sell_condition(self, i):
        """Identifies supports and resistances to set sl and tp
        for selling conditions"""
        sl = rsf(self.df, self.rsf_vals[0], self.rsf_vals[1], 1).find_strongest(self.df.iloc[i]['Close'], 4)
        if sl:
            self.df.iloc[i, self.df.columns.get_loc('sl')] = sl
        else:
            sl = rsf(self.df, self.rsf_vals[0] - 1, self.rsf_vals[1] - 1, 1).find_strongest(
                self.df.iloc[i]['Close'], 4)
            self.df.iloc[i, self.df.columns.get_loc('sl')] = sl

        tp = self.df.iloc[i]['Close'] + (self.df.iloc[i]['Close'] - sl) * 2
        self.df.iloc[i, self.df.columns.get_loc('tp')] = tp
        return [sl, tp]

    def retracement_bar_sell_condition(self, i):

        whole_bar = self.df.iloc[i]['High'] - self.df.iloc[i]['Low']
        if self.df.iloc[i]['Close'] < self.df.iloc[i]['Open']:
            retracement = self.df.iloc[i]['Close'] - self.df.iloc[i]['Low']
            if retracement / whole_bar * 100 >= self.strat.retracement_bar_val:
                return True

        elif self.df.iloc[i]['Close'] > self.df.iloc[i]['Open']:
            retracement = self.df.iloc[i]['Open'] - self.df.iloc[i]['Low']
            if retracement / whole_bar * 100 >= self.strat.retracement_bar_val:
                return True

    def buying_conditions_applier(self, i):

        conditions = []
        valid_conditions = 0

        if self.strat.rsi_high:
            conditions.append("rsi")
            if self.rsi_buy_condition(i):
                valid_conditions += 1

        if self.strat.macd_fast:
            conditions.append("macd")
            if self.macd_buy_condition(i):
                valid_conditions += 1

        if self.strat.ema_length:
            conditions.append("ema")
            if self.ema_trend_buy_condition(i):
                valid_conditions += 1

        if self.strat.sma_length:
            conditions.append("sma")
            if self.sma_trend_buy_condition(i):
                valid_conditions += 1

        if self.strat.retracement_bar_val:
            conditions.append("rbv")
            if self.retracement_bar_buy_condition(i):
                valid_conditions += 1

        if valid_conditions == len(conditions):
            return True

    def selling_conditions_applier(self, i):

        conditions = []
        valid_conditions = 0

        if self.strat.rsi_high:
            conditions.append("rsi")
            if self.rsi_sell_condition(i):
                valid_conditions += 1

        if self.strat.ema_length:
            conditions.append("ema")
            if self.ema_trend_sell_condition(i):
                valid_conditions += 1

        if self.strat.macd_fast:
            conditions.append("macd")
            if self.macd_sell_condition(i):
                valid_conditions += 1

        if self.strat.sma_length:
            conditions.append("sma")
            if self.sma_trend_sell_condition(i):
                valid_conditions += 1

        if self.strat.retracement_bar_val:
            conditions.append("rbv")
            if self.retracement_bar_sell_condition(i):
                valid_conditions += 1

        if valid_conditions == len(conditions):
            return True

    def simulate_df(self):

        self.add_cols(["sell", "buy", "sl", "tp", "trend_angle"])
        self.find_lever()
        self.strat.lever = self.lever
        self.strat.save()

        for i in range(len(self.df)):

            trend_angle = self.tst.get_angle_two_points(
                    self.df.iloc[i - self.trend_win][self.ema],
                    self.df.iloc[i][self.ema],
                    self.lever
            )
            self.df.iloc[i, self.df.columns.get_loc('trend_angle')] = trend_angle

            """Applies buying position logic"""
            if self.buying_conditions_applier(i):
                self.df.iloc[i, self.df.columns.get_loc('buy')] = 1
                if self.strat.rsf_n1:
                    self.rsf_buy_condition(i)
                elif self.strat.n_vol_tp:
                    self.vol_tp_condition(i, 1)
                elif self.strat.ma_tp:
                    self.ma_tp_condition(i, 1)

            """Applies selling position logic"""
            if self.selling_conditions_applier(i):
                self.df.iloc[i, self.df.columns.get_loc('sell')] = 1
                if self.strat.rsf_n1:
                    self.rsf_sell_condition(i)
                elif self.strat.n_vol_tp:
                    self.vol_tp_condition(i, 2)
                elif self.strat.ma_tp:
                    self.ma_tp_condition(i, 2)

        return self.df

    def simulate(self):
        """Simulate the strategy based on the data
        from the simulate_df() method."""

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
                        "trend_angle": self.df.iloc[i]['trend_angle'],
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
                        "trend_angle": self.df.iloc[i]['trend_angle'],
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
                            trend_angle=round(pos["trend_angle"], 5),
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
                            close_val=round(pos["sl"], 9),
                            win=0,
                            loss=1,
                            profit=round(loss, 9),
                            date=pos["date"],
                            trend_angle=round(pos["trend_angle"], 5),
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
                            trend_angle=round(pos["trend_angle"], 5),
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
                            close_val=round(pos["sl"], 9),
                            win=0,
                            loss=1,
                            profit=round(loss, 9),
                            date=pos["date"],
                            trend_angle=round(pos["trend_angle"], 5),
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

        win_ratio = num_wins / len(positions) * 100

        res = {
            "num_positions": num_positions,
            "num_wins": num_wins,
            "num_losses": num_losses,
            "win_ratio": win_ratio,
            "total_profit": total_profit
        }

        stats = Stats(
            start_time=datetime.now(),
            win_ratio=win_ratio,
            wins=num_wins,
            losses=num_losses,
            profit=total_profit * self.lever,
            strategy=self.strategy_id,
        )
        stats.save()

        return res


"""__________________________________________________________________________________________________________________"""
# print(Simulator(2).simulate_df().tail(20))
# print(Simulator(2).simulate())
# print(Simulator(2).make_stats())
# print(Simulator(38).find_lever())
"""__________________________________________________________________________________________________________________"""


class Launcher:

    """The Launcher is build to launch a strategy over
    multiple indexes. The 'indexes' to be simulated should be
    a list of tickers and the strategy parameter should be
    defined as the 'params'"""

    def __init__(self, indexes, params, tick_file=None):

        # Indexes should be a list of tickers like "EURUSD=X"
        self.indexes = indexes
        # Parameters should be a dict of the parameters to use.
        self.params = params
        self.tick_file = tick_file

    def name_creator(self, ticker):

        """Creates a name for the strategy containing its parameters
        (which makes it unique)"""

        res = f'{ticker}-{self.params["period"]}-{self.params["interval"]}'
        if self.params["rsi_length"]:
            res += f'-rsi-{self.params["rsi_length"]}-{self.params["rsi_high"]}-{self.params["rsi_low"]}'
        if self.params["macd_fast"]:
            res += f'-macd-{self.params["macd_fast"]}-{self.params["macd_slow"]}'
        if self.params["ema_length"]:
            res += f'-ema-{self.params["ema_length"]}'
        if self.params["sma_length"]:
            res += f'-sma-{self.params["sma_length"]}'
        if self.params["trend_line_win"]:
            res += f'-tl-{self.params["trend_line_win"]}-{self.params["trend_angle"]}'
            res += f'-stl-{self.params["short_win"]}-{self.params["short_angle"]}'
        if self.params["rsf_n1"]:
            res += f'-rsf-{self.params["rsf_n1"]}-{self.params["rsf_n2"]}'
        if self.params["n_vol_tp"]:
            res += f'-vol-{self.params["n_vol_tp"]}-{self.params["tp_percent"]}-{self.params["sl_percent"]}'
        if self.params["ma_tp"]:
            res += f'-ma_tp-{self.params["ma_tp"]}'
        return res

    def check_duplicates(self, ticker):

        """Checks if strategy has already been tested"""

        strat_name = self.name_creator(ticker)
        strat_exists = Strategy.select().where(Strategy.name == strat_name)
        if strat_exists:
            return True
        else:
            return False

    def strategies_creator(self):
        strat_names = []
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
                    trend_angle=self.params["trend_angle"],
                    short_trend_win=self.params["short_win"],
                    short_trend_angle=self.params["short_angle"],
                    rsf_n1=self.params["rsf_n1"],
                    rsf_n2=self.params["rsf_n2"],
                    n_vol_tp=self.params["n_vol_tp"],
                    tp_percentage=self.params["tp_percent"],
                    sl_percentage=self.params["sl_percent"],
                    retracement_bar_val=self.params["rbv"],
                    ma_tp=self.params["ma_tp"],
                    description=self.params["description"],

                )
                strat.save()
                strat_names.append(self.name_creator(ticker))
        print(strat_names)
        return strat_names

    def launch(self):

        if self.tick_file:
            self.indexes = []
            with open(self.tick_file, 'r') as f:
                for line in f:
                    self.indexes.append(line.replace('\n', ''))

        strat_names = self.strategies_creator()

        for name in strat_names:
            try:
                strat = Strategy.get(name=name)
                print(strat.id, strat.ticker)
                Simulator(strat.id).simulate()
                Simulator(strat.id).make_stats()
            except ZeroDivisionError:
                print("Not enough values")
                continue


"""__________________________________________________________________________________________________________________"""

launcher = Launcher(
    ["JPY=X", "EURJPY=X", "EURCAD=X", "EURAUD=X", "EURNZD=X"],
    {
        "period": "50d",
        "interval": "5m",
        "rsi_length": None,
        "rsi_high": None,
        "rsi_low": None,
        "macd_fast": None,
        "macd_slow": None,
        "ema_length": 200,
        "sma_length": None,
        "trend_line_win": 200,
        "trend_angle": 45,
        "short_win": 100,
        "short_angle": 30,
        "rsf_n1": None,
        "rsf_n2": None,
        "n_vol_tp": None,
        "tp_percent": None,
        "sl_percent": None,
        "rbv": 45,
        "ma_tp": 2.0,
        "description": "res:sup finder strength = 4"
    },
    'D:\Predictive Financial Tools\currency_tickers.txt',
)

# print(launcher.strategies_creator())
print(launcher.launch())


"""__________________________________________________________________________________________________________________"""
