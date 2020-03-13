import datetime
import time


class TWAP_CHILD(object):
    def __init__(self, order_time, security_id, user_id, side,
                 order_quantity, sliced_no, parent_code, status):
        self.order_time = order_time
        self.side = side
        self.security_id = security_id
        self.user_id = user_id
        self.order_quantity = order_quantity
        self.sliced_no = sliced_no
        self.parent_code = parent_code
        self.status = status
        self.order_quantity_done = 0
        self.order_type = 2  # 1- Market 2- Limit 3- Market Limit Market(MLM)
        # 4- Market To Limit(MTL) 5- Best Limit(BL) 6- Limit To Market (LTM)
        self.order_price = 9
    def activate_order(self):
        self.status = 3

    def send_order(self):
        ts = time.time()
        order_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        return 'success'

    def modify_order(self):
        pass

    def cancel_order(self):
        pass

    def modify_quantity(self, new_quantity):
        self.order_quantity = new_quantity
