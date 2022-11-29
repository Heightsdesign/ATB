import MetaTrader5 as mt

# Demo Account
login = 41792961
password = 'e9w3Ef2zL2Hl'
server = 'AdmiralMarkets-Demo'


def mt_connect():
    mt.initialize()
    mt.login(login, password, server)


def account_info():
    mt_connect()
    account_info = mt.account_info()
    return account_info


balance = account_info().balance
print(balance)