import os
from dotenv import load_dotenv
from . import get_queries_strings as qtool

load_dotenv()
return_query_no_params = qtool.return_query_no_params

# consts:
ALL_NODE_TYPES = ("Order", "Product")
ORDER_FILES = ["order_2012Q1","order_2012Q2",
               "order_2011Q1","order_2011Q2","order_2011Q3","order_2011Q4"]
CANCELLED_ORDERS_FILES=["4_Φ¿éσû«σÅûµ╢ê\\cancel_order"]
PRODUCT_FILES = ["2_σòåσôüµ¬ö\\product(σÇëσç║)"]
SUPPLIERS_FILES = ["1_Σ╛¢µçëσòå\\supplier"]
SUPPLIERS_FILES = ["1_Σ╛¢µçëσòå\\supplier"]
PARENT_FOLDER = os.getenv('PARENT_FOLDER')

def get_one_order():
    return return_query_no_params("MATCH (o:Order) RETURN o LIMIT 1")
    
def get_one_product():
    return return_query_no_params("MATCH (p:Product) RETURN p LIMIT 1")

def get_one_cancel_order():
    return return_query_no_params("MATCH (c:CancelledOrder) RETURN c LIMIT 1")
    
def get_delete_all():
    return return_query_no_params(f'MATCH (n) WHERE (n:{" OR n:".join(ALL_NODE_TYPES)}) DETACH DELETE n')

def get_add_order_csv_files():
    query=""
    for i in ORDER_FILES:
        query += "\nLOAD CSV WITH HEADERS FROM 'file:///"+ PARENT_FOLDER + i + """.csv' as ord
        CALL {
            WITH ord
            OPTIONAL MATCH (prod:Product {id: ord.商品編號})    
            CREATE (ord_node:Order {id: ord.訂單編號, sub_ord:ord.子單編號, user: ord.客戶代號, del_adr: ord.到貨地址})
            FOREACH(_ IN CASE WHEN prod IS NOT NULL THEN [1] END | CREATE (ord_node)-[:PRODUCT]->(prod))
        } IN TRANSACTIONS OF 100000 ROWS"""

    return return_query_no_params(query)

def get_add_product_csv_files():
    query=""
    for i in PRODUCT_FILES:
        query += "\nLOAD CSV WITH HEADERS FROM 'file:///" + PARENT_FOLDER + i + """.csv' as prod
                CREATE (:Product {id: prod.商品編號, name: prod.商品名子, seller: prod.供應商編號})"""
                # CREATE INDEX FOR (p:Product) ON (p.id)"""
    
    return return_query_no_params(query)


def get_add_cancel_orders_csv_files():
    query=""
    for i in CANCELLED_ORDERS_FILES:
        query += "\nLOAD CSV WITH HEADERS FROM 'file:///" + PARENT_FOLDER + i + """.csv' as ord
        CALL {
            WITH ord
            CREATE (:CancelledOrder {order_id: ord.RG單號, cancelllation_date: ord.取消日期, status: ord.proc_status, reason: ord.取消原因})
        } IN TRANSACTIONS OF 100000 ROWS"""
        # CREATE relationships"""
    
    return return_query_no_params(query)
