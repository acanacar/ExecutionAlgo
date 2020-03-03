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

    def __init__(self, symbol, parent_order_quantity, start_time, end_time, side, i_would_price, left_over_action):
        '''Initializes a new instance of the VolumeWeightedAveragePriceExecutionModel class'''
        self.time_horizon = TWAP.get_time_horizon()
        self.symbolData = symbol
        self.start_time = start_time
        self.end_time = end_time
        self.parent_order_quantity = parent_order_quantity
        self.side = side
        self.interval_count = TWAP.get_interval_count()
        self.interval_time = TWAP.get_interval_time()
        self.i_would_price = self.i_would_price()
        self.set_child_order_quantity()
        self.child_orders = []
        self.parent_code = 'sss'
        self.left_over_action = left_over_action

    def set_child_order_quantity(self):
        self.child_order_quantity = self.child_order_quantity

    def create_child_orders(self):
        for interval_no in range(1, self.interval_count + 1):
            self.child_orders.append(TWAP.Child(interval_no, self.child_order_quantity, self.parent_code))
