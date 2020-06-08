import threading
import time

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract


class IBapi(EWrapper, EClient):

    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, self)

    def tickPrice(self, reqId, tickType, price, attrib):
        if reqId == 1:
            print(f'The current USD_EUR({reqId}) tickType:{tickType} price is: {price}')
        elif reqId == 2:
            print(f'The current BTC({reqId}) tickType:{tickType} price is: {price}')


def run_loop():
    app.run()


app = IBapi()
app.connect('127.0.0.1', 7497, 123)

# Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1) # Sleep interval to allow time for connection to server

apple_contract = Contract()
apple_contract.symbol = 'AAPL'
apple_contract.secType = 'STK'
apple_contract.exchange = 'SMART'
apple_contract.currency = 'USD'

eurusd_contract = Contract()
eurusd_contract.symbol = 'EUR'
eurusd_contract.secType = 'CASH'
eurusd_contract.exchange = 'IDEALPRO'
eurusd_contract.currency = 'USD'

btc_futures__contract = Contract()
btc_futures__contract.symbol = 'BRR'
btc_futures__contract.secType = 'FUT'
btc_futures__contract.exchange = 'CMECRYPTO'
btc_futures__contract.lastTradeDateOrContractMonth = '202006'

# MarketDataTypeEnum.DELAYED
# app.reqMarketDataType(3)

# Request Market Data for EUR\USD
app.reqMktData(1, eurusd_contract, '', False, False, [])

# Request Market Data for BTC
# app.reqMktData(2, btc_futures__contract, '', False, False, [])
