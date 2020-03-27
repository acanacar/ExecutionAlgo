import cx_Oracle

username = 'INTERNET'
password = 'M'
ip = '172.30.0.10'
port = 1521
encoding = 'UTF-8'
sid = 'DEV'

con = cx_Oracle.connect('{}/{}@{}:{}/{}'.format(username, password, ip, port, sid))
ver = con.version.split(".")

con.close()

