import pandas as pd
import pandas_ta as ta
from math import atan2, degrees


class Strategy:

    def __init__(self, tick, period, interval):
        self.tick = tick
        self.period = period
        self.interval = interval

    def get_df(self):

        df = pd.DataFrame()
        df = df.ta.ticker(self.tick, period=self.period, interval=self.interval)
        return df

    def create_strategy_df(self):
        # define strategy here
        df = self.get_df()
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

        rsi = df.ta.rsi(close='Close', length=14, signal_indicators=True, xa=65, xb=35)
        macd = df.ta.macd(close='Close', fast=9, slow=26)
        ema = df.ta.ema(close='Close', length=200)
        df = pd.concat([df, rsi, macd, ema], axis=1)
        df = df.drop(['Dividends', 'Stock Splits'], axis=1)
        return df

    def get_shift(self, new_val, old_val):

        return (new_val - old_val) / old_val * 100

    def GetAngleOfLineBetweenTwoPoints(self, og_val, next_val):

        myradians = atan2(next_val - og_val, 1)
        mydegrees = degrees(myradians)

        return mydegrees

    def get_trend_scores(self, offset, num_offsets):

        offsets = []
        angles = []
        scores = []
        shift_index = 0
        mid_score = 0

        df = self.get_df()
        ema = df.ta.ema(close='Close', length=200)
        df = pd.concat([df, ema], axis=1)
        df = df.drop(['Dividends', 'Stock Splits'], axis=1)

        last_val = df.iloc[-1]['EMA_200']
        offsets.append(last_val)

        for i in range(1, num_offsets):
            offset_val = df.iloc[-offset * i]['EMA_200']
            offsets.append(offset_val)

        offsets.reverse()

        for val in offsets:
            if shift_index < len(offsets) - 1:
                angle = self.GetAngleOfLineBetweenTwoPoints(val, offsets[shift_index + 1])
                angles.append(angle)
                shift_index += 1

        for angle in angles:
            mid_score += angle

        long_offset = df.iloc[-offset * num_offsets * 2]['EMA_200']
        long_score = self.GetAngleOfLineBetweenTwoPoints(long_offset, last_val)


        return [angles, mid_score, long_score]


# strategy = Strategy("AAPL", "1mo", "15m")
# print(strategy.create_strategy_df().tail(20))
# print(strategy.get_trend_scores(10, 5))
# print(help(ta.macd))







