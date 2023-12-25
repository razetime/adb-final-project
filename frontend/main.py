from flask import Flask, render_template, request, jsonify
from psql_query import *
import random
from python_neo4j.init_py import neo4jConnection
from python_neo4j.get_queries_strings import QUERY_TYPES
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/repeated_purchases')
def repeated_purchases():
    timeframes = ["Monthly", "Quarterly"]
    years = []
    quarters = []
    months = []
    return render_template('repeated_purchases.html', timeframes=timeframes, years=years, quarters=quarters, months=months)

@app.route('/supplier_customer_relationships')
def supplier_customer_relationships():
    return render_template('supplier_customer_relationships.html')

@app.route('/time_series_analysis')
def time_series_analysis():
    timeframes = ["Daily", "Monthly"]
    years = []
    quarters = []
    months = []
    return render_template('time_series_analysis.html', timeframes=timeframes, years=years, quarters=quarters, months=months)

@app.route('/get_products', methods=['POST'])
def get_products():
    supplier_id = request.json.get('supplier_id')
    products = []
    if supplier_id == "Asus":
        products = ["VivoBook Pro 15", "ROG Zephyrus S17"]
    elif supplier_id == "Acer":
        products = ["Swift Go 14", "Predator Helios 16"]
    elif supplier_id == "All":
        products = ["VivoBook Pro 15", "ROG Zephyrus S17", "Swift Go 14", "Predator Helios 16"]
    return jsonify(products=products)

@app.route('/update_map_repeated_purchases', methods=['POST'])
def update_map_repeated_purchases():
    data = request.json
    print("Received data:", data)  # This line prints the received data to the console
    city = data.get('city')
    # supplier_id = data.get('supplier_id')  # New field for Supplier ID
    product_id = data.get('product_id') # 1199969
    timeframe = data.get('timeframe')
    year = data.get('year')  # New field for Year
    quarter = data.get('quarter')  # New field for Quarter
    month = data.get('month')  # New field for Month
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"];

    # Fetch GeoJSON
    url = 'https://api.maptiler.com/data/09e09097-be00-42f9-ae5e-af6db6815443/features.json?key=uIMFZoCyLmKWTvmPj2JG'
    # response = requests.get(url)
    # geojson_data = response.json()
    print(int(year),quarter[1],[months.index(month)+1,product_id])
    geojson_data = None
    match timeframe:
        case 'Monthly':
            mno = months.index(month)+1
            if not query_product_exists_mnt(int(year),quarter[1],[mno,product_id]):
                return jsonify({'status': 'id_failure'})
            geojson_data = query_monthly(int(year),quarter[1],[mno,product_id])
        case 'Quarterly':
            if not query_product_exists_qtr(int(year),quarter[1],[product_id]):
                return jsonify({'status': 'id_failure'})
            geojson_data = query_quarterly(int(year),quarter[1],[product_id])
        

    # Process GeoJSON
    processed_data = []
    # for feature in geojson_data['features']:
    for feature in geojson_data:
        feature=feature[0]
        city = feature['properties']['city']
        # district = feature['properties']['district']
        repeated_purchases = feature['properties']['count']
        coordinates = feature['geometry']['coordinates']

        processed_data.append({
            # 'district': district,
            'city': city,
            'repeated_purchases': repeated_purchases,
            'coordinates': coordinates
        })

    # Calculate min and max repeated purchases
    # min_purchases = min(int(feature['properties']['Repeated Purchases']) for feature in geojson_data['features'])
    # max_purchases = max(int(feature['properties']['Repeated Purchases']) for feature in geojson_data['features'])
    max_purchases = max(int(feature[0]['properties']['count']) for feature in geojson_data)
    min_purchases = min(int(feature[0]['properties']['count']) for feature in geojson_data)

    # Prepare and return the response data
    response_data = {
        'status': 'success',
        'received': data,  # Includes the data received from the AJAX request
        'processed': processed_data,  # The processed GeoJSON data
        'min_purchases': min_purchases,  # Minimum repeated purchases value
        'max_purchases': max_purchases   # Maximum repeated purchases value
    }
    print(response_data)
    return jsonify(response_data)


