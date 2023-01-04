import MetaTrader5 as mt
import time
from datetime import datetime, date, timedelta

from live_toolbox import ToolBox
from analyser import analyser



# Demo Account
login = 41792961
password = 'e9w3Ef2zL2Hl'
server = 'AdmiralMarkets-Demo'

best_strats = analyser(15)
print(best_strats)


def mt_connect():
    mt.initialize()
    mt.login(login, password, server)


class Live:

    def __init__(self, strats, max_margin):
        # Best sttrategies (list of ids) returned from analyser module
        self.strats = strats
        self.launch = True

        # max percentage of margin from balance
        self.max_margin = max_margin

    def check_margin(self):

        """Checks if the total of open positions are under the defined percentage of maximum margin"""

        mt_connect()
        margin = mt.account_info().margin
        balance = mt.account_info().balance

        if margin / balance * 100 < self.max_margin:
            print("Margin True")
            return True

    def get_history(self, hour_delta, symb):

        """Checks positions for one symbol are only opened with defined hourly interval"""

        mt_connect()
        today = datetime.today()
        delta = today - timedelta(hours=hour_delta)
        symbols = []

        orders = mt.history_orders_get(delta, today)
        for order in orders:
            symbols.append(order.symbol)

        print(symbols)

        if symb not in symbols:
            return True

    def max_pos(self, max, symb):

        "Defines a maximum number of open positions for one symbol"

        mt_connect()
        positions = mt.positions_get()
        symbols = []
        for pos in positions:
            symbols.append(pos.symbol)

        if symbols.count(symb) <= max:
            return True

    def run(self):
        start_time = time.time()
        mt_connect()

        while self.launch:
            print(mt.account_info().margin)
            print(mt.account_info().balance)
            for id in self.strats:
                req = ToolBox(id).request_creator()
                print("\n")
                if self.check_margin():
                    if req:
                        if self.max_pos(1, req["symbol"]):
                            if self.get_history(2, req["symbol"]):
                                print(req)
                                mt_connect()
                                mt.order_send(req)
                                print(mt.order_send(req))

            print(datetime.now())
            time.sleep(60.0 - ((time.time() - start_time) % 60.0))


"""__________________________________________________________________________________________________________________"""

print(Live(best_strats, 50).run())
# print(Live(best_strats, 50).max_pos(3, "USDJPY"))
# print(Live(best_strats, 50).get_history(10, "USDJPY"))