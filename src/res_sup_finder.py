import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from decimal import Decimal
import math


class ResSupFinder:
    def __init__(self, df, n1, n2, direction):

        self.df = df
        # number of candles to consider before switch
        self.n1 = n1
        # number of candles to consider after switch
        self.n2 = n2
        # Should the program find resistance or support
        # 1 for resistance, 0 for support
        self.direction = direction

    def support_finder(self, l):

        for i in range(l - self.n1 + 1, l + 1):
            if self.df["Low"][i] > self.df["Low"][i - 1]:
                return 0

        for i in range(l + 1, l + self.n2 + 1):
            if self.df["Low"][i] < self.df["Low"][i - 1]:
                return 0

        return 1

    def resistance_finder(self, l):

        for i in range(l - self.n1 + 1, l + 1):
            if i < len(self.df):
                # checks if candles are increasing else returns 0
                if self.df["High"][i] < self.df["High"][i-1]:
                    return 0

        for i in range(l + 1, l + self.n2 + 1):
            if i < len(self.df):
                # checks if candles are decreasing else returns 0
                if self.df["High"][i] > self.df["High"][i - 1]:
                    return 0

        return 1

    def get_supports(self):

        supports = []
        for row in range(self.n1, len(self.df - self.n2)):

            if self.support_finder(row):
                supports.append(self.df["Low"][row])

        return supports

    def get_resistances(self):

        resistances = []

        for row in range(self.n1, len(self.df - self.n2)):
            if self.resistance_finder(row):
                resistances.append(self.df["High"][row])

        return resistances

    def assign_score(self, vals):
        # vals should be in the  get_resistances() or get_supports data format

        assigned_scores = []

        for val in vals:
            count = vals.count(val)
            assigned_scores.append([val, count])

        return assigned_scores

    def find_closest(self, val):

        if self.direction == 1:

            res_vals = self.get_resistances()

            arr = np.asarray(res_vals)
            diff = arr - val
            diff[diff < 0] = np.inf
            idx = diff.argmin()

            return arr[idx]

        if self.direction == 0:

            sup_vals = self.get_supports()

            arr = np.asarray(sup_vals)
            diff = arr - val
            diff[diff > 0] = -np.inf
            idx = diff.argmax()
            return arr[idx]

    def find_strongest(self, val):
        pass

    def plot_vals(self, vals):
        # vals should be the assign_score data format

        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=self.df.index,
                    open=self.df["Open"],
                    high=self.df["High"],
                    low=self.df["Low"],
                    close=self.df["Close"]
                )
            ]
        )

        index = 0

        while 1:
            if index > len(vals) -1:
                break

            fig.add_shape(
                type='line',
                x0=self.df.index[0],
                y0=vals[index][0],
                x1=self.df.index[-1],
                y1=vals[index][0]
            )
            index += 1
        fig.show()


"""______________________________________________________________________________________________________"""

df = pd.DataFrame()
df = df.ta.ticker("AAPL", period="5d", interval="5m")

res_sup_finder = ResSupFinder(df, 3, 2, 1)

resistances = res_sup_finder.get_resistances()
print(resistances)

supports = res_sup_finder.get_supports()
# print(supports)

# print(res_sup_finder.assign_score(resistances))

print(res_sup_finder.find_closest(142.60000610351562))

assigned_resistances = res_sup_finder.assign_score(resistances)
# print(res_sup_finder.plot_vals(assigned_resistances))













