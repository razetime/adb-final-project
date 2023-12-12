import csv
import re
import psycopg2
import psycopg2.extras


hostname = 'localhost' #information from postgresql servers
database = 'adb_final'
username = 'postgres'
pwd = 'a'
port_id = 5432
conn = None

def findcd(addr):
    city = None
    if c := re.search('(..)市',addr):
        city = c.group(1)
    dist = None
    if d := re.search('(..)[區鎮]',addr):
        dist = d.group(1)
    return (city,dist)

with open("e-commerce_data\\電商數據\\2_商品檔\\(商品主檔)sku_20120413\\(�ӫ~�D��)sku_20120413.csv",newline='') as infile,psycopg2.connect(
                host = hostname,
                dbname = database,
                user = username,
                password = pwd,
                port = port_id) as conn:
    cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    header = next(csv.reader([infile.readline()]))
    for idx, line in enumerate(infile):
        row = next(csv.reader([line]))
        if len(row) != len(header):
            continue
        # new_row = [*row[0:3],*findcd(row[3]),row[4],*findcd(row[5])]
        # final_row = []
        # for i in new_row:
        #     if i == '':
        #         final_row.append(None)
        #     else:
        #         final_row.append(i) 
        # print(final_row[1])
        try:
            cur.execute("insert into sku_20120413 values (%s,%s,%s,%s,%s,%s,%s,%s,%s)", row)
        except:
            print("err", idx)
