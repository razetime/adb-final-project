import psycopg2
import psycopg2.extras
import re

hostname = 'localhost'
database = 'adb_final'
username = 'postgres'
pwd = 'a'
port_id = 5432
conn = None

def db_retrieve(func):
    def db_wrapper(*args, **kwargs):
        conn = psycopg2.connect(
            host = hostname,
            dbname = database,
            user = username,
            password = pwd,
            port = port_id,
            connect_timeout = 3)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        func(cur,*args,**kwargs)
        ret = cur.fetchall()
        cur.close()
        conn.close()
        return ret
    return db_wrapper

@db_retrieve
def query_purchase_numbers(cur,year,quarter,query_arr):
    # query_arr = [month number, product number, delivery city]
    cur.execute(f"""SELECT json_build_object(
                        'type',       'Feature',
                        'id',         gid,
                        'geometry',   ST_AsGeoJSON(geom)::json,
                        'properties', json_build_object(
                            'city', delivery_city,
                            'district', delivery_district,
                            'count', cnt,
                            'feat_area', ST_Area(geom)
                        )
                    ) FROM (
                    SELECT ord.delivery_city,ord.delivery_district,ord.cnt,gid,geom
                    FROM gadm41_twn_2
                    RIGHT JOIN (
                        SELECT delivery_city,delivery_district,COUNT(product_number) as cnt
                        FROM order_{year}Q{quarter}
                        WHERE
                            EXTRACT(MONTH FROM order_establishment_time) = %s AND 
                            product_number = %s
                            AND delivery_city = %s
                        GROUP BY delivery_city,delivery_district
                    ) as ord
                    ON delivery_city = left(nl_name_2,2)
                    ) as tbl;""",query_arr)
                
@db_retrieve
def query_cities(cur):
    cur.execute("SELECT distinct delivery_city from cities;")

# print(query_purchase_numbers(2011,1,[1,1199969,'基隆']))
print([i[0] for i in query_cities() if i[0] and not re.search("[a-zA-Z0-9\(\) 〈（]",i[0])])