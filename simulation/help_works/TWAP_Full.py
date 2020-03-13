from collections import namedtuple
import pandas as pd


class TWAP(object):
    Child = namedtuple('Child',
                       ['sliced_no', 'quantity', 'parent_code'])

    def get_time_horizon(self):
        return None

    def get_interval_count(self):
        return None

    def get_interval_time(self):
        return None

    def __init__(self, symbol,
                 parent_order_quantity,
                 start_time, end_time,
                 side,
                 interval,
                 i_would_price,
                 adaptive_variance,
                 left_over_action='leave',
                 price_type=None,  # ltp,bid,ask,SameSide,OppositeSide
                 price_mode=None,  # Fixed,relative
                 offsets=None
                 ):
        '''Initializes a new instance of the VolumeWeightedAveragePriceExecutionModel class'''
        self.symbolData = symbol
        self.start_time = start_time
        self.end_time = end_time
        # self.time_horizon = TWAP.get_time_horizon(self)
        self.interval_count = TWAP.get_interval_count()
        self.interval_time = TWAP.get_interval_time()
        self.parent_order_quantity = parent_order_quantity
        self.adaptive_variance = adaptive_variance
        self.side = side
        self.i_would_price = i_would_price
        self.set_child_order_quantity()
        self.child_orders = []
        self.parent_code = 'sss'
        self.left_over_action = left_over_action
        # leave => Leaves the resting child order portion in the market
        # merge => Cancels the resting child order portion and submits a new order equal to the sum of the canceled quantity plus the next disclosed order portion at the specified price level
        # market => Cancels the resting child order portion and submits a market order for the remaining quantity
        # payup => Cancels the resting child order portion and submits a limit order for the remaining quantity; the limit price is based upon the buy/sell direction of the order and the Payup Ticks value

    def set_child_order_quantity(self):
        self.child_order_quantity = self.child_order_quantity

    def create_child_orders(self):
        for interval_no in range(1, self.interval_count + 1):
            self.child_orders.append(TWAP.Child(interval_no, self.child_order_quantity, self.parent_code))

    def cancel_parent_order(self):
        pass

    def modify_the_fixed_price(self):
        """
        If the synthetic order is an Iceberg,
        Timed Sliced, or Volume Sliced
        order, changing the price limit only
        applies to child orders submitted
        after the change."""

        pass


twap_1 = TWAP(symbol='AKBNK',
              parent_order_quantity=8000,
              start_time=pd.to_datetime('2017-01-03 10:00'),
              end_time=pd.to_datetime('2017-01-03 13:00'),
              side='B',
              i_would_price=8.50,
              adaptive_variance=.5
              )
