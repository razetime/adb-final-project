from neo4j import GraphDatabase, basic_auth, Result
import os
from dotenv import load_dotenv
from graphviz import Digraph
import time

from . import get_queries_strings as qtool
from . import get_set_data_queries as qsettool

load_dotenv()

URI = os.getenv('URI')
USERNAME = os.getenv('USER')
PASSWORD = os.getenv('PASS')
DATABASE = os.getenv('DATABASE')

class neo4jConnection:
    def __init__(self):
        self.driver = GraphDatabase.driver(uri=URI, auth=basic_auth(USERNAME, PASSWORD))
        # self.check_and_init_data()

    def close(self):
        self.driver.close()

    def check_connectivity(self):
        res = self.driver.verify_connectivity()
        print('check_connectivity', res)

    def check_and_init_data(self):
        start_time= time.time()
        session = self.driver.session(database=DATABASE)
        check_records= session.run(qsettool.get_one_supplier()["query"])
        if not len(check_records.data()):
            print("add suppliers:")
            add_query = qsettool.get_add_suppliers_csv_files()["query"]
            session.run(add_query)
            print('finished adding suppliers at', time.time() - start_time)

        check_records= session.run(qsettool.get_one_product()["query"])
        if not len(check_records.data()):
            print("add products:")
            add_query = qsettool.get_add_product_csv_files()["query"]
            session.run(add_query)
            index_query= qsettool.get_add_indexes_query()["query"]
            try:
                session.run(index_query)
            except:
                print("index creation failed")
            print('finished adding products at', time.time() - start_time)

        check_records= session.run(qsettool.get_one_order()["query"])
        if not len(check_records.data()):
            print("add orders:")
            add_query = qsettool.get_add_order_csv_files()["query"]
            session.run(add_query) 
            print('finished adding orders at', time.time() - start_time)

        
        check_records= session.run(qsettool.get_one_cancel_order()["query"])
        if not len(check_records.data()):
            print("add cancelled orders:")
            add_query = qsettool.get_add_cancel_orders_csv_files()["query"]
            session.run(add_query)
            print('finished adding cancelled orders at', time.time() - start_time)


    def parse_to_obj(self, res_g) :
        res_obj={"nodes":[], "relationships":[]}
        get_id = lambda x: x if not (x.rfind(":") + 1) else x[(x.rfind(":") + 1):]
        for nod in res_g.nodes:
            try:
                elm_id = (nod.element_id)
            except:
                elm_id = (nod.id)
            res_obj["nodes"].append({**nod._properties, **{"type":nod._labels, "element_id": get_id(elm_id)}})
        for rel in res_g.relationships:
            try:
                elm_id = (nod.element_id)
            except:
                elm_id = (nod.id)
            rel_nodes= list(map(lambda x: x.element_id[(x.element_id.rfind(":") + 1):],rel.nodes))
            res_obj["relationships"].append({**rel._properties, **{"type":rel.type, "nodes": rel_nodes, "element_id": get_id(elm_id)}})
        # if len(res_obj["relationships"]):
        #     res_obj["graph"] = self.get_graph_svg(res_obj)
        return res_obj

    def fetch_data(self, func_name, params):
        query_data = getattr(qtool, func_name)()
        query_parameters = {}
        for i in range(len(query_data["parameters"])):
            query_parameters[query_data["parameters"][i]] = params[i]

        session = self.driver.session(database=DATABASE)
        records = session.run(query_data["query"], query_parameters)

        return self.parse_to_obj(records.graph())
    
    def get_node_color(self, nod_type) :
        if 'Product' in nod_type:
            return 'red'
        elif 'Order' in nod_type:
            return 'blue'
        else:
            return 'black'

    def get_graph_svg(self, graph):
        f = Digraph('G', format='svg')
        f.attr(rankdir='LR', size='10')
        f.attr('node', shape='doublecircle')
        for nod in graph["nodes"]:
            f.node(name=nod["element_id"], label=nod["id"], color=self.get_node_color(nod["type"]))

        f.attr('node', shape='circle')
        for rel in graph["relationships"]:
            f.edge(rel["nodes"][0], rel["nodes"][1], label=rel["type"])

        return f

    

