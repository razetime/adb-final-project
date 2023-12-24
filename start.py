from python_neo4j.init_py import neo4jConnection
from python_neo4j.get_queries_strings import QUERY_TYPES

connection = neo4jConnection()

res= connection.fetch_data(QUERY_TYPES["ORDERS_OF_PRODUCT_NAME"], ["CASIO 光動能輕薄型數位錶"])
print("res", res)
print("\n")
res= connection.fetch_data(QUERY_TYPES["ORDERS_FROM_SUPPLIER"], ["510"])
print("res", res)
print("\n")
res= connection.fetch_data(QUERY_TYPES["SUPPLIER_USER_RELATIONSHIPS"], ["505", "eBRIejoRT3q3.bSthUA9"])
print("res", res)
print("\n")
res= connection.fetch_data(QUERY_TYPES["SUPPLIER_SELLING_KEYWORD"], ["Acer"])
print("res", res)
print("\n")
connection.close()
