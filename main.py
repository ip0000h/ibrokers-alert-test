import json
import logging
import time
from argparse import ArgumentParser
from datetime import datetime
from enum import Enum
from threading import Thread

from ibapi.client import EClient
from ibapi.common import BarData, TickAttrib, TickerId
from ibapi.contract import Contract
from ibapi.ticktype import TickType
from ibapi.wrapper import EWrapper

from rq import Queue
from redis import Redis


CONNECT_SERVER_SLEEP_TIME = 1
REDIS_GET_TASKS_DELAY = 0.2


class AlertRule(Enum):
    GREAT = 1
    LESS = 2


class AlertTask(object):
    """
    Class for alerts objects
    """
    def __init__(self, req_id: int, alert_rule: AlertRule, price: float):
        self.req_id = req_id
        self.alert_rule = alert_rule
        self.price = price

    def is_alert_triggered(self, price: float):
        if self.alert_rule == AlertRule.GREAT:
            if price > self.price:
                return True
            else:
                return False
        else:
            if price < self.price:
                return True
            else:
                return False


class IBApp(EWrapper, EClient):
    """
    Mixin of Client (message sender and message loop holder)
    and Wrapper (set of callbacks)
    """
    def __init__(self, host: str, port: int, client_id: int, redis_queue: Queue):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)

        self.connect(host=host, port=port, clientId=client_id)
        app_thread = Thread(target=self.run, daemon=True)
        app_thread.start()
        setattr(self, "_thread", app_thread)

        self.redis_queue = redis_queue

        # alerts list
        self.tick_price_alerts = list
        self.historical_data_alerts = list
        # req_id for registering
        self.req_id = 0

    def next_req_id(self):
        self.req_id += 1
        return self.req_id

    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float, attrib: TickAttrib):
        logging.info('%s tickType:%s Price: %s', reqId, tickType, price)
        # TODO: here check for price and rules and create an alert task if needed

    def historicalData(self, reqId: int, bar: BarData):
        logging.info('Time: %s Close: %s', bar.date, bar.close)
        # TODO: here check for price and rules and create an alert task if needed

    def register_tick_price_alert(self, task_data: dict):
        contract = self.create_stock_contract(task_data['symbol'])
        # Request Market Data for contract
        self.reqMktData(self.next_req_id(), contract, '', False, False, [])


    def register_historical_data_alert(self, task_data: dict):
        contract = self.create_stock_contract(task_data['symbol'])
        # Request Market Data for contract
        # TODO: add other params
        self.reqHistoricalData(self.next_req_id(),
                               contract, '', '2 D', '1 hour', 'BID', 0, 2, False, [])

    def create_stock_contract(self, symbol: str, secType: str = 'CASH',
                              exchange: str = 'IDEALPRO', currency: str = 'USD'):
        """
        Custom method to create contract
        """
        contract = Contract()
        contract.symbol = symbol
        contract.secType = secType
        contract.exchange = exchange
        contract.currency = currency
        return contract


def main():
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Starting time is %s .", datetime.now())

    cmdLineParser = ArgumentParser()
    cmdLineParser.add_argument("-ih", "--ibroker_host", action="store", type=str,
                               dest="ibroker_host", default="127.0.0.1",
                               help="The host of IB app to use")
    cmdLineParser.add_argument("-ip", "--ibroker_port", action="store", type=int,
                               dest="ibroker_port", default=7497,
                               help="The TCP port for IB to use")
    cmdLineParser.add_argument("-rh", "--redis_host", action="store", type=str,
                               dest="redis_host", default="127.0.0.1",
                               help="The host of Redis app to use")
    cmdLineParser.add_argument("-rp", "--redis_port", action="store", type=int,
                               dest="redis_port", default=6379,
                               help="The TCP port for redis to use")
    args = cmdLineParser.parse_args()

    # create a redis connection and queue
    redis_connection = Redis(host=args.redis_host, port=args.redis_port)
    redis_queue = Queue(connection=redis_connection)

    app = IBApp(args.ibroker_host, args.ibroker_port, client_id=1, redis_queue=redis_queue)

    time.sleep(CONNECT_SERVER_SLEEP_TIME) # Sleep interval to allow time for connection to server

    try:
        while True:
            try:

                # get a new tasks for tick price
                new_tasks_tick_price = redis_connection.lrange('new_tasks_tick_price', 0, -1)
                redis_connection.delete('new_tasks_tick_price')
                if new_tasks_tick_price:
                    for task in new_tasks_tick_price:
                        task = json.loads(task)
                        app.register_tick_price_alert(task)

                # get a new tasks for history data
                new_tasks_history_data = redis_connection.lrange('new_tasks_historical_data', 0, -1)
                redis_connection.delete('new_tasks_historical_data')
                if new_tasks_history_data:
                    for task in new_tasks_history_data:
                        task = json.loads(task)
                        app.register_historical_data_alert(task)

                # sleep for new task
                time.sleep(REDIS_GET_TASKS_DELAY)

            except TypeError:
                logging.error('Wrong data from redis')
                continue
    finally:
        redis_connection.close()
        app.disconnect()


if __name__ == "__main__":
    main()
