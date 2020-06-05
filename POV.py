import asyncio
import logging
from pprint import pprint as pp

import cx_Oracle
import numpy as np
import pandas as pd

from dev.helpers.config import config
from dev.oracle_db.send_child_order import send_child_order
from dev.utils.truncate import truncate
from oop_study.oop_dev.ALGO_STORAGES import VAR_STORAGES


class POV(object):

    def __init__(self, order_no,
                 symbol,
                 start_time, end_time,
                 side,
                 order_quantity,
                 interval,
                 participation_rate,
                 disclose,
                 user_id,
                 var_storages,
                 left_over_action=3,  # 1- Leave 2- Merge 3- Market 4- Payup
                 log_option=0):

        self.loop = asyncio.get_event_loop()
        self.VAR_STORAGES = var_storages
        self.symbol = symbol
        self.security_id = VAR_STORAGES().symbol_securityid_lookup[symbol]
        self.pov_response_pool = self.VAR_STORAGES.pov_response_pool
        self.last_prices_pool = self.VAR_STORAGES.last_prices_pool
        self.sum_of_vol = 0
        self.startvol = None
        # self.schedule_task()
        self.order_no = order_no
        # self.start_time = start_time if start_time is not None else pd.to_datetime('2017-01-03 10:00')
        # self.end_time = end_time if end_time is not None else pd.to_datetime('2017-01-03 18:00')
        if isinstance(start_time, str):
            self.start_time = pd.to_datetime(start_time, dayfirst=True, format='%d/%m/%Y %H:%M:%S').tz_localize(
                'Europe/Istanbul')
        if isinstance(end_time, str):
            self.end_time = pd.to_datetime(end_time, dayfirst=True, format='%d/%m/%Y %H:%M:%S').tz_localize(
                'Europe/Istanbul')
        self.side = side
        self.order_quantity = order_quantity
        self.participation_rate = float(participation_rate)
        self.interval = float(interval)
        # if isinstance(disclose, str):
        #     self.disclose_pct = float(disclose.split('%')[1]) / 100
        # else:
        #     self.disclose = float(self)
        self.disclose = (self.interval * self.participation_rate) / 100
        self.user_id = user_id
        self.left_over_action = left_over_action
        self.status = 1  # 1- Waiting 2- Pending Trigger 3- Working 4- Hold 5- Paused 6- Deleting 7- Filled 8- Available
        # 9- Owned 10- Pulling 11- Unmanaged 12- Initializing 13- Recovering
        self.order_type = 2  # 1- Market 2- Limit 3- Market Limit Market(MLM)
        # 4- Market To Limit(MTL) 5- Best Limit(BL) 6- Limit To Market (LTM)
        self.parent_code = f"POV_User{user_id}_{symbol}|{self.start_time.strftime('%Y%m%d-%H%M')}"
        self.executed_quantity = 0
        self.working_quantity = 0
        self.undisclosed_quantity = order_quantity
        self.algo_name = 'pov'
        if log_option == 1:
            logging.debug('TWAP-ALGO Object is created successfully')
        self.children = []
        self.check_task = None
        self.display_task = None
        self.count = 0

    def schedule_task(self):
        self.check_task = self.loop.create_task(self.check_for_trade())
        self.diplay_task = self.loop.create_task(self.display())
        self.loop.create_task(self.start_tasks())

    async def start_tasks(self):
        await self.check_task
        await self.display_task

    def find_(self):
        a = [i['tV'] for i in self.VAR_STORAGES.response_pool[self.security_id].values() if not np.isnan(i['tV'])]
        if len(a) > 0:
            print(f'last total volume is {a[-1]}')
            return a[-1]
        else:
            print('there is no total volume data in response pool')
            return None

    def start(self):
        try:
            self.startvol = self.pov_response_pool[self.security_id]['tV']
        except KeyError as e:
            print(str(e))
            self.startvol = self.find_()
        self.schedule_task()

    def modify_quantity(self, new_quantity):
        self.order_quantity = new_quantity

    def send_order(self, p_miktar, p_fiyat):
        params = config(section='oracledb')
        with cx_Oracle.connect(
                f"{params['username']}/{params['password']}@{params['ip']}:{params['port']}/{params['sid']}") as con:
            cur = con.cursor()
            res = send_child_order(parent_order_no=self.order_no,
                                   p_miktar=p_miktar,
                                   p_fiyat=p_fiyat,
                                   p_fiyat_tipi=self.order_type,
                                   cur=cur)
            con.commit()
        return res

    async def display(self):
        while True:
            await asyncio.sleep(7)
            print(f"current sum of volume is {self.sum_of_vol}")

    def is_done(self):
        if self.order_quantity_done >= self.order_quantity:
            return True
        # if self.count == 2:
        #     return True
        else:
            return False

    def get_last_vol(self):
        x = list(self.pov_response_pool[self.security_id].values())
        if len(x) > 0:
            return x[-1]['tV']
        else:
            return None

    async def check_for_trade(self):
        while True:
            await asyncio.sleep(.01)
            last_vol = self.get_last_vol()
            if last_vol:
                self.sum_of_vol = last_vol - self.startvol
                if self.sum_of_vol >= self.interval:
                    if self.is_done():
                        try:
                            print('Task is cancelling')
                            self.check_task.cancel()
                            self.diplay_task.cancel()
                        except Exception as e:
                            print(str(e))
                        # task cancel
                    else:
                        print(f"sum of volume ({self.sum_of_vol}) is more than {self.interval}")
                        self.sum_of_vol -= self.disclose
                        self.count += 1
                        self.trade()

    @property
    def remaining_seconds_to_order(self):
        return (self.start_time - pd.Timestamp.now('Europe/Istanbul')).total_seconds()

    @property
    def order_quantity_done(self):
        return sum([child.order_quantity_done for child in self.children])

    def manipulate_order_price(self, order_price):
        print(f'manipulating pov order price {order_price}')
        if self.side == 'A':
            return truncate(order_price + .1, 2)
        else:
            return truncate(order_price - .1, 2)

    def trade(self):
        print('trade')
        try:
            child_order_price = list(self.VAR_STORAGES.last_prices_pool[self.security_id].values())[-1]
            order_time = pd.Timestamp.now()
            pov_child_order = POV_CHILD(parent_order_no=self.order_no, order_price=child_order_price,
                                        order_time=order_time,
                                        order_quantity=self.disclose)
            # child_order = (
            #     child_order_price, order_time, self.disclose)  # named tuple or class cunku bunlara order no eklenecek.
            self.children.append(pov_child_order)
            if child_order_price is None:
                # historic price api
                pass
            manipulated_child_order_price = self.manipulate_order_price(child_order_price)

            res = self.send_order(p_fiyat=manipulated_child_order_price, p_miktar=self.disclose)
            pov_child_order.order_response = res
            pov_child_order.handle_order_response()
        except Exception as e:
            print('trade error in pov! ', str(e))

    def update(self, detected_child_order_msg):
        x = [child for child in self.children if child.order_no == detected_child_order_msg['order_no']]
        if len(x) == 1:
            related_pov_child = x[0]
            related_pov_child.update(detected_child_order_msg)


