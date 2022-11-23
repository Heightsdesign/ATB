import pandas as pd
import pandas_ta as ta
from math import atan2, degrees
from datetime import date
from dateutil.relativedelta import relativedelta
import yfinance as yf
from models import Strategy


class Strat:

    def __init__(self, id):
        self.id = id
        self.obj = Strategy.get(id=self.id)

    def get_df(self):

        """Gets the data and inserts it in a dataframe"""
        dfs = []
        today = date.today()
        ticker = yf.Ticker(self.obj.ticker)

        # if user selected a number of months to backtest
        """if self.obj.backtest_months:
            for i in range(self.obj.backtest_months):
                if self.obj.backtest_months - i >= 1:
                    start = today - relativedelta(months=self.obj.backtest_months - i)
                    end = today - relativedelta(months=self.obj.backtest_months - i - 1)
                    df = ticker.history(start=str(start), end=str(end), interval=self.obj.interval)
                    dfs.append(df)
            final_df = pd.concat(dfs)
        else:
            final_df = ticker.history(period=self.obj.period, interval=self.obj.interval)"""

        final_df = ticker.history(period=self.obj.period, interval=self.obj.interval)

        return final_df

    def create_strategy_df(self):
        """Creates the main dataframe using the specified
        parameters the df looks like :ohlc data, rsi data,
        macd data, long ema data"""

        df = self.get_df()

        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

        rsi = df.ta.rsi(close='Close',
                        length=self.obj.rsi_length,
                        signal_indicators=True,
                        xa=self.obj.rsi_high,
                        xb=self.obj.rsi_low)

        macd = df.ta.macd(close='Close', fast=self.obj.macd_fast, slow=self.obj.macd_slow)
        ema = df.ta.ema(close='Close', length=self.obj.ema_length)
        sma = df.ta.sma(close='Close', length=self.obj.sma_length)

        df = pd.concat([df, rsi, macd, ema, sma], axis=1)
        df = df.drop(['Dividends', 'Stock Splits'], axis=1)

        return df

    def get_shift(self, new_val, old_val):
        """Gets the shift percentage between two values"""
        return (new_val - old_val) / old_val * 100

    def get_angle_two_points(self, og_val, next_val, lever):
        """Get the angle in degrees between two points
        use the trend lever to get right values"""

        myradians = atan2(next_val - og_val, 1)
        mydegrees = degrees(myradians)

        return mydegrees * lever

    def get_trend_line_angle(self):
        """ Get the trend line angle"""

        df = self.get_df()
        ema = df.ta.ema(close='Close', length=self.obj.ema_length)
        df = pd.concat([df, ema], axis=1)
        df = df.drop(['Dividends', 'Stock Splits'], axis=1)

        now_point = df.iloc[-1]['EMA_' + str(self.obj.ema_length)]
        previous_point = df.iloc[-self.obj.trend_line_win]['EMA_' + str(self.obj.ema_length)]

        trend_angle = self.get_angle_two_points(previous_point, now_point)
        print(f"Trend angle : {trend_angle}, Previous point : {previous_point}, Now point : {now_point}")

        return trend_angle


"""__________________________________________________________________________________________________________________"""


# strategy = Strat(5)
# print(strategy.create_strategy_df().tail(50))
# print(strategy.get_trend_line_angle())
# print(help(ta.macd))








