import MetaTrader5 as mt
import time
from datetime import datetime

from live_toolbox import ToolBox
from analyser import analyser



# Demo Account
login = 41792961
password = 'e9w3Ef2zL2Hl'
server = 'AdmiralMarkets-Demo'

best_strats = analyser(9)
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
        mt_connect()
        margin = mt.account_info().margin
        balance = mt.account_info().balance
        print(margin)
        print(balance)

        if margin / balance * 100 < self.max_margin:
            return True

    def run(self):
        start_time = time.time()
        mt_connect()

        while self.launch:

            for id in self.strats:
                request = ToolBox(id).request_creator()
                if self.check_margin():
                    if request:
                        print(request["action"])
                        mt.order_send(request)
                        print(mt.order_send(request))

            print(datetime.now())
            time.sleep(60.0 - ((time.time() - start_time) % 60.0))


"""__________________________________________________________________________________________________________________"""

print(Live(best_strats, 30).run())
# print(Live(best_strats, 50).check_margin())
