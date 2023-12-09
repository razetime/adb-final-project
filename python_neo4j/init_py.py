from neo4j import GraphDatabase, basic_auth, Result
import os
from dotenv import load_dotenv

from . import get_queries_strings as qtool

load_dotenv()

URI = os.getenv('URI')
USERNAME = os.getenv('USER')
PASSWORD = os.getenv('PASS')
DATABASE = os.getenv('DATABASE')

class neo4jConnection:
    def __init__(self):
        self.driver = GraphDatabase.driver(uri=URI, auth=basic_auth(USERNAME, PASSWORD))
        self.check_and_init_data()

    def close(self):
        self.driver.close()

    def check_connectivity(self):
        res = self.driver.verify_connectivity()
        print('check_connectivity', res)

    def check_and_init_data(self):
        check_records= self.driver.execute_query(
            qtool.get_one_order()["query"],
            database_=DATABASE,
            result_transformer_= Result.single
        )
        if not check_records:
            print ("empty orders!")
            # TODO: remove everything and re-write to DB

    def fetch_data(self, params):
        query_data = qtool.get_all_orders_with_product_name()
        query_parameters = {}
        for i in range(len(query_data["parameters"])):
            query_parameters[query_data["parameters"][i]] = params[i]

        session = self.driver.session(database=DATABASE)
        records = session.run(query_data["query"], query_parameters)
        # records, _, _ = self.driver.execute_query(
        #     query_=query_data["query"],
        #     parameters_=query_parameters,
        #     database_=DATABASE,
        #     # result_transformer_=Result.consume
        # )
        return records
