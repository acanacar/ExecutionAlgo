from collections import namedtuple


class TWAP(object):
    Child = namedtuple('Child',
                       ['sliced_no', 'quantity', 'parent_code'])

    def get_time_horizon(self):
        return None

    def get_interval_count(self):
        return None

    def get_interval_time(self):
        return None

    def __init__(self, parent_order_quantity, start_time, end_time, i_would_price):
        '''Initializes a new instance of the VolumeWeightedAveragePriceExecutionModel class'''
        self.time_horizon = TWAP.get_time_horizon()
        self.symbolData = {}
        self.start_time = self.start_time
        self.end_time = self.end_time
        self.parent_order_quantity = self.parent_order_quantity
        self.side = self.side
        self.interval_count = TWAP.get_interval_count()
        self.interval_time = TWAP.get_interval_time()
        self.i_would_price = self.i_would_price()
        self.set_child_order_quantity()
        self.child_orders = []

    def set_child_order_quantity(self):
        self.child_order_quantity = self.child_order_quantity

    def create_child_orders(self):
        for i in range(1, self.interval_count + 1):

            pass