@app.route('/get_network_data', methods=['POST'])
def get_network_data():
    data = request.json
    customer = data.get('customer')
    supplier_id = data.get('supplier_id')
    # timeframe = data.get('timeframe')
    # year = data.get('year')  # New field for Year
    # quarter = data.get('quarter')  # New field for Quarter
    # month = data.get('month')  # New field for Month
    # Sample data resembling the output of a Neo4J query
    # resdict = {
    #     "nodes": 
    #     [
    #         {"id": "eBRIejoRT3q3.bSthUA9", "type": ["User"] ,"element_id": "8217280"}, 
    #         {"datetime": "2012-06-15 22:34:00.000", "id": "39218011", "parent_ord_num": "RM1206150031411", "type": ["ParentOrder"], "element_id": "8217279"}, 
    #         {"ship_method": "倉出", "id": "RS1206150047841", "type": ["Order"], "element_id": "8217278"}, 
    #         {"name": "Delonghi 迪朗奇多功能磨豆機 KG40", "id": "7320052", "type": ["Product"], "element_id": "9761"}, 
    #         {"name": "新各界企業有限公司", "id": "505", "type": ["Supplier"], "element_id": "13"}, 
    #         {"datetime": "2012-06-15 22:34:00.000", "id": "39218011", "parent_ord_num": "RM1206150031412", "type": ["ParentOrder"], "element_id": "8217282"}, 
    #         {"ship_method": "倉出", "id": "RS1206150047842", "type": ["Order"], "element_id": "8217281"}, 
    #         {"name": "迪朗奇義式濃縮半自動咖啡機 EC155", "id": "7320016", "type": ["Product"], "element_id": "9760"}
    #     ], 
    #     "relationships": 
    #     [
    #         {"type": "ORDERED", "nodes": ["8217280", "8217279"], "element_id": "9760"}, 
    #         {"type": "INCLUDE", "nodes": ["8217279", "8217278"], "element_id": "9760"}, 
    #         {"type": "CONTAIN", "nodes": ["8217278", "9761"], "element_id": "9760"}, 
    #         {"type": "PRODUCES", "nodes": ["9761", "13"], "element_id": "9760"}, 
    #         {"type": "ORDERED", "nodes": ["8217280", "8217282"], "element_id": "9760"}, 
    #         {"type": "INCLUDE", "nodes": ["8217282", "8217281"], "element_id": "9760"}, 
    #         {"type": "CONTAIN", "nodes": ["8217281", "9760"], "element_id": "9760"}, 
    #         {"type": "PRODUCES", "nodes": ["9760", "13"], "element_id": "9760"}
    #     ]
    # }
    # {
