import cx_Oracle
from oracle_db import config as cfg

'''
DECLARE
V_STR VARCHAR2(4000);

BEGIN
    V_STR:=PKG_ALGO.emirler_ilet(
        '26730080',
        15,--p_miktar number,
        2,--p_fiyat_tipi varchar2,-- 1-MARKET,2-LİMİT
        11,--p_fiyat number,
        0,--p_sure_tipi varchar2, -- 0 - GÜN, 3 - KİE
        'EALGO'
    );

dbms_output.put_line('Value of V_STR='||V_STR);
END;
'''


def emir_ilet(child_no='26730080', p_miktar=15, p_fiyat_tipi=2, p_fiyat=11, p_sure_tipi=0, user='EALGO'):
    config = cfg.config_1
    try:
        # create a connection to the Oracle Database
        with cx_Oracle.connect('{}/{}@{}:{}/{}'.format(config['username'],
                                                       config['password'],
                                                       config['ip'],
                                                       config['port'],
                                                       config['sid'])) as connection:
            with connection.cursor() as cursor:
                res = cursor.callfunc('PKG_ALGO.emirler_ilet',
                                      cx_Oracle.STRING,
                                      [child_no, p_miktar, p_fiyat_tipi, p_fiyat, p_sure_tipi, user])
                return res

    except cx_Oracle.Error as error:
        print(error)

# if __name__ == '__main__':
#     x = emir_ilet()
#     print(x)
