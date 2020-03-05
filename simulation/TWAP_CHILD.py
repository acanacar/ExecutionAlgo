class TWAP_CHILD(object):
    def __init__(self, order_time, order_quantity, sliced_no, parent_code, status):
        self.order_time = order_time
        self.order_quantity = order_quantity
        self.sliced_no = sliced_no
        self.parent_code = parent_code
        self.status = 'waiting'
        self.order_quantity_done = 0
        self.order_type = 'limit'

    def activate_order(self):
        self.status = 'live'

    def send_order(self):
        self.activate_order()
        pass

    def modify_order(self):
        pass

    def cancel_order(self):
        pass