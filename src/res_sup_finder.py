import pandas as pd
import pandas_ta as ta


class ResSupFinder:
    def __init__(self, df, n1, n2):
        self.df = df
        self.n1 = n1
        self.n2 = n2

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
                if self.df["High"][i] < self.df["High"][i-1]:
                    return 0

        for i in range(l + 1, l + self.n2 + 1):
            if i < len(self.df):
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

        assigned_scores = []

        for val in vals:
            count = vals.count(val)
            assigned_scores.append([val, count])

        return assigned_scores

    def plot(self):
        pass

df = pd.DataFrame()
df = df.ta.ticker("EURUSD=X", period="5d", interval="5m")
res_sup_finder = ResSupFinder(df, 4, 3)
resistances = res_sup_finder.get_resistances()
print(res_sup_finder.assign_score(resistances))












