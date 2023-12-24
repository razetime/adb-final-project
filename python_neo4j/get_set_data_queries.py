import os
from dotenv import load_dotenv
from . import get_queries_strings as qtool

load_dotenv()
return_query_no_params = qtool.return_query_no_params

# consts:
ALL_NODE_TYPES = ("Order", "Product", "CancelledOrder", "Supplier", "ParentOrder", "User")
ORDER_FILES = ["order_2012Q1","order_2012Q2",
               "order_2011Q1","order_2011Q2","order_2011Q3","order_2011Q4"
               ]
CANCELLED_ORDERS_FILES=["4_Φ¿éσû«σÅûµ╢ê\\cancel_order"]
WEARHOUSE_FILES=["3_σ»äσÇëσàÑσ║½µ¬ö\\stlend"]
PRODUCT_FILES = [
    # "2_σòåσôüµ¬ö\\product(σÇëσç║)", 
    "2_σòåσôüµ¬ö\\2012_product_list"]
SUPPLIERS_FILES = ["1_Σ╛¢µçëσòå\\supplier"]
PARENT_FOLDER = os.getenv('PARENT_FOLDER')

def get_one_order():
    return return_query_no_params("MATCH (o:Order) RETURN o LIMIT 1")
    
def get_one_product():
    return return_query_no_params("MATCH (p:Product) RETURN p LIMIT 1")

def get_one_cancel_order():
    return return_query_no_params("MATCH (c:CancelledOrder) RETURN c LIMIT 1")

def get_one_supplier():
    return return_query_no_params("MATCH (c:Supplier) RETURN c LIMIT 1")

def get_delete_all():
    return return_query_no_params('CALL {MATCH (n) DETACH DELETE n} IN TRANSACTIONS OF 100000 ROWS')

def get_add_order_csv_files():
    query=""
    for i in ORDER_FILES:
        query += "\nLOAD CSV WITH HEADERS FROM 'file:///"+ PARENT_FOLDER + i + """.csv' as ord
        CALL {
            WITH ord
            OPTIONAL MATCH (prod:Product {id: ord.商品編號})    
            CREATE (ord_node:Order {id: ord.子單編號, ship_method: ord.出貨方式})
            FOREACH(_ IN CASE WHEN prod IS NOT NULL THEN [1] END | CREATE (ord_node)-[:CONTAIN]->(prod))
            MERGE (parent_ord:ParentOrder {id:ord.RG, parent_ord_num:ord.訂單編號, datetime: ord.訂單成立時間})
            MERGE (parent_ord)-[:INCLUDE]->(ord_node)
            MERGE (u:User {id: ord.客戶代號})
            MERGE (u)-[:ORDERED]->(parent_ord)
        } IN TRANSACTIONS OF 2000 ROWS"""
    return return_query_no_params(query)

def get_add_product_csv_files():
    query=""
    index=0
    for i in PRODUCT_FILES:
        query += "\nLOAD CSV WITH HEADERS FROM 'file:///" + PARENT_FOLDER + i + """.csv' as prod_new
                MATCH (sup:Supplier {id: prod_new.供應商編號})
                CREATE (prod_node:Product {id: prod_new.商品編號, name: prod_new.商品名子}), (prod_node)-[:PRODUCES]->(sup)"""
        index+=1

    return return_query_no_params(query)

def get_add_indexes_query():
    return return_query_no_params("""CREATE INDEX FOR (p:Product) ON (p.id);
                                  CREATE INDEX FOR (po:ParentOrder) ON (po.id);
                                  CREATE INDEX FOR (u:User) ON (u.id);
                                  CREATE INDEX FOR (s:Supplier) ON (s.id);""")

def get_add_cancel_orders_csv_files():
    query=""
    for i in CANCELLED_ORDERS_FILES:
        query += "\nLOAD CSV WITH HEADERS FROM 'file:///" + PARENT_FOLDER + i + """.csv' as c_ord
        CALL {
            WITH c_ord
            MATCH (po:ParentOrder {id: c_ord.RG單號})
            CREATE (co:CancelledOrder {order_id: c_ord.RG單號, cancelllation_date: c_ord.取消日期, status: c_ord.proc_status, reason: c_ord.取消原因}), (co)-[:CANCELLING]->(po)
        } IN TRANSACTIONS OF 5000 ROWS"""
    
    return return_query_no_params(query)

def get_add_suppliers_csv_files():
    query=""
    for i in SUPPLIERS_FILES:
        query += "\nLOAD CSV WITH HEADERS FROM 'file:///" + PARENT_FOLDER + i + """.csv' as sup
        CALL {
            WITH sup
            CREATE (:Supplier {id: sup.供應商代號, name: sup.供應商名稱})
        } IN TRANSACTIONS OF 5000 ROWS"""
    
    return return_query_no_params(query)