#   "links": [
#     {
#       "source": {
#         "customer_id": "WShFnNhQdHtqxBxv6exd8w--",
#         "group": "User",
#         "id": "9851751",
#         "index": 0,
#         "x": 559.4390647813877,
#         "y": -404.9308887094558,
#         "vy": 0.10906178734531154,
#         "vx": 0.00021986499212127772
#       },
#       "target": {
#         "datetime": "2012-01-11 18:20:00.000",
#         "group": "ParentOrder",
#         "id": "9851754",
#         "parent_ord_id": "31987006",
#         "parent_ord_num": "RM1201110029139",
#         "index": 1,
#         "x": 394.910062873015,
#         "y": -49.92498845289136,
#         "vy": 0.057344418186255845,
#         "vx": -0.009011718870572874
#       },
#       "type": "ORDERED",
#       "index": 0
#     },
#     {
#       "source": {
#         "datetime": "2012-01-11 18:20:00.000",
#         "group": "ParentOrder",
#         "id": "9851754",
#         "parent_ord_id": "31987006",
#         "parent_ord_num": "RM1201110029139",
#         "index": 1,
#         "x": 394.910062873015,
#         "y": -49.92498845289136,
#         "vy": 0.057344418186255845,
#         "vx": -0.009011718870572874
#       },
#       "target": {
#         "group": "Order",
#         "id": "9851752",
#         "order_id": "RS1201110046192",
#         "ship_method": "倉出",
#         "index": 2,
#         "x": 293.0588623529172,
#         "y": 353.01064111522356,
#         "vy": 0.011267047979246363,
#         "vx": -0.013685224835442343
#       },
#       "type": "INCLUDE",
#       "index": 1
#     },
#     {
#       "source": {
#         "group": "Order",
#         "id": "9851752",
#         "order_id": "RS1201110046192",
#         "ship_method": "倉出",
#         "index": 2,
#         "x": 293.0588623529172,
#         "y": 353.01064111522356,
#         "vy": 0.011267047979246363,
#         "vx": -0.013685224835442343
#       },
#       "target": {
#         "group": "Product",
#         "id": "5819",
#         "name": "歌林充電式隨身電暖蛋2入超值組—粉紅*2 (MIT台灣製造)",
#         "prod_id": "7220057",
#         "index": 3,
#         "x": 403.19719545987095,
#         "y": 771.9562948010908,
#         "vy": -0.03192167862509489,
#         "vx": -0.00845139114652976
#       },
#       "type": "CONTAIN",
#       "index": 2
#     },
#     {
#       "source": {
#         "group": "Product",
#         "id": "5819",
#         "name": "歌林充電式隨身電暖蛋2入超值組—粉紅*2 (MIT台灣製造)",
#         "prod_id": "7220057",
#         "index": 3,
#         "x": 403.19719545987095,
#         "y": 771.9562948010908,
#         "vy": -0.03192167862509489,
#         "vx": -0.00845139114652976
#       },
#       "target": {
#         "group": "Supplier",
#         "id": "431",
#         "name": "宥喬國際有限公司",
#         "ship_method": "",
#         "supplier_id": "1303",
#         "index": 4,
#         "x": 566.5192589348508,
#         "y": 956.7108316454536,
#         "vy": -0.09985652706099651,
#         "vx": 0.00016151578774865224
#       },
#       "type": "PRODUCES",
#       "index": 3
#     },
#     {
#       "source": {
#         "datetime": "2012-01-11 18:20:00.000",
#         "group": "ParentOrder",
#         "id": "9851754",
#         "parent_ord_id": "31987006",
#         "parent_ord_num": "RM1201110029139",
#         "index": 1,
#         "x": 394.910062873015,
#         "y": -49.92498845289136,
#         "vy": 0.057344418186255845,
#         "vx": -0.009011718870572874
#       },
#       "target": {
#         "group": "Order",
#         "id": "9851753",
#         "order_id": "RS1201110046192",
#         "ship_method": "倉出",
#         "index": 5,
#         "x": 488.87797252817705,
#         "y": 292.4552150557804,
#         "vy": 0.0054867999348927445,
#         "vx": -0.0030403746763948787
#       },
#       "type": "INCLUDE",
#       "index": 4
#     },
#     {
#       "source": {
#         "group": "Order",
#         "id": "9851753",
#         "order_id": "RS1201110046192",
#         "ship_method": "倉出",
#         "index": 5,
#         "x": 488.87797252817705,
#         "y": 292.4552150557804,
#         "vy": 0.0054867999348927445,
#         "vx": -0.0030403746763948787
#       },
#       "target": {
#         "group": "Product",
#         "id": "1650006",
#         "name": "歌林充電式隨身電暖蛋2入超值組—粉紅*2 (MIT台灣製造)",
#         "prod_id": "7220057",
#         "index": 6,
#         "x": 606.4113315880949,
#         "y": 802.634779979419,
#         "vy": -0.02964283324079469,
#         "vx": 0.0026995532919583056
#       },
#       "type": "CONTAIN",
#       "index": 5
#     },
#     {
#       "source": {
#         "group": "Product",
#         "id": "1650006",
#         "name": "歌林充電式隨身電暖蛋2入超值組—粉紅*2 (MIT台灣製造)",
#         "prod_id": "7220057",
#         "index": 6,
#         "x": 606.4113315880949,
#         "y": 802.634779979419,
#         "vy": -0.02964283324079469,
#         "vx": 0.0026995532919583056
#       },
#       "target": {
#         "group": "Supplier",
#         "id": "431",
#         "name": "宥喬國際有限公司",
#         "ship_method": "",
#         "supplier_id": "1303",
#         "index": 4,
#         "x": 566.5192589348508,
#         "y": 956.7108316454536,
#         "vy": -0.09985652706099651,
#         "vx": 0.00016151578774865224
#       },
#       "type": "PRODUCES",
#       "index": 6
#     },
#     {
#       "source": {
#         "customer_id": "WShFnNhQdHtqxBxv6exd8w--",
#         "group": "User",
#         "id": "9851751",
#         "index": 0,
#         "x": 559.4390647813877,
#         "y": -404.9308887094558,
#         "vy": 0.10906178734531154,
#         "vx": 0.00021986499212127772
#       },
#       "target": {
#         "datetime": "2012-01-11 18:20:00.000",
#         "group": "ParentOrder",
#         "id": "9851757",
#         "parent_ord_id": "31987006",
#         "parent_ord_num": "RM1201110029140",
#         "index": 7,
#         "x": 563.5939915001769,
#         "y": 66.54973229764616,
#         "vy": 0.06863229370482452,
#         "vx": -0.000028139054299111014
#       },
#       "type": "ORDERED",
#       "index": 7
#     },
#     {
#       "source": {
#         "datetime": "2012-01-11 18:20:00.000",
#         "group": "ParentOrder",
#         "id": "9851757",
#         "parent_ord_id": "31987006",
#         "parent_ord_num": "RM1201110029140",
#         "index": 7,
#         "x": 563.5939915001769,
#         "y": 66.54973229764616,
#         "vy": 0.06863229370482452,
#         "vx": -0.000028139054299111014
#       },
#       "target": {
#         "group": "Order",
#         "id": "9851755",
#         "order_id": "RS1201110046193",
#         "ship_method": "倉出",
#         "index": 8,
#         "x": 639.2648507764624,
#         "y": 431.82061525236554,
#         "vy": 0.018931245065561556,
#         "vx": 0.0038560428032358737
#       },
#       "type": "INCLUDE",
#       "index": 8
#     },
#     {
#       "source": {
#         "group": "Order",
#         "id": "9851755",
#         "order_id": "RS1201110046193",
#         "ship_method": "倉出",
#         "index": 8,
#         "x": 639.2648507764624,
#         "y": 431.82061525236554,
#         "vy": 0.018931245065561556,
#         "vx": 0.0038560428032358737
#       },
#       "target": {
#         "group": "Product",
#         "id": "5820",
#         "name": "歌林充電式隨身電暖蛋2入超值組—白色*2 (MIT台灣製造)",
#         "prod_id": "7220058",
#         "index": 9,
#         "x": 513.1323944179577,
#         "y": 731.9905344645607,
#         "vy": -0.035847451803064326,
#         "vx": -0.002294961188632085
#       },
#       "type": "CONTAIN",
#       "index": 9
#     },
#     {
#       "source": {
#         "group": "Product",
#         "id": "5820",
#         "name": "歌林充電式隨身電暖蛋2入超值組—白色*2 (MIT台灣製造)",
#         "prod_id": "7220058",
#         "index": 9,
#         "x": 513.1323944179577,
#         "y": 731.9905344645607,
#         "vy": -0.035847451803064326,
#         "vx": -0.002294961188632085
#       },
#       "target": {
#         "group": "Supplier",
#         "id": "431",
#         "name": "宥喬國際有限公司",
#         "ship_method": "",
#         "supplier_id": "1303",
#         "index": 4,
#         "x": 566.5192589348508,
#         "y": 956.7108316454536,
#         "vy": -0.09985652706099651,
#         "vx": 0.00016151578774865224
#       },
#       "type": "PRODUCES",
#       "index": 10
#     },
#     {
#       "source": {
#         "datetime": "2012-01-11 18:20:00.000",
#         "group": "ParentOrder",
#         "id": "9851757",
#         "parent_ord_id": "31987006",
#         "parent_ord_num": "RM1201110029140",
#         "index": 7,
#         "x": 563.5939915001769,
#         "y": 66.54973229764616,
#         "vy": 0.06863229370482452,
#         "vx": -0.000028139054299111014
#       },
#       "target": {
#         "group": "Order",
#         "id": "9851756",
#         "order_id": "RS1201110046193",
#         "ship_method": "倉出",
#         "index": 10,
#         "x": 443.43147328805196,
#         "y": 492.34852406638146,
#         "vy": 0.0253488469743556,
#         "vx": -0.006456841706454243
#       },
#       "type": "INCLUDE",
#       "index": 11
#     },
#     {
#       "source": {
#         "group": "Order",
#         "id": "9851756",
#         "order_id": "RS1201110046193",
#         "ship_method": "倉出",
#         "index": 10,
#         "x": 443.43147328805196,
#         "y": 492.34852406638146,
#         "vy": 0.0253488469743556,
#         "vx": -0.006456841706454243
#       },
#       "target": {
#         "group": "Product",
#         "id": "1650007",
#         "name": "歌林充電式隨身電暖蛋2入超值組—白色*2 (MIT台灣製造)",
#         "prod_id": "7220058",
#         "index": 11,
#         "x": 492.8021013008005,
#         "y": 847.197693758307,
#         "vy": -0.024200449791498446,
#         "vx": -0.004306533171073858
#       },
#       "type": "CONTAIN",
#       "index": 12
#     },
#     {
#       "source": {
#         "group": "Product",
#         "id": "1650007",
#         "name": "歌林充電式隨身電暖蛋2入超值組—白色*2 (MIT台灣製造)",
#         "prod_id": "7220058",
#         "index": 11,
#         "x": 492.8021013008005,
#         "y": 847.197693758307,
#         "vy": -0.024200449791498446,
#         "vx": -0.004306533171073858
#       },
#       "target": {
#         "group": "Supplier",
#         "id": "431",
#         "name": "宥喬國際有限公司",
#         "ship_method": "",
#         "supplier_id": "1303",
#         "index": 4,
#         "x": 566.5192589348508,
#         "y": 956.7108316454536,
#         "vy": -0.09985652706099651,
#         "vx": 0.00016151578774865224
#       },
#       "type": "PRODUCES",
#       "index": 13
#     },
#     {
#       "source": {
#         "customer_id": "WShFnNhQdHtqxBxv6exd8w--",
#         "group": "User",
#         "id": "9851751",
#         "index": 0,
#         "x": 559.4390647813877,
#         "y": -404.9308887094558,
#         "vy": 0.10906178734531154,
#         "vx": 0.00021986499212127772
#       },
#       "target": {
#         "datetime": "2012-01-11 18:20:00.000",
#         "group": "ParentOrder",
#         "id": "9851750",
#         "parent_ord_id": "31987006",
#         "parent_ord_num": "RM1201110029138",
#         "index": 12,
#         "x": 725.9779271186043,
#         "y": -58.560395523102365,
#         "vy": 0.05683617702998692,
#         "vx": 0.008922564955259192
#       },
#       "type": "ORDERED",
#       "index": 14
#     },
#     {
#       "source": {
#         "datetime": "2012-01-11 18:20:00.000",
#         "group": "ParentOrder",
#         "id": "9851750",
#         "parent_ord_id": "31987006",
#         "parent_ord_num": "RM1201110029138",
#         "index": 12,
#         "x": 725.9779271186043,
#         "y": -58.560395523102365,
#         "vy": 0.05683617702998692,
#         "vx": 0.008922564955259192
#       },
#       "target": {
#         "group": "Order",
#         "id": "9851749",
#         "order_id": "RS1201110046191",
#         "ship_method": "倉出",
#         "index": 13,
#         "x": 835.0999539435826,
#         "y": 371.2032724703969,
#         "vy": 0.014588129065363612,
#         "vx": 0.014129185594374417
#       },
#       "type": "INCLUDE",
#       "index": 15
#     },
#     {
#       "source": {
#         "group": "Order",
#         "id": "9851749",
#         "order_id": "RS1201110046191",
#         "ship_method": "倉出",
#         "index": 13,
#         "x": 835.0999539435826,
#         "y": 371.2032724703969,
#         "vy": 0.014588129065363612,
#         "vx": 0.014129185594374417
#       },
#       "target": {
#         "group": "Product",
#         "id": "1650005",
#         "name": "歌林充電式隨身電暖蛋2入超值組—粉紅+白色( MIT台灣製造)",
#         "prod_id": "7220056",
#         "index": 14,
#         "x": 620.8937416351644,
#         "y": 686.4980894629668,
#         "vy": -0.04035280112318805,
#         "vx": 0.003860198845619328
#       },
#       "type": "CONTAIN",
#       "index": 16
#     },
#     {
#       "source": {
#         "group": "Product",
#         "id": "1650005",
#         "name": "歌林充電式隨身電暖蛋2入超值組—粉紅+白色( MIT台灣製造)",
#         "prod_id": "7220056",
#         "index": 14,
#         "x": 620.8937416351644,
#         "y": 686.4980894629668,
#         "vy": -0.04035280112318805,
#         "vx": 0.003860198845619328
#       },
#       "target": {
#         "group": "Supplier",
#         "id": "431",
#         "name": "宥喬國際有限公司",
#         "ship_method": "",
#         "supplier_id": "1303",
#         "index": 4,
#         "x": 566.5192589348508,
#         "y": 956.7108316454536,
#         "vy": -0.09985652706099651,
#         "vx": 0.00016151578774865224
#       },
#       "type": "PRODUCES",
#       "index": 17
#     },
#     {
#       "source": {
#         "datetime": "2012-01-11 18:20:00.000",
#         "group": "ParentOrder",
#         "id": "9851750",
#         "parent_ord_id": "31987006",
#         "parent_ord_num": "RM1201110029138",
#         "index": 12,
#         "x": 725.9779271186043,
#         "y": -58.560395523102365,
#         "vy": 0.05683617702998692,
#         "vx": 0.008922564955259192
#       },
#       "target": {
#         "group": "Order",
#         "id": "9851748",
#         "order_id": "RS1201110046191",
#         "ship_method": "倉出",
#         "index": 15,
#         "x": 684.7031722306305,
#         "y": 231.91347192308095,
#         "vy": -0.0006100003752497431,
#         "vx": 0.007462824991852848
#       },
#       "type": "INCLUDE",
#       "index": 18
#     },
#     {
#       "source": {
#         "group": "Order",
#         "id": "9851748",
#         "order_id": "RS1201110046191",
#         "ship_method": "倉出",
#         "index": 15,
#         "x": 684.7031722306305,
#         "y": 231.91347192308095,
#         "vy": -0.0006100003752497431,
#         "vx": 0.007462824991852848
#       },
#       "target": {
#         "group": "Product",
#         "id": "5818",
#         "name": "歌林充電式隨身電暖蛋2入超值組—粉紅+白色( MIT台灣製造)",
#         "prod_id": "7220056",
#         "index": 16,
#         "x": 714.1891537049153,
#         "y": 757.0934268514097,
#         "vy": -0.03301454463264565,
#         "vx": 0.008471868047359337
#       },
#       "type": "CONTAIN",
#       "index": 19
#     },
#     {
#       "source": {
#         "group": "Product",
#         "id": "5818",
#         "name": "歌林充電式隨身電暖蛋2入超值組—粉紅+白色( MIT台灣製造)",
#         "prod_id": "7220056",
#         "index": 16,
#         "x": 714.1891537049153,
#         "y": 757.0934268514097,
#         "vy": -0.03301454463264565,
#         "vx": 0.008471868047359337
#       },
#       "target": {
#         "group": "Supplier",
#         "id": "431",
#         "name": "宥喬國際有限公司",
#         "ship_method": "",
#         "supplier_id": "1303",
#         "index": 4,
#         "x": 566.5192589348508,
#         "y": 956.7108316454536,
#         "vy": -0.09985652706099651,
#         "vx": 0.00016151578774865224
#       },
#       "type": "PRODUCES",
#       "index": 20
#     }
#   ],
#   "nodes": [
#     {
#       "customer_id": "WShFnNhQdHtqxBxv6exd8w--",
#       "group": "User",
#       "id": "9851751",
#       "index": 0,
#       "x": 559.4390647813877,
#       "y": -404.9308887094558,
#       "vy": 0.10906178734531154,
#       "vx": 0.00021986499212127772
#     },
#     {
#       "datetime": "2012-01-11 18:20:00.000",
#       "group": "ParentOrder",
#       "id": "9851754",
#       "parent_ord_id": "31987006",
#       "parent_ord_num": "RM1201110029139",
#       "index": 1,
#       "x": 394.910062873015,
#       "y": -49.92498845289136,
#       "vy": 0.057344418186255845,
#       "vx": -0.009011718870572874
#     },
#     {
#       "group": "Order",
#       "id": "9851752",
#       "order_id": "RS1201110046192",
#       "ship_method": "倉出",
#       "index": 2,
#       "x": 293.0588623529172,
#       "y": 353.01064111522356,
#       "vy": 0.011267047979246363,
#       "vx": -0.013685224835442343
#     },
#     {
#       "group": "Product",
#       "id": "5819",
#       "name": "歌林充電式隨身電暖蛋2入超值組—粉紅*2 (MIT台灣製造)",
#       "prod_id": "7220057",
#       "index": 3,
#       "x": 403.19719545987095,
#       "y": 771.9562948010908,
#       "vy": -0.03192167862509489,
#       "vx": -0.00845139114652976
#     },
#     {
#       "group": "Supplier",
#       "id": "431",
#       "name": "宥喬國際有限公司",
#       "ship_method": "",
#       "supplier_id": "1303",
#       "index": 4,
#       "x": 566.5192589348508,
#       "y": 956.7108316454536,
#       "vy": -0.09985652706099651,
#       "vx": 0.00016151578774865224
#     },
#     {
#       "group": "Order",
#       "id": "9851753",
#       "order_id": "RS1201110046192",
#       "ship_method": "倉出",
#       "index": 5,
#       "x": 488.87797252817705,
#       "y": 292.4552150557804,
#       "vy": 0.0054867999348927445,
#       "vx": -0.0030403746763948787
#     },
#     {
#       "group": "Product",
#       "id": "1650006",
#       "name": "歌林充電式隨身電暖蛋2入超值組—粉紅*2 (MIT台灣製造)",
#       "prod_id": "7220057",
#       "index": 6,
#       "x": 606.4113315880949,
#       "y": 802.634779979419,
#       "vy": -0.02964283324079469,
#       "vx": 0.0026995532919583056
#     },
#     {
#       "datetime": "2012-01-11 18:20:00.000",
#       "group": "ParentOrder",
#       "id": "9851757",
#       "parent_ord_id": "31987006",
#       "parent_ord_num": "RM1201110029140",
#       "index": 7,
#       "x": 563.5939915001769,
#       "y": 66.54973229764616,
#       "vy": 0.06863229370482452,
#       "vx": -0.000028139054299111014
#     },
#     {
#       "group": "Order",
#       "id": "9851755",
#       "order_id": "RS1201110046193",
#       "ship_method": "倉出",
#       "index": 8,
#       "x": 639.2648507764624,
#       "y": 431.82061525236554,
#       "vy": 0.018931245065561556,
#       "vx": 0.0038560428032358737
#     },
#     {
#       "group": "Product",
#       "id": "5820",
#       "name": "歌林充電式隨身電暖蛋2入超值組—白色*2 (MIT台灣製造)",
#       "prod_id": "7220058",
#       "index": 9,
#       "x": 513.1323944179577,
#       "y": 731.9905344645607,
#       "vy": -0.035847451803064326,
#       "vx": -0.002294961188632085
#     },
#     {
#       "group": "Order",
#       "id": "9851756",
#       "order_id": "RS1201110046193",
#       "ship_method": "倉出",
#       "index": 10,
#       "x": 443.43147328805196,
#       "y": 492.34852406638146,
#       "vy": 0.0253488469743556,
#       "vx": -0.006456841706454243
#     },
#     {
#       "group": "Product",
#       "id": "1650007",
#       "name": "歌林充電式隨身電暖蛋2入超值組—白色*2 (MIT台灣製造)",
#       "prod_id": "7220058",
#       "index": 11,
#       "x": 492.8021013008005,
#       "y": 847.197693758307,
#       "vy": -0.024200449791498446,
#       "vx": -0.004306533171073858
#     },
#     {
#       "datetime": "2012-01-11 18:20:00.000",
#       "group": "ParentOrder",
#       "id": "9851750",
#       "parent_ord_id": "31987006",
#       "parent_ord_num": "RM1201110029138",
#       "index": 12,
#       "x": 725.9779271186043,
#       "y": -58.560395523102365,
#       "vy": 0.05683617702998692,
#       "vx": 0.008922564955259192
#     },
#     {
#       "group": "Order",
#       "id": "9851749",
#       "order_id": "RS1201110046191",
#       "ship_method": "倉出",
#       "index": 13,
#       "x": 835.0999539435826,
#       "y": 371.2032724703969,
#       "vy": 0.014588129065363612,
#       "vx": 0.014129185594374417
#     },
#     {
#       "group": "Product",
#       "id": "1650005",
#       "name": "歌林充電式隨身電暖蛋2入超值組—粉紅+白色( MIT台灣製造)",
#       "prod_id": "7220056",
#       "index": 14,
#       "x": 620.8937416351644,
#       "y": 686.4980894629668,
#       "vy": -0.04035280112318805,
#       "vx": 0.003860198845619328
#     },
#     {
#       "group": "Order",
#       "id": "9851748",
#       "order_id": "RS1201110046191",
#       "ship_method": "倉出",
#       "index": 15,
#       "x": 684.7031722306305,
#       "y": 231.91347192308095,
#       "vy": -0.0006100003752497431,
#       "vx": 0.007462824991852848
#     },
#     {
#       "group": "Product",
#       "id": "5818",
#       "name": "歌林充電式隨身電暖蛋2入超值組—粉紅+白色( MIT台灣製造)",
#       "prod_id": "7220056",
#       "index": 16,
#       "x": 714.1891537049153,
#       "y": 757.0934268514097,
#       "vy": -0.03301454463264565,
#       "vx": 0.008471868047359337
#     }
#   ]
# }
    connection = neo4jConnection()
    # "505", "eBRIejoRT3q3.bSthUA9"
    resdict = connection.fetch_data(QUERY_TYPES["SUPPLIER_USER_RELATIONSHIPS"], [supplier_id, customer])
    #print(type(resdict))

    # # Generate nodes and links based on the supplier
    # # For now, this is just a simple example
    # if supplier_id=="All":
    #     # Sample data for two suppliers and their products
    #     suppliers = ["Asus", "Acer"]
    #     asus_products = ["VivoBook", "ZenBook", "ROG Laptop"]
    #     acer_products = ["Aspire", "Swift", "Predator"]

    #     # Initialize nodes with suppliers
    #     nodes = [{"id": supplier} for supplier in suppliers]

    #     # Initialize links
    #     links = []

    #     # Add products and links for Asus
    #     for product in asus_products:
    #         nodes.append({"id": product})
    #         links.append({"source": "Asus", "target": product, "value": random.randint(10, 100)})

    #     # Add products and links for Acer
    #     for product in acer_products:
    #         nodes.append({"id": product})
    #         links.append({"source": "Acer", "target": product, "value": random.randint(10, 100)})
    # else:
    #     nodes = [{"id": supplier_id}]
    #     links = []

    #     # Example: Generate random nodes and links
    #     for i in range(1, 5):  # Change 5 to the desired number of nodes
    #         product_name = f"Product{i}"
    #         nodes.append({"id": product_name})
    #         links.append({"source": supplier_id, "target": product_name, "value": random.randint(10, 100)})

    # Assuming resdict is already defined or received from another source
    nodes, links = process_data_for_graph(resdict)
    print("nodes: ", nodes, "links: ", links)
    return jsonify({"nodes": nodes, "links": links})