class POV_CHILD():
    def __init__(self, order_price, order_time, order_quantity, parent_order_no):
        self.order_price = order_price
        self.order_time = order_time
        self.order_quantity = order_quantity
        self.parent_order_no = parent_order_no
        self.order_response = None
        self.order_no = None
        self.status = 0
        self.order_quantity_left = order_quantity
        self.updates = []

    def console_order_sent(self):
        logging.debug(f"Child order iletildi ve open_twap_children objesine kaydedildi.")
        print(f"{'-' * 40}\n ILETILMIS EMIR :")
        pp(self.__dict__)
        logging.info(f"SUBMITTED ORDER @ {pd.Timestamp.now('Europe/Istanbul')} !!!")
        logging.info(f"sent order -> {self.__dict__}")

    def console_trade_execution(self, child_from_db):
        print('TRADE EXECUTION !!! ')
        print(
            f'****  {self.parent_order_no}:: {self.order_no} Executed !!! '
            f'Total Quantity: {self.order_quantity}'
            f'\nOld Quantity Left:{self.order_quantity_left} '
            f'New Quantity Left: {int(child_from_db["left"])} ****')

    def update(self, detected_child_order_msg):
        self.updates.append(detected_child_order_msg)

        status_ = int(detected_child_order_msg['status'])
        new_left_quantity_ = int(detected_child_order_msg['left'])
        exec_amount_ = float(detected_child_order_msg['exec_amount'].replace(',', '.'))

        if exec_amount_ > 0:
            self.console_trade_execution(detected_child_order_msg)

        self.status = status_
        self.order_quantity_left = new_left_quantity_

    def handle_order_response(self):
        res_status, res_order_no = self.order_response.split(';')[0], self.order_response.split(';')[2]

        if res_status == 'OK':
            self.status = 1
            self.order_no = res_order_no
            self.console_order_sent()

        elif res_status == "ER":
            print(f'Emir Iletilemedi. Response: {self.order_response}')
            print(f'Iletilemeyen Emir : {self.__dict__}')

        else:
            print(f'ANOTHER RETURN CODE FROM SEND_ORDER_TO_ORACLE_DB => {res_status} ')

    @property
    def order_response(self):
        return self._order_response

    @order_response.setter
    def order_response(self, value):
        self._order_response = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if hasattr(self, "status") and value != self.status:
            print(f'Status will change from {self.status} to {value}')
        self._status = value

    @property
    def remaining_seconds_to_order(self):
        return (self.order_time - pd.Timestamp.now('Europe/Istanbul')).total_seconds()

    @property
    def order_quantity_done(self):
        return self.order_quantity - self.order_quantity_left

    @property
    def order_quantity_left(self):
        return self._order_quantity_left

    @order_quantity_left.setter
    def order_quantity_left(self, value):
        self._order_quantity_left = value
