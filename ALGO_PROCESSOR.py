from oop_study.oop_dev.POV import POV
from oop_study.oop_dev.TWAP import *
from oop_study.oop_dev.subscription import subscribe


class ALGO_PROCESSOR:
    def __init__(self, ws, queue_storages, var_storages, algo_parents):
        self.loop = asyncio.get_event_loop()
        self.ws = ws
        self.VAR_STORAGES = var_storages
        self.QUEUE_STORAGES = queue_storages

        self.algo_parents = algo_parents

        self.open_twap_children_lock = asyncio.Lock()
        self.parent_lock = asyncio.Lock()

        self.schedule_task()

    def schedule_task(self):
        self.loop.create_task(self.process_detected_parent())

    def create_instance(self, parent_order, type):
        if type == 'TWAP':
            return TWAP(order_no=parent_order['order_no'],
                        symbol=parent_order['stock_code'],
                        parent_order_quantity=int(parent_order['how_much']),
                        start_time=parent_order['start_time'],
                        end_time=parent_order['end_time'],
                        side=parent_order['buy_sel'],
                        one_slice_interval_as_minutes=int(parent_order['Interval']),
                        user_id=parent_order['customer_no'],
                        log_option=1)
        if type == 'POV':
            return POV(order_no=parent_order['order_no'],
                       symbol=parent_order['stock_code'],
                       start_time=parent_order['start_time'],
                       end_time=parent_order['end_time'],
                       side=parent_order['buy_sel'],
                       order_quantity=int(parent_order['how_much']),
                       interval=parent_order['Interval'],
                       participation_rate = parent_order['Participation_Rate'],
                       disclose=parent_order['Child_Quantity'],
                       user_id=parent_order['customer_no'],
                       log_option=1,
                       var_storages=self.VAR_STORAGES)

    async def twap_process(self, order):
        security_id = self.VAR_STORAGES.symbol_securityid_lookup[order['stock_code']]

        self.VAR_STORAGES.twap_response_pool.update({security_id: {}})

        await subscribe(websocket=self.ws,
                        symbol=self.VAR_STORAGES.symbol_securityid_lookup[order['stock_code']],
                        fields=self.VAR_STORAGES.shortcodes['twap'])
        algo_parent = self.create_instance(parent_order=order, type='TWAP')
        algo_parent.create_child_orders()
        return algo_parent

    async def pov_process(self, order):
        security_id = self.VAR_STORAGES.symbol_securityid_lookup[order['stock_code']]
        self.VAR_STORAGES.pov_response_pool.update({security_id: {}})

        await subscribe(websocket=self.ws,
                        symbol=self.VAR_STORAGES.symbol_securityid_lookup[order['stock_code']],
                        fields=self.VAR_STORAGES.shortcodes['pov'])
        algo_parent = self.create_instance(parent_order=order, type='POV')
        print(algo_parent)
        return algo_parent

    def vwap_process(self, order):
        pass

    def check_validity(self, parent_order):
        v1 = parent_order['order_no'] not in self.algo_parents
        # v2 = parent_order['start_time'] > pd.Timestamp.now('Europe/Istanbul').strftime('%d/%m/%Y %H:%M:%S')
        v2 = True
        v3 = parent_order['end_time'] > pd.Timestamp.now('Europe/Istanbul').strftime('%d/%m/%Y %H:%M:%S')
        if not v1:
            print(f"parent order is already got !")
        if not v2:
            print(f"Parent Order start time is already passed. "
                  f"{parent_order['start_time']} < {pd.Timestamp.now('Europe/Istanbul').strftime('%d/%m/%Y %H:%M:%S')}")
        return v1 and v2 and v3

    async def handle_subscribe(self, symbol):
        security_id = self.VAR_STORAGES.symbol_securityid_lookup[symbol]
        self.VAR_STORAGES.response_pool.update({security_id: {}})
        # self.VAR_STORAGES.previous_tick.update({security_id: {}})
        # self.VAR_STORAGES.twap_response_pool.update({security_id: {}})
        # self.VAR_STORAGES.minutes_processed_pool.update({security_id: {}})
        # self.VAR_STORAGES.minutes_candlesticks_pool.update({security_id: []})
        # await subscribe(websocket=self.ws,
        #                 symbol=symbol,
        #                 fields=self.VAR_STORAGES.shortcodes['twap'])

    async def handle_detected_parent(self, order):
        if order['algo_type'] == '1000':  # TWAP

            algo_parent = await self.twap_process(order)
            await self.QUEUE_STORAGES.algo_parent_queue.put(algo_parent)  # twap olarak degismeli

        elif order['algo_type'] == '1':  # POV

            algo_parent = await self.pov_process(order)
            await self.QUEUE_STORAGES.algo_parent_pov_queue.put(algo_parent)

        else:  # VWAP
            algo_parent = self.vwap_process(order)

    async def process_detected_parent(self):
        while True:
            parent_orders = await self.QUEUE_STORAGES.detected_parent_orders_queue.get()
            if parent_orders:
                for parent_order_ in parent_orders:
                    if self.check_validity(parent_order_):
                        await self.handle_subscribe(parent_order_['stock_code'])
                        try:
                            await self.handle_detected_parent(parent_order_)
                        except Exception as e:
                            print(str(e))
                            continue
                self.QUEUE_STORAGES.detected_parent_orders_queue.task_done()
