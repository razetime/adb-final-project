import psycopg2
import psycopg2.extras


hostname = 'localhost'
database = 'adb_final'
username = 'postgres'
pwd = 'a'
port_id = 5432
conn = None

def query_purchases_district_cities(type,year,quarter,query_arr):
    with psycopg2.connect(
                    host = hostname,
                    dbname = database,
                    user = username,
                    password = pwd,
                    port = port_id,
                    connect_timeout = 3) as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        match type:
            case 0:
                cur.execute(f"""SELECT delivery_city,delivery_district,COUNT(product_number)
                                FROM order_{year}Q{quarter}
                                WHERE
                                    EXTRACT(MONTH FROM order_establishment_time) = %s AND 
                                    product_number = %s
                                    AND delivery_city = %s
                                GROUP BY delivery_city,delivery_district;""",query_arr)
                return cur.fetchall()
                

print(query_purchases_district_cities(0,2011,1,[1,1199969,'基隆']))