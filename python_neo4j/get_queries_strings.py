# consts:
ALL_NODE_TYPES = ("Order", "Product")
ORDER_FILES = ["order_2012Q1","order_2012Q2"]
PRODUCT_FILES = ["2012_product_list"]

QUERY_TYPES = {
    "ORDERS_OF_PRODUCT_NAME": "get_all_orders_with_product_name"
}

def return_query_no_params(quer):
    return {
        "query": quer,
        "parameters": []
    }

def get_one_order():
    return return_query_no_params("MATCH (o:Order) RETURN o LIMIT 1")
    
def get_one_product():
    return return_query_no_params("MATCH (p:Product) RETURN p LIMIT 1")
    
def get_delete_all():
    return return_query_no_params(f'MATCH (n) WHERE (n:{" OR n:".join(ALL_NODE_TYPES)}) DETACH DELETE n')

def get_add_order_csv_files():
    query=""

    for i in ORDER_FILES:
        query += "\nLOAD CSV WITH HEADERS FROM 'file:///" + i + """.csv' as ord
        MATCH (prod:Product {id: ord.商品編號})
        CREATE (ord_node:Order {id: ord.訂單編號, sub_ord:ord.子單編號, user: ord.客戶代號, del_adr: ord.到貨地址}),
            (ord_node)-[:PRODUCT]->(prod)"""
    
    return return_query_no_params(query)

def get_add_product_csv_files():
    query=""

    for i in PRODUCT_FILES:
        query += "\nLOAD CSV WITH HEADERS FROM 'file:///" + i + """.csv' as prod
                CREATE (:Product {id: prod.商品編號, name: prod.商品名子, seller: prod.供應商編號})
                CREATE INDEX FOR (p:Product) ON (p.id)"""
    
    return return_query_no_params(query)


def get_all_orders_with_product_name():
    return {
        "query": 'MATCH (o:Order)-[relatedTo]-(p:Product {name: $prod_name}) RETURN o, p',
        "parameters": [
            'prod_name'
        ]
    }
