# run init.sql before this to create tables with the right schema.

# Goals:
# - remove fully null columns (3,4,5,6,7)
# - convert address to city and district only
# - show file being converted
# - show indicator for number of lines converted

# import sys
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


# for filename in sys.argv[1:]:
for filename in [
                 "e-commerce_data\電商數據\order_2011Q1.csv",
                 "e-commerce_data\電商數據\order_2011Q2.csv",
                 "e-commerce_data\電商數據\order_2011Q3.csv",
                 "e-commerce_data\電商數據\order_2011Q4.csv",
                 "e-commerce_data\電商數據\order_2012Q1.csv",
                 "e-commerce_data\電商數據\order_2012Q2.csv",
                 ]:
    print("Correcting "+filename[-16:])
    with open(filename,newline='') as infile,psycopg2.connect(
                host = hostname,
                dbname = database,
                user = username,
                password = pwd,
                port = port_id) as conn: #, open(filename[:-4]+'_corrected.csv','w',newline='') as outfile:
            cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            header = next(csv.reader([infile.readline()]))
            tname = filename[-16:-4]
            print("table:",tname)
            for idx, line in enumerate(infile):
                row = next(csv.reader([line]))
                if idx % 100000 == 0:
                    print(idx,"lines done")
                if len(row) != len(header):
                    continue
                addr = row[15]
                city = 'NULL'
                if c := re.search('(..)市',addr):
                    city = c.group(1)
                dist = 'NULL'
                if d := re.search('(..)[區鎮]',addr):
                    dist = d.group(1)
                new_row = row[0:2]+row[7:15]+[city,dist]+row[16:]
                final_row = []
                for i in new_row:
                    if i == 'NULL':
                        final_row.append(None)
                    else:
                        final_row.append(i) 
                cur.execute("insert into "+tname+" values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", final_row)




