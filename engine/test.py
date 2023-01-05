import MetaTrader5 as mt
import winsound
# Demo Account
login = 41795408
password = 'S3lZc200ewoo'
server = 'AdmiralMarkets-Demo'


def mt_connect():
    mt.initialize()
    mt.login(login, password, server)


def mt_account_info():
    mt_connect()
    account_info = mt.account_info()
    return account_info


def get_price(symbol):
    mt_connect()
    price = mt.symbol_info_tick(symbol).ask
    return price

symbol = "EURUSD"
lot = 0.01
sl = 0.0
tp = 0.0
deviation = 20

request = {
                "action": mt.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": mt.ORDER_TYPE_BUY,
                "price": get_price(symbol),
                "sl": sl,
                "tp": tp,
                "deviation": deviation,
                "magic": 234000,
                "comment": "python script open",
                "type_time": mt.ORDER_TIME_GTC,
                "type_filling": mt.ORDER_FILLING_IOC,
            }
#print(mt_connect())
#print(get_price(symbol))
#print(mt.order_send(request))
