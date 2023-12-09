# consts:
ALL_NODE_TYPES = ("Order", "Product")

def return_query_no_params(quer):
    return {
        "query": quer,
        "parameters": []
    }

def get_one_order():
    return return_query_no_params("MATCH (o:Order) RETURN o LIMIT 1")
    
def get_delete_all_query():
    return return_query_no_params(f'MATCH (n) WHERE (n:{" OR n:".join(ALL_NODE_TYPES)}) DETACH DELETE n')

def get_all_orders_with_product_name():
    return {
        "query": 'MATCH (o:Order)-[relatedTo]-(p:Product {name: $prod_name}) RETURN o, p',
        "parameters": [
            'prod_name'
        ]
    }
