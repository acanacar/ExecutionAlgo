from oracle_db.connection import *
from Orders.TWAP import *

twap_1 = TWAP(security_id='AKBNK',
              parent_order_quantity=800,
              start_time=pd.to_datetime('2017-01-03 10:10'),
              end_time=pd.to_datetime('2017-01-03 10:30'),
              side='B',
              one_slice_interval_as_minutes=.5)

parent_orders = [twap_1]
for i, parent_order in enumerate(parent_orders):
    parent_order.parent_code = 'parent_{}'.format(i)
    parent_order.user_id = 'user_{}'.format(i)
    parent_order.create_child_orders()

child = twap_1.child_orders[0]

res = emir_ilet(
    # child_no='{}_{}'.format(child.parent_code, child.sliced_no),
    p_miktar=child.order_quantity,
    p_fiyat_tipi=2,
    p_fiyat=child.order_price,
    p_sure_tipi=0,
    user='EALGO')

[ans, status, x, y, z] = res.split(';')
if ans == 'OK':
    print('Child Order is Sent to DB')


