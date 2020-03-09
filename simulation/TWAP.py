import pandas as pd
from simulation.TWAP_CHILD import *


class TWAP(object):

    def __init__(self, start_time, end_time,
                 security_id,
                 parent_order_quantity,
                 side,
                 one_slice_interval_as_minutes,
                 user_id = 'user_default',
                 left_over_action=3,  # 1- Leave 2- Merge 3- Market 4- Payup
                 ):
        self.security_id = security_id
        self.user_id = user_id
        self.side = side
        self.start_time = start_time if start_time is not None else pd.to_datetime('2017-01-03 10:00')
        self.end_time = end_time if end_time is not None else pd.to_datetime('2017-01-03 18:00')
        self.left_over_action = left_over_action
        self.one_slice_interval = one_slice_interval_as_minutes
        self.one_slice_interval_as_seconds = one_slice_interval_as_minutes * 60

        self.parent_order_quantity = parent_order_quantity
        self.set_twap_time_horizon()
        self.set_interval_count()
        self.set_child_order_quantity()
        self.child_orders = []
        self.status = 1
        # 1- Waiting
        # 2- Pending Trigger
        # 3- Working
        # 4- Hold
        # 5- Paused
        # 6- Deleting
        # 7- Filled
        # 8- Available
        # 9- Owned
        # 10- Pulling
        # 11- Unmanaged
        # 12- Initializing
        # 13- Recovering
        self.parent_code = 'sss'
        self.executed_quantity  = 0
        self.working_quantity = 0
        self.undisclosed_quantity = parent_order_quantity
        self.algo_name = 'twap'
        self.algo_stage = 1  # 1 - running 2 - paused 3 - deleting

    def modify_quantity(self, new_quantity):
        if self.algo_stage == 1:  # running
            self.parent_order_quantity = new_quantity

    def set_twap_time_horizon(self):
        self.twap_time_horizon_as_seconds = int((self.end_time - self.start_time).seconds)
        self.twap_time_horizon_as_minutes = self.twap_time_horizon_as_seconds / 60

    def set_interval_count(self):
        self.interval_count = int(self.twap_time_horizon_as_minutes / self.one_slice_interval)

    def set_child_order_quantity(self):
        self.child_order_quantity = self.parent_order_quantity / self.interval_count

    def get_order_submit_times(self):
        '''
        :return: child orderslara ait order time lar.
        '''
        last_child_order_submit_time = self.start_time + \
                                       pd.DateOffset(seconds=
                                                     self.interval_count * self.one_slice_interval_as_seconds)
        order_submit_times = pd.date_range(start=self.start_time,
                                           end=last_child_order_submit_time,
                                           periods=self.interval_count + 1,
                                           closed='right')
        return order_submit_times

    def get_order_quantities(self):
        leap = self.parent_order_quantity % self.interval_count
        q1 = (self.parent_order_quantity - leap) / self.interval_count
        return (self.interval_count - 1) * [q1] + \
               [q1 + leap]

    def create_child_orders(self):
        order_submit_times = self.get_order_submit_times()

        order_quantities = self.get_order_quantities()
        self.child_orders = [TWAP_CHILD(order_time=order_submit_time,
                                        security_id=self.security_id,
                                        user_id=self.user_id,
                                        side=self.side,
                                        order_quantity=order_quantity,
                                        sliced_no=order_idx,
                                        parent_code=self.parent_code,
                                        status=1)
                             for order_idx, (order_submit_time, order_quantity) in
                             enumerate(zip(order_submit_times, order_quantities), start=1)]
        self.child_orders_islem = self.child_orders.copy()
