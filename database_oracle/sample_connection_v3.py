import cx_Oracle

username = 'INTERNET'
password = 'M'
ip = '172.30.0.10'
port = 1521
encoding = 'UTF-8'
sid = 'DEV'

con = cx_Oracle.connect('{}/{}@{}:{}/{}'.format(username, password, ip, port, sid))

cur = con.cursor()

child_no = '26730080'
p_miktar = 15
p_fiyat_tipi = 2
p_fiyat = 11
p_sure_tipi = 0
user = 'EALGO'

V_STR = cur.var(str)

res = cur.callfunc('PKG_ALGO.emirler_ilet',
                   cx_Oracle.STRING,
                   [child_no, p_miktar, p_fiyat_tipi, p_fiyat, p_sure_tipi, user]
                   )
