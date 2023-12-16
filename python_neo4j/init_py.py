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
        session = self.driver.session(database=DATABASE)
        check_records= session.run(qtool.get_one_order()["query"])
        if not len(check_records.data()):
            print("add orders:")
            add_query = qtool.get_add_order_csv_files()["query"]
            session.run(add_query)
        
        check_records= session.run(qtool.get_one_product()["query"])
        if not len(check_records.data()):
            print("add products:")
            add_query = qtool.get_add_product_csv_files()["query"]
            session.run(add_query)

    def parse_to_obj(self, res_g) :
        res_obj={"nodes":[], "relationships":[]}
        for nod in res_g.nodes:
            res_obj["nodes"].append({**nod._properties, **{"type":nod._labels, "element_id": nod.element_id}})
        for rel in res_g.relationships:
            rel_nodes= list(map(lambda x: x.element_id,rel.nodes))
            res_obj["relationships"].append({**rel._properties, **{"type":rel.type, "nodes": rel_nodes, "element_id": nod.element_id}})
        return res_obj

    def fetch_data(self, func_name, params):
        query_data = getattr(qtool, func_name)()
        query_parameters = {}
        for i in range(len(query_data["parameters"])):
            query_parameters[query_data["parameters"][i]] = params[i]

        session = self.driver.session(database=DATABASE)
        records = session.run(query_data["query"], query_parameters)
        return self.parse_to_obj(records.graph())
    
    # TODO: visualize/go over results
    

