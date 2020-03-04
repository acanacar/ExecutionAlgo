from simulation.TWAP import *

twap_1 = TWAP(symbol='AKBNK',
              parent_order_quantity=8000,
              start_time=pd.to_datetime('2017-01-03 10:00'),
              end_time=pd.to_datetime('2017-01-03 13:00'),
              side='B',
              one_slice_interval_as_minutes=10)

twap_1.create_child_orders()
for i in twap_1.child_orders:
    print(i)
print('x')
