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

    def __init__(self, strats):
        self.strats = strats
        self.launch = True

    def run(self):
        start_time = time.time()
        mt_connect()

        while self.launch:

            for id in self.strats:
                request = ToolBox(id).request_creator()
                if request:
                    print(request["action"])
                    mt.order_send(request)
                    print(mt.order_send(request))

            print(datetime.now())
            time.sleep(60.0 - ((time.time() - start_time) % 60.0))


print(Live(best_strats).run())
