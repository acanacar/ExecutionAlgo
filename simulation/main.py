from simulation.TWAP import *


date1 = '2017-01-03'
date2 = '2017-01-04'

x = pd.date_range(date1, date2, freq='1s')
x = x[x.indexer_between_time('10:00', '11:00')]


twap_1 = TWAP(symbol='AKBNK',
              parent_order_quantity=800,
              start_time=pd.to_datetime('2017-01-03 10:10'),
              end_time=pd.to_datetime('2017-01-03 10:30'),
              side='B',
              one_slice_interval_as_minutes=.5)

twap_2 = TWAP(symbol='AKBNK',
              parent_order_quantity=1000,
              start_time=pd.to_datetime('2017-01-03 10:03'),
              end_time=pd.to_datetime('2017-01-03 10:20'),
              side='B',
              one_slice_interval_as_minutes=.5)

twap_1.create_child_orders()
twap_2.create_child_orders()

parent_orders = [twap_1,twap_2]
for i in twap_1.child_orders:
    print(i.__dict__)



for time in x:
    for parent_order in parent_orders:
        if parent_order.start_time == time:
            parent_order.status = 'working'
        for child_order in parent_order.child_orders_islem:
            if child_order.order_time == time:
                child_order.send_order()
                child_order.status = 'working'

                print(time)
