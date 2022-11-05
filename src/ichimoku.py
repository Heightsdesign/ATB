import pandas as pd
import pandas_ta as ta
from fetcher import Fetcher


class IchimokuDF:

    def __init__(self, df):
        self.df = df

    def calculate(self):

        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        self.df.columns = map(str.lower, self.df.columns)
        ichimoku = ta.ichimoku(self.df['high'], self.df['low'], self.df['close'])
        self.df = pd.concat([self.df, ichimoku[0], ichimoku[1]], axis=1)
        # df1 = self.df.loc[self.df['volume'] > 0]

        return self.df


testobj = IchimokuDF(Fetcher('eurusd=x', '1mo', '1h').fetch_hist()[['Open', 'High', 'Low', 'Close', 'Volume']])
# print(testobj.calculate().tail(100))

print(help(ta.ichimoku))