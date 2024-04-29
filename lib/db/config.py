import psycopg2

try:
    conn = psycopg2.connect(dbname='postgres',user='postgres', host='localhost')
    cursor = conn.cursor()
except:
    print('Can`t establish connection to database')
