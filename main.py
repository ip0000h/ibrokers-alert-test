import logging
import time
from argparse import ArgumentParser
from datetime import datetime

from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper


class IBApp(EWrapper, EClient):
    """
    Mixin of Client (message sender and message loop holder)
    and Wrapper (set of callbacks)
    """
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self.started = False
        self.nKeybInt = 0

    def keyboardInterrupt(self):
        """Callback - User pressed Ctrl-C"""
        self.nKeybInt += 1
        if self.nKeybInt == 1:
            msg = "Manual interruption!"
            logging.warning(msg)
            self._onStop()
        else:
            msg = "Forced Manual interruption!"
            logging.error(msg)

    def _onStart(self):
        if self.started:
            return
        self.started = True
        self.onStart()

    def _onStop(self):
        if not self.started:
            return
        self.onStop()
        self.started = False

    def onStart(self):
        logging.info('Main logic started')

    def onStop(self):
        logging.info('Main logic stopped')

    def tickPrice(self, reqId, tickType, price, attrib):
        if tickType == 2 and reqId == 1:
            print('The current ask price is: ', price)


def main():
    logging.debug("Starting time is %s .", datetime.now())
    logging.getLogger().setLevel(logging.WARNING)

    cmdLineParser = ArgumentParser()
    cmdLineParser.add_argument("-H", "--host", action="store", type=str,
                               dest="host", default="127.0.0.1", help="The host of IB app to use")
    cmdLineParser.add_argument("-p", "--port", action="store", type=int,
                               dest="port", default=7497, help="The TCP port to use")
    cmdLineParser.add_argument("-C", "--global-cancel", action="store_true",
                               dest="global_cancel", default=False,
                               help="whether to trigger a globalCancel req")
    args = cmdLineParser.parse_args()
    app = IBApp()
    app.connect(args.host, args.port, clientId=1)

    time.sleep(1) #Sleep interval to allow time for connection to server

    #Create contract object
    apple_contract = Contract()
    apple_contract.symbol = 'AAPL'
    apple_contract.secType = 'STK'
    apple_contract.exchange = 'SMART'
    apple_contract.currency = 'USD'

    #Request Market Data
    app.reqMktData(1, apple_contract, '', False, False, [])

    time.sleep(10) #Sleep interval to allow time for incoming price data
    app.disconnect()

if __name__ == "__main__":
    main()
