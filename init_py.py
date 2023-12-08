from neo4j import GraphDatabase, basic_auth
import os
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv('URI')
USERNAME = os.getenv('USER')
PASSWORD = os.getenv('PASS')
DATABASE = os.getenv('DATABASE')

class neo4jConnection:
    def __init__(self):
        self.driver = GraphDatabase.driver(uri=URI, auth=basic_auth(USERNAME, PASSWORD))

    def close(self):
        self.driver.close()

    def check_connectivity(self):
        res = self.driver.verify_connectivity()
        print('check_connectivity', res)

    def return_actor(self, act_name):
        session = self.driver.session(database=DATABASE)
        records = session.run("MATCH (a:Person {name: $act_name})-[:ACTED_IN]->(m:Movie) RETURN a,m",act_name=act_name)

        # records, _, _ = self.driver.execute_query(
        #     "MATCH (a:Person {name: $act_name})-[:ACTED_IN]->(m:Movie) RETURN a,m",
        #     act_name=act_name,
        #     database_=DATABASE,
        #     # result_transformer_=Result.consume
        # )
        return records

connection = neo4jConnection()
connection.check_connectivity()
res= connection.return_actor("Tom Hanks")
# print("res list", res)
print("res as data", res.data())
print("res as graph", res.graph())
connection.close()
