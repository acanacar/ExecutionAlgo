import asyncio
import logging

import cx_Oracle

from dev.helpers.config import config
from dev.oracle_db.get_orders import get_orders_ as fetch_orders


class ALGO_DETECTOR:

    def __init__(self, queue_storages, query_frequency):
        self.loop = asyncio.get_event_loop()
        self.twap_children_queue = queue_storages.twap_children_queue

        self.QUEUE_STORAGES = queue_storages
        self.query_frequency = query_frequency

        self.last_pc_q = ['0']

        self.schedule_tasks()

    def schedule_tasks(self):
        self.loop.create_task(self.detect())

    def fetch_orders_from_oracledb(self):
        params = config(section='oracledb')
        with cx_Oracle.connect(
                f"{params['username']}/{params['password']}@{params['ip']}:{params['port']}/{params['sid']}") as con:
            cur = con.cursor()
            res = fetch_orders(cur=cur, p_cq=self.last_pc_q[-1])
            if self.last_pc_q[-1] != res[0]:
                print('last_pc_q : ', self.last_pc_q[-1])
                logging.debug(f'last_pc_q : {self.last_pc_q[-1]}')
                logging.info(f'last_pc_q : {self.last_pc_q[-1]}')
            self.last_pc_q.append(res[0])
            con.commit()
        return res

    @staticmethod
    def console_orders(c_orders, p_orders):
        if len(c_orders) != 0 or len(p_orders) != 0:
            print(f"# of open_child_orders :{len(c_orders)}, # of parent_orders : {len(p_orders)}")
            if len(c_orders) >= 1:
                print('=== OPEN DB Child Orders ===')
                for i, child in enumerate(c_orders):
                    print(i, child)
                    # pp(child)

    @staticmethod
    def split_orders(res):
        child_orders = []
        parent_orders = []

        for order in res[1:]:
            order_d = {}
            for item in order.split('|'):
                [key, val] = item.split(';')
                order_d[key] = val
            if order_d['pr_order_no'] != '' and order_d['pr_order_no'] != order_d['order_no']:  # child order filter
                order_d['parent_child_f'] = 'child'
                child_orders.append(order_d)
            else:
                order_d['parent_child_f'] = 'parent'
                parent_orders.append(order_d)
            logging.debug('Child and Parent Orders are Splitted ORACLE-DB Orders')
        return child_orders, parent_orders

    async def handle_detected_child_order(self, children):
        for child in children:
            if child['algo_type'] == '1000':  # TWAP
                await self.QUEUE_STORAGES.detected_child_order_queues['TWAP'].put(child)
            elif child['algo_type'] == '1':  # POV
                await self.QUEUE_STORAGES.detected_child_order_queues['POV'].put(child)
            else:  # VWAP
                await self.QUEUE_STORAGES.detected_child_order_queues['VWAP'].put(child)

    async def detect(self):
        '''
        :param twap_children_queue: twap child queue
        :param n: kac saniyede bir yeni twap parent order uretilsin
        :return: no return but twap childlar twap_children_queue ya ekleniyor
        '''

        while True:
            logging.info(f'detection is sleeping {self.query_frequency} seconds')
            await asyncio.sleep(self.query_frequency)
            try:
                res = self.fetch_orders_from_oracledb()
                open_child_orders, parent_orders = self.split_orders(res)
                self.console_orders(c_orders=open_child_orders, p_orders=parent_orders)
                if len(parent_orders) > 0:
                    await self.QUEUE_STORAGES.detected_parent_orders_queue.put(parent_orders)
                if len(open_child_orders) > 0:
                    await self.handle_detected_child_order(children=open_child_orders)
            except Exception as e:
                print(str(e))
                logging.exception(e)
