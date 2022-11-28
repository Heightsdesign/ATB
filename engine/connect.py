import MetaTrader5 as mt

mt.initialize()

login = 41792961
password = 'e9w3Ef2zL2Hl'
server = 'AdmiralMarkets-Demo'

mt.login(login, password, server)

account_info = mt.account_info()
print(account_info)