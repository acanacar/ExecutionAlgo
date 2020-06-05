from dev.export_libraries import *
from oop_study.oop_dev.TWAP_CALCULATOR import *


class TWAP_EXECUTOR:
    def __init__(self, queue_storages, order_storages, var_storages):
        self.loop = asyncio.get_event_loop()

        self.ORDER_STORAGES = order_storages
        self.VAR_STORAGES = var_storages
        self.QUEUE_STORAGES = queue_storages

        # self.algo_children_lock = asyncio.Lock()
        self.algo_parents_lock = asyncio.Lock()
        self.schedule_task()
        self.TWAP_CALCULATOR = TWAP_CALCULATOR

    def schedule_task(self):
        self.loop.create_task(self.algo_parent_consume())
        self.loop.create_task(self.process_detected_child())

    async def execute(self, child_order):
        """
        Sending twap order that have passed to ORACLE_DB
        :type child_order: object
        :param child_order: twap child order
        """
        print(f"Emir is executing, {child_order.parent_order_no}-{child_order.sliced_no}")
        try:
            TWAP_CALCULATOR = self.TWAP_CALCULATOR(symbol=child_order.security_id,
                                                   var_storages=self.VAR_STORAGES,
                                                   last_n_minutes=child_order.parent_slice_interval)
            await TWAP_CALCULATOR.calculate_twap()

            child_order.trade(twap_=TWAP_CALCULATOR.twap_val)

            if child_order.order_no is not None and child_order.status == 1:
                with await self.algo_parents_lock:
                    related_parent = self.ORDER_STORAGES.algo_parents[child_order.parent_order_no]
                    related_parent.child_orders_islem.update({child_order.sliced_no: child_order})

        except Exception as e:
            print(str(e))

    def schedule_execution(self, child_order):
        loop_time = self.loop.time()
        if 1000 > child_order.remaining_seconds_to_order > 0:
            print('-' * 20, child_order.remaining_seconds_to_order, '-' * 20)
        else:
            print(f"{'!' * 10} {child_order.remaining_seconds_to_order} seconds "
                  f"{child_order.parent_order_no}-{child_order.sliced_no} {'!' * 10}")
        self.loop.call_at(loop_time + child_order.remaining_seconds_to_order,
                          asyncio.create_task,
                          self.execute(child_order))

        logging.info(
            f'current time of loop: {loop_time}'
            f'\nremaining seconds: {child_order.remaining_seconds_to_order}\nexecution time: {child_order.order_time}')

    async def algo_parent_consume(self):
        '''New Algo Parent lar ORDER_STORAGES'a depolanir ve child orderlar schedule edilir'''
        while True:
            algo_parent = await self.QUEUE_STORAGES.algo_parent_queue.get()
            if algo_parent:
                with await self.algo_parents_lock:

                    self.ORDER_STORAGES.algo_parents[algo_parent.order_no] = algo_parent

                for child_order in algo_parent.child_orders:
                    ''' zamani gecmemis child orderlar basiliyor.
                     zamani gecmemis parent orderlar olarak degistirilebilir.'''
                    if child_order.remaining_seconds_to_order > 0:
                        self.schedule_execution(child_order)
                self.QUEUE_STORAGES.algo_parent_queue.task_done()

    def find_related_child_order(self, child_order):
        order_no = child_order['order_no']
        parent_order_no = child_order['pr_order_no']
        related_parent = self.ORDER_STORAGES.algo_parents[parent_order_no]
        twap_child_obj = [child for child in related_parent.child_orders_islem.values() if
                          child.order_no == order_no][0]
        return twap_child_obj

    async def update_related_child_order(self, order, detected_child_msg):
        with await self.algo_parents_lock:
            order.update(child_from_db=detected_child_msg)

    async def process_detected_child(self):
        detected_child_order_queue = self.QUEUE_STORAGES.detected_child_order_queues['TWAP']
        while True:
            child_order = await detected_child_order_queue.get()
            if child_order:

                try:

                    if child_order['pr_order_no'] in self.ORDER_STORAGES.algo_parents:
                        twap_child_obj = self.find_related_child_order(child_order)
                        await self.update_related_child_order(order=twap_child_obj, detected_child_msg=child_order)

                except Exception as e:
                    logging.exception(e)

                self.QUEUE_STORAGES.detected_child_order_queue.task_done()
