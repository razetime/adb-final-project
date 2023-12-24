QUERY_TYPES = {
    "ORDERS_OF_PRODUCT_NAME": "get_all_orders_with_product_name",
    "ORDERS_OF_SUPPLIER": "get_supplier_all_relationships",
    "SUPPLIER_USER_RELATIONSHIPS": "get_supplier_customer_relationships",
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

def get_supplier_all_relationships():
    return {
        "query": """MATCH (u:User)-[or:ORDERED]-(po:ParentOrder)-[in:INCLUDE]-(o:Order)-[co:CONTAIN]-(p:Product)-[pr:PRODUCES]-(s:Supplier) 
                    WHERE s.id = $sup_id RETURN u,or,po,in,o,co,p,pr,s""",
        "parameters": [
            'sup_id'
        ]
    }

def get_supplier_customer_relationships():
    return {
        "query": """MATCH (u:User)-[or:ORDERED]-(po:ParentOrder)-[in:INCLUDE]-(o:Order)-[co:CONTAIN]-(p:Product)-[pr:PRODUCES]-(s:Supplier) 
                    WHERE s.id = $sup_id AND u.id = $u_id RETURN u,or,po,in,o,co,p,pr,s""",
        "parameters": [
            'sup_id',
            'u_id'
        ]
    }