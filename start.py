from python_neo4j.init_py import neo4jConnection
from python_neo4j.get_queries_strings import QUERY_TYPES

connection = neo4jConnection()

res= connection.fetch_data(QUERY_TYPES["ORDERS_OF_PRODUCT_NAME"], ["CASIO 光動能輕薄型數位錶"])
print("res", res)
connection.close()
