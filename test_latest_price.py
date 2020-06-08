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
        print(f'The current USD_EUR({reqId}) tickType:{tickType} price is: {price}')


def run_loop():
    app.run()


app = IBapi()
app.connect('127.0.0.1', 7497, 1)

# Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1) #  Sleep interval to allow time for connection to server

# EUR\USD contract
eurusd_contract = Contract()
eurusd_contract.symbol = 'EUR'
eurusd_contract.secType = 'CASH'
eurusd_contract.exchange = 'IDEALPRO'
eurusd_contract.currency = 'USD'

# Request Market Data for EUR\USD
app.reqMktData(1, eurusd_contract, '', False, False, [])
