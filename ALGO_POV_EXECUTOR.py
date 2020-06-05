from dev.export_libraries import *
from oop_study.oop_dev.TWAP_CALCULATOR import *


class POV_EXECUTOR:
    def __init__(self, ws, queue_storages, order_storages, var_storages):
        self.loop = asyncio.get_event_loop()
        self.ws = ws

        self.ORDER_STORAGES = order_storages
        self.VAR_STORAGES = var_storages
        self.QUEUE_STORAGES = queue_storages

        # self.algo_children_lock = asyncio.Lock()
        self.algo_parents_lock = asyncio.Lock()
        self.schedule_task()
        # self.POV_CALCULATOR = POV_CALCULATOR

    def schedule_task(self):
        self.loop.create_task(self.algo_parent_consume())
        self.loop.create_task(self.process_detected_child())
        self.loop.create_task(self.check_vol())

    async def check_vol(self):
        while True:
            await asyncio.sleep(.001)

    async def execute(self, child_order):
        """
        Sending twap order that have passed to ORACLE_DB
        :type child_order: object
        :param child_order: twap child order
        """
        print(f"Emir is executing, {child_order.parent_order_no}-{child_order.sliced_no}")
        try:
            POV_CALCULATOR = self.POV_CALCULATOR(symbol=child_order.security_id,
                                                 var_storages=self.VAR_STORAGES,
                                                 last_n_minutes=child_order.parent_slice_interval)
            await POV_CALCULATOR.calculate_pov()

            child_order.trade(twap_=TWAP_CALCULATOR.twap_val)

            if child_order.order_no is not None and child_order.status == 1:
                with await self.algo_parents_lock:
                    related_parent = self.ORDER_STORAGES.algo_parents[child_order.parent_order_no]
                    related_parent.child_orders_islem.update({child_order.sliced_no: child_order})

        except Exception as e:
            print(str(e))

    async def schedule_execution(self, algorithm):
        loop_time = self.loop.time()
        print("algorithm.remaining_seconds_to_order -> ", algorithm.remaining_seconds_to_order)
        if 1000 > algorithm.remaining_seconds_to_order > -200:
            print('-' * 20, algorithm.remaining_seconds_to_order, '-' * 20)
        # self.loop.call_at(loop_time + algorithm.remaining_seconds_to_order,
        #                   algorithm.start)
        self.loop.call_at(loop_time + 5,
                          algorithm.start)
        logging.info(
            f'current time of loop: {loop_time}'
            f'\nremaining seconds: {algorithm.remaining_seconds_to_order}\nexecution time: {algorithm.start_time}')

    async def update_related_pov_order(self, detected_child_order_msg):
        related_parent = self.ORDER_STORAGES.algo_parents[detected_child_order_msg['pr_order_no']]
        with await self.algo_parents_lock:
            related_parent.update(detected_child_order_msg=detected_child_order_msg)

    async def algo_parent_consume(self):
        '''New Algo Parent lar ORDER_STORAGES'a depolanir ve child orderlar schedule edilir'''
        while True:
            algo_parent = await self.QUEUE_STORAGES.algo_parent_pov_queue.get()
            if algo_parent:
                with await self.algo_parents_lock:
                    self.ORDER_STORAGES.algo_parents[algo_parent.order_no] = algo_parent
                if algo_parent.remaining_seconds_to_order > -1000:
                    await self.schedule_execution(algo_parent)
                # schdule twap hacim takip eden bi trader a donusmeli
                self.QUEUE_STORAGES.algo_parent_pov_queue.task_done()

    async def process_detected_child(self):
        detected_child_order_queue = self.QUEUE_STORAGES.detected_child_order_queues['POV']
        while True:
            child_order = await detected_child_order_queue.get()
            if child_order:
                try:

                    if child_order['pr_order_no'] in self.ORDER_STORAGES.algo_parents:
                        await self.update_related_pov_order(detected_child_order_msg = child_order)

                except Exception as e:
                    logging.exception(e)

                detected_child_order_queue.task_done()
