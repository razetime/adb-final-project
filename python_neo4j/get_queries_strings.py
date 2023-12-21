QUERY_TYPES = {
    "ORDERS_OF_PRODUCT_NAME": "get_all_orders_with_product_name"
}

def return_query_no_params(quer):
    return {
        "query": quer,
        "parameters": []
    }

def get_all_orders_with_product_name():
    return {
        "query": 'MATCH (o:Order)-[relatedTo]-(p:Product) WHERE p.name CONTAINS $prod_name RETURN o, p, relatedTo',
        "parameters": [
            'prod_name'
        ]
    }
