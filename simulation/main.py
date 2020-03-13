from Orders.TWAP import *

date1 = '2017-01-03'
date2 = '2017-01-04'

times = pd.date_range(date1, date2, freq='1s')
times = times[times.indexer_between_time('10:00', '11:00')]

twap_1 = TWAP(security_id='AKBNK',
              parent_order_quantity=800,
              start_time=pd.to_datetime('2017-01-03 10:10'),
              end_time=pd.to_datetime('2017-01-03 10:30'),
              side='B',
              one_slice_interval_as_minutes=.5)

twap_2 = TWAP(security_id='AKBNK',
              parent_order_quantity=1000,
              start_time=pd.to_datetime('2017-01-03 10:03'),
              end_time=pd.to_datetime('2017-01-03 10:20'),
              side='B',
              one_slice_interval_as_minutes=.5)

parent_orders = [twap_1, twap_2]
for i, parent_order in enumerate(parent_orders):
    parent_order.parent_code = 'parent_{}'.format(i)
    parent_order.user_id = 'user_{}'.format(i)
    parent_order.create_child_orders()

for i in twap_1.child_orders:
    print(i.__dict__)

for time in times:
    for parent_order in parent_orders:
        if parent_order.start_time == time:
            parent_order.status = 3
        for child_order in parent_order.child_orders_islem:
            if child_order.order_time == time:
                child_order.activate_order()
                res = child_order.send_order()
                if res is 'success':
                    parent_order.undisclosed_quantity -= child_order.order_quantity
                    parent_order.working_quantity += child_order.order_quantity
                else:
                    print('ORDER GONDERILEMEDI')
                res, amount = child_order.get_trade_status()
                if res is 'full-filled':
                    child_order.status = 7
                    parent_order.executed_quantity += child_order.order_quantity
                    parent_order.working_quantity -= child_order.order_quantity
                elif res is 'partial-fill':
                    parent_order.executed_quantity += amount
                    parent_order.working_quantity -= amount
                else:
                    print('CHILD ORDER FILL OLAMADI')
                print(time)
