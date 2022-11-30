import time
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import MetaTrader5 as mt

from res_sup_finder import ResSupFinder as rsf
from models import Strategy, Stats, Results
from strategies import Strat


def mt_account_info():
    account_info = mt.account_info()
    return account_info


def get_price(symbol):
    price = mt.symbol_info_tick(symbol).ask
    return price


class ToolBox:

    def __init__(self, strategy_id):

        self.strategy_id = strategy_id
        self.strat = Strat(self.strategy_id).obj
        self.strat_tools = Strat(self.strategy_id)
        self.lever = self.strat.lever

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

    def get_lot(self):

        balance = mt_account_info().balance

        lot = 0
        if 1000 <= balance < 2000:
            lot = 0.01
        elif 2000 <= balance < 3000:
            lot = 0.02
        elif 3000 <= balance < 4000:
            lot = 0.03
        elif 4000 <= balance < 5000:
            lot = 0.04

        return lot

    def get_data_period(self):

        min_num_candles = self.strat.trend_line_win * 8
        num_mins = min_num_candles * 5
        num_hours = num_mins / 60
        num_days = num_hours / 24

        return f"{round(num_days)}d"

    def get_data(self):
        ticker = yf.Ticker(self.strat.ticker)
        self.df = ticker.history(period=self.get_data_period(), interval=self.strat.interval)
        return self.df

    def create_mt_symbol(self):
        yf_sym = self.strat.ticker
        if "=X" in yf_sym:
            yf_sym = yf_sym.replace("=X", "")

        if len(yf_sym) == 3:
            yf_sym = "USD" + yf_sym

        return yf_sym

    def apply_inidcators(self):

        self.df = self.get_data()

        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

        rsi = self.df.ta.rsi(close='Close',
                             length=self.strat.rsi_length,
                             signal_indicators=True,
                             xa=self.strat.rsi_high,
                             xb=self.strat.rsi_low
                             )

        macd = self.df.ta.macd(close='Close',
                               fast=self.strat.macd_fast,
                               slow=self.strat.macd_slow)
        ema = self.df.ta.ema(close='Close', length=self.strat.ema_length)
        sma = self.df.ta.sma(close='Close', length=self.strat.sma_length)

        self.df = pd.concat([self.df, rsi, macd, ema, sma], axis=1)
        self.df = self.df.drop(['Dividends', 'Stock Splits'], axis=1)
        return self.df

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
        long_trend = self.strat_tools.get_angle_two_points(
                    self.df.iloc[i - self.trend_win][self.ema],
                    self.df.iloc[i][self.ema],
                    self.lever)

        short_trend = self.strat_tools.get_angle_two_points(
                    self.df.iloc[i - self.short_win][self.ema],
                    self.df.iloc[i][self.ema],
                    self.lever)

        if long_trend > self.strat.trend_angle and short_trend > self.strat.short_trend_angle:
            return True

    def sma_trend_buy_condition(self, i):
        """defines the sma buying condition."""
        long_trend = self.strat_tools.get_angle_two_points(
            self.df.iloc[i - self.trend_win][self.sma],
            self.df.iloc[i][self.sma],
            self.lever)

        short_trend = self.strat_tools.get_angle_two_points(
            self.df.iloc[i - self.short_win][self.sma],
            self.df.iloc[i][self.sma],
            self.lever)

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
        sl = 0
        tp = 0

        for val in range(self.strat.n_vol_tp - 1):
            shift = self.df.iloc[i - self.strat.n_vol_tp + val]['Close'] - self.df.iloc[i - self.strat.n_vol_tp + val - 1]['Close']
            shifts += abs(shift)

        avg_shift = shifts / self.strat.n_vol_tp
        tp_val = avg_shift * self.strat.tp_percentage / 100

        if direction == 1:
            tp = self.df.iloc[i]['Close'] + tp_val
            sl = self.df.iloc[i]['Close'] - tp_val * self.strat.sl_percentage / 100

        elif direction == 2:
            tp = self.df.iloc[i]['Close'] - tp_val
            sl = self.df.iloc[i]['Close'] + tp_val * self.strat.sl_percentage / 100

        return [sl, tp]

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
        long_trend = self.strat_tools.get_angle_two_points(
            self.df.iloc[i - self.trend_win][self.ema],
            self.df.iloc[i][self.ema],
            self.lever)

        short_trend = self.strat_tools.get_angle_two_points(
            self.df.iloc[i - self.short_win][self.ema],
            self.df.iloc[i][self.ema],
            self.lever)

        if long_trend < self.strat.trend_angle * -1 and short_trend < self.strat.short_trend_angle * -1:
            return True

    def sma_trend_sell_condition(self, i):
        """defines the sma sell condition."""
        long_trend = self.strat_tools.get_angle_two_points(
            self.df.iloc[i - self.trend_win][self.sma],
            self.df.iloc[i][self.sma],
            self.lever)

        short_trend = self.strat_tools.get_angle_two_points(
            self.df.iloc[i - self.short_win][self.sma],
            self.df.iloc[i][self.sma],
            self.lever)

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

    def request_creator(self):

        self.df = self.apply_inidcators()
        idx = len(self.df) - 1
        request = {}

        symbol = self.create_mt_symbol()
        lot = self.get_lot()
        deviation = 20
        price = get_price(symbol)
        sl = 0
        tp = 0

        """Applies buying position logic"""
        if self.buying_conditions_applier(idx):
            if self.strat.rsf_n1:
                sl = self.rsf_buy_condition(idx)[0]
                tp = self.rsf_buy_condition(idx)[1]
            elif self.strat.n_vol_tp:
                sl = self.vol_tp_condition(idx, 1)[0]
                tp = self.vol_tp_condition(idx, 1)[1]

            request = {
                "action": mt.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": mt.ORDER_TYPE_BUY,
                "price": price,
                "sl": round(sl, 5),
                "tp": round(tp, 5),
                "deviation": deviation,
                "magic": 234000,
                "comment": "python script open",
                "type_time": mt.ORDER_TIME_GTC,
                "type_filling": mt.ORDER_FILLING_IOC,
            }

        """Applies selling position logic"""
        if self.selling_conditions_applier(idx):
            self.df.iloc[i, self.df.columns.get_loc('sell')] = 1
            if self.strat.rsf_n1:
                sl = self.rsf_sell_condition(idx)[0]
                tp = self.rsf_sell_condition(idx)[1]
            elif self.strat.n_vol_tp:
                sl = self.vol_tp_condition(idx, 2)[0]
                tp = self.vol_tp_condition(idx, 2)[1]

            request = {
                "action": mt.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": mt.ORDER_TYPE_SELL,
                "price": price,
                "sl":round(sl, 5),
                "tp": round(tp, 5),
                "deviation": deviation,
                "magic": 234000,
                "comment": "python script open",
                "type_time": mt.ORDER_TIME_GTC,
                "type_filling": mt.ORDER_FILLING_IOC,
            }

        return request


"""__________________________________________________________________________________________________________________"""

# print(ToolBox(2).request_creator())
"""__________________________________________________________________________________________________________________"""

