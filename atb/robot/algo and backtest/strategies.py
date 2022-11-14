import pandas as pd
import pandas_ta as ta
from math import atan2, degrees
from datetime import date
from dateutil.relativedelta import relativedelta
import yfinance as yf



class Strategy:

    def __init__(self,
                 tick, period, interval,
                 rsi_length, xa, xb,
                 macd_fast, macd_slow,
                 ema_length,
                 trend_line_win, trend_lever,
                 backtest_months
                 ):
        self.tick = tick
        self.period = period
        self.interval = interval
        self.rsi_length = rsi_length
        self.xa = xa
        self.xb = xb
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.ema_length = ema_length
        self.backtest_months = backtest_months

        # The number of candles to consider to evaluate the trend angle
        self.trend_line_win = trend_line_win

        """Depending of the tick we are evaluating the trend angle
        might not reflect the right angle for instance a stock is likely
        to move several integer points within a day while a currency pair 
        might only move a few decimal points, the lever is used compensate
        that difference."""
        self.trend_lever = trend_lever

    def get_month_delta(self, num_months):
        today = date.today()
        print(str(today))
        previous_date = today - relativedelta(months=num_months)
        print(str(previous_date))
        return previous_date


    def get_df(self):
        """Gets the data and inserts it in a dataframe"""
        dfs = []
        final_df = pd.DataFrame()
        today = date.today()
        ticker = yf.Ticker(self.tick)

        if self.backtest_months:
            for i in range(self.backtest_months):
                if self.backtest_months - i >= 1:
                    start = today - relativedelta(months=self.backtest_months - i)
                    end = today - relativedelta(months=self.backtest_months - i - 1)
                    df = ticker.history(start=str(start), end=str(end), interval=self.interval)
                    dfs.append(df)
            final_df = pd.concat(dfs)
        else:
            final_df = ticker.history(period=self.period, interval=self.interval)

        return final_df


    def create_strategy_df(self):
        """Creates the main dataframe using the specified
        parameters the df looks like :ohlc data, rsi data,
        macd data, long ema data"""


        df = self.get_df()
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

        rsi = df.ta.rsi(close='Close', length=self.rsi_length, signal_indicators=True, xa=self.xa, xb=self.xb)
        macd = df.ta.macd(close='Close', fast=self.macd_fast, slow=self.macd_slow)
        ema = df.ta.ema(close='Close', length=self.ema_length)
        df = pd.concat([df, rsi, macd, ema], axis=1)
        df = df.drop(['Dividends', 'Stock Splits'], axis=1)

        return df

    def get_shift(self, new_val, old_val):
        """Gets the shift percentage between two values"""
        return (new_val - old_val) / old_val * 100

    def get_angle_two_points(self, og_val, next_val):
        """Get the angle in degrees between two points
        use the trend lever to get right values"""

        myradians = atan2(next_val - og_val, 1)
        mydegrees = degrees(myradians)

        return mydegrees * self.trend_lever

    def get_trend_line_angle(self):
        """ Get the trend line angle"""

        df = self.get_df()
        ema = df.ta.ema(close='Close', length=self.ema_length)
        df = pd.concat([df, ema], axis=1)
        df = df.drop(['Dividends', 'Stock Splits'], axis=1)

        now_point = df.iloc[-1]['EMA_' + str(self.ema_length)]
        previous_point = df.iloc[-self.trend_line_win]['EMA_' + str(self.ema_length)]

        trend_angle = self.get_angle_two_points(previous_point, now_point)
        print(f"Trend angle : {trend_angle}, Previous point : {previous_point}, Now point : {now_point}")

        return trend_angle


"""__________________________________________________________________________________________________________________"""


# strategy = Strategy("EURUSD=X", "1mo", "5m", 14, 65, 35, 9, 26, 200, 200, 100, 0)
# print(strategy.create_strategy_df().tail(35))
# print(strategy.get_trend_line_angle())
# print(help(ta.macd))








