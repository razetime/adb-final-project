from python_neo4j.init_py import neo4jConnection


connection = neo4jConnection()

res= connection.fetch_data(["[快]SONY PJ50(平輸繁中)-黑色"])
print("res list", res)
print("res as data", res.data())
print("res as graph", res.graph())
connection.close()
