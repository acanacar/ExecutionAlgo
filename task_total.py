import asyncio

from oop_study.oop_dev.ALGO_DETECTOR import ALGO_DETECTOR
from oop_study.oop_dev.ALGO_MESSAGE_GET import FXPLUS_MESSENGER
from oop_study.oop_dev.ALGO_POV_EXECUTOR import POV_EXECUTOR
from oop_study.oop_dev.ALGO_PROCESSOR import ALGO_PROCESSOR
from oop_study.oop_dev.ALGO_RESPONSE_CREATOR import RESPONSE_CREATOR
from oop_study.oop_dev.ALGO_TWAP_EXECUTOR import TWAP_EXECUTOR


class TASK_TOTAL:

    def __init__(self, ws, var_storages, queue_storages, order_storages):
        self.loop = asyncio.get_event_loop()
        self.VAR_STORAGES = var_storages
        self.ORDER_STORAGES = order_storages
        self.QUEUE_STORAGES = queue_storages

        self.messager = FXPLUS_MESSENGER(ws, self.QUEUE_STORAGES.fx_plus_messages_queue)
        self.message_handler = RESPONSE_CREATOR(self.QUEUE_STORAGES.fx_plus_messages_queue, self.VAR_STORAGES)

        self.twap_listener = ALGO_DETECTOR(queue_storages=self.QUEUE_STORAGES, query_frequency=1)

        self.parent_processor = ALGO_PROCESSOR(ws=ws,
                                               var_storages=self.VAR_STORAGES,
                                               queue_storages=self.QUEUE_STORAGES,
                                               algo_parents=self.ORDER_STORAGES.algo_parents)

        self.twap_executor = TWAP_EXECUTOR(
            queue_storages=self.QUEUE_STORAGES,
            order_storages=self.ORDER_STORAGES,
            var_storages=self.VAR_STORAGES)
        self.pov_executor = POV_EXECUTOR(
            ws=ws,
            queue_storages=self.QUEUE_STORAGES,
            order_storages=self.ORDER_STORAGES,
            var_storages=self.VAR_STORAGES)
