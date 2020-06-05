from dev.export_libraries import *
from dev.helpers.config import config
from dev.oracle_db.send_child_order import send_child_order
from dev.utils.truncate import truncate


class TWAP_CHILD(object):
    def __init__(self, order_time, security_id, user_id, side,
                 order_quantity, sliced_no, parent_code,
                 parent_start_time, parent_end_time, parent_order_no,
                 parent_slice_interval, status):
        self.order_time = order_time
        self.side = side
        self.security_id = security_id
        self.user_id = user_id
        self.order_quantity = order_quantity
        self.sliced_no = sliced_no
        self.parent_code = parent_code
        self.parent_order_no = parent_order_no
        self.parent_start_time = parent_start_time
        self.parent_end_time = parent_end_time
        self.parent_slice_interval = parent_slice_interval
        self.status = status
        self.order_type = 2  # 1- Market 2- Limit 3- Market Limit Market(MLM)
        # 4- Market To Limit(MTL) 5- Best Limit(BL) 6- Limit To Market (LTM)
        self.order_price = 9
        self.twap = 9
        self.order_quantity_left = order_quantity
        self.updates = []
        self.order_response = None
        self.order_no = None

    @property
    def order_quantity(self):
        return self._order_quantity

    @property
    def order_response(self):
        return self._order_response

    @property
    def order_price(self):
        return self._order_price

    @property
    def order_quantity_done(self):
        return self.order_quantity - self.order_quantity_left

    @property
    def twap(self):
        return self._twap

    @property
    def order_quantity_left(self):
        return self._order_quantity_left

    @property
    def status(self):
        return self._status

    @twap.setter
    def twap(self, value):
        self._twap = value

    @order_price.setter
    def order_price(self, value):
        self._order_price = value

    @order_quantity.setter
    def order_quantity(self, value):
        self._order_quantity = value

    @status.setter
    def status(self, value):
        if hasattr(self, "status") and value != self.status:
            print(f'Status will change from {self.status} to {value}')
        self._status = value

    @order_quantity_left.setter
    def order_quantity_left(self, value):
        if hasattr(self, "order_quantity_left") and value != self.order_quantity_left:
            print(f'order_quantity_left will change from {self.order_quantity_left} to {value}')
        self._order_quantity_left = value

    @order_response.setter
    def order_response(self, value):
        self._order_response = value

    def console_trade_execution(self, child_from_db):
        print('TRADE EXECUTION !!! ')
        print(
            f'****  {self.parent_order_no}:: {self.order_no} Executed !!! '
            f'Total Quantity: {self.order_quantity}'
            f'\nOld Quantity Left:{self.order_quantity_left} '
            f'New Quantity Left: {int(child_from_db["left"])} ****')

    def manipulate_order_price(self):
        print(f'manipulating order price {self.order_price}')
        if self.side == 'A':
            self.order_price = truncate(self.order_price + .1, 2)
        else:
            self.order_price = truncate(self.order_price - .1, 2)

    def update(self, child_from_db):
        self.updates.append(child_from_db)

        status_ = int(child_from_db['status'])
        new_left_quantity_ = int(child_from_db['left'])
        exec_amount_ = float(child_from_db['exec_amount'].replace(',', '.'))

        if exec_amount_ > 0:
            self.console_trade_execution(child_from_db)

        self.status = status_
        self.order_quantity_left = new_left_quantity_

    def send_order(self):
        params = config(section='oracledb')
        with cx_Oracle.connect(
                f"{params['username']}/{params['password']}@{params['ip']}:{params['port']}/{params['sid']}") as con:
            cur = con.cursor()
            res = send_child_order(parent_order_no=self.parent_order_no,
                                   p_miktar=int(self.order_quantity),
                                   p_fiyat=self.order_price,
                                   p_fiyat_tipi=self.order_type,
                                   cur=cur)
            con.commit()
        return res

    def console_order_sent(self):
        logging.debug(f"Child order iletildi ve open_twap_children objesine kaydedildi.")
        print(f"{'-' * 40}\n ILETILMIS EMIR :")
        pp(self.__dict__)
        logging.info(f"SUBMITTED ORDER @ {pd.Timestamp.now('Europe/Istanbul')} !!!")
        logging.info(f"sent order -> {self.__dict__}")

    def handle_order_response(self):
        res_status, res_order_no = self.order_response.split(';')[0], self.order_response.split(';')[2]

        if res_status == 'OK':
            self.status = 1
            self.order_no = res_order_no
            self.console_order_sent()

        elif res_status == "ER":
            print(f'Emir Iletilemedi. Response: {self.order_response}')
            print(f'Iletilemeyen Emir : {self.__dict__}')

        else:
            print(f'ANOTHER RETURN CODE FROM SEND_ORDER_TO_ORACLE_DB => {res_status} ')

    @property
    def remaining_seconds_to_order(self):
        return (self.order_time - pd.Timestamp.now('Europe/Istanbul')).total_seconds()

    def trade(self, twap_):
        self.twap = twap_
        self.order_price = truncate(self.twap, 2)
        self.manipulate_order_price()
        res = self.send_order()
        self.order_response = res
        self.handle_order_response()
