import pandas as pd
import pandas_ta as ta

params = {}


class Simulator:
    def __init__(self, data, params):
        self.data = data
        self.params = params