#Function that will process the data coming from Neo4J
def process_data_for_graph(resdict):
    # Extract and format nodes using element_id as the unique identifier
    nodes = []
    for node in resdict["nodes"]:
        node_info = {
            "id": node["element_id"],  # Use element_id as the unique identifier
            "group": list(node["type"])[0],
        }
        # Additional properties based on type
        if node_info["group"] == "User":
            node_info["customer_id"] = node.get("id", "")
        elif node_info["group"] == "ParentOrder":
            node_info["parent_ord_id"] = node.get("id", "")
            node_info["datetime"] = node.get("datetime", "")
            node_info["parent_ord_num"] = node.get("parent_ord_num", "")
        elif node_info["group"] == "Order":
            node_info["order_id"] = node.get("id", "")
            node_info["ship_method"] = node.get("ship_method", "")
        elif node_info["group"] == "Product":
            node_info["prod_id"] = node.get("id", "")
            node_info["name"] = node.get("name", "")
        elif node_info["group"] == "Supplier":
            node_info["supplier_id"] = node.get("id", "")
            node_info["ship_method"] = node.get("ship_method", "")
            node_info["name"] = node.get("name", "")
        
        nodes.append(node_info)

    # Extract and format relationships using element_id
    links = []
    for relation in resdict["relationships"]:
        source_id = next((node["id"] for node in nodes if node["id"] == relation["nodes"][0]), None)
        target_id = next((node["id"] for node in nodes if node["id"] == relation["nodes"][1]), None)
        if source_id and target_id:
            link = {
                "source": source_id,
                "target": target_id,
                "type": relation["type"]
            }
            links.append(link)

    return nodes, links






@app.route('/get_time_series_data', methods=['POST'])
def get_time_series_data():
    data = request.json
    print("Received data:", data)
    supplier_id = data.get('supplier_id')
    product_id = data.get('product_id')
    timeframe = data.get('timeframe')
    year = data.get('year')  # New field for Year
    quarter = data.get('quarter')  # New field for Quarter
    month = data.get('month')  # New field for Month

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    # Generate time series data based on the timeframe
    if timeframe == 'Daily':
        labels = [f'Day {i+1}' for i in range(31)]
    elif timeframe == 'Monthly':
        labels = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    query_data = query_product_timeseries_daily(year,quarter,[product_id,1+months.index(month)])
    # data = [random.randint(100, 500) for _ in labels]  # Random data for illustration

    return jsonify({
        'labels': [x[0] for x in query_data],
        'data': [x[1] for x in query_data]
        })


if __name__ == '__main__':
    app.run(debug=True,port=8080)