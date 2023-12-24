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
    timeframe = data.get('timeframe')
    year = data.get('year')  # New field for Year
    quarter = data.get('quarter')  # New field for Quarter
    month = data.get('month')  # New field for Month
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
    connection = neo4jConnection()
    resdict = connection.fetch_data(QUERY_TYPES["SUPPLIER_USER_RELATIONSHIPS"], ["505", "eBRIejoRT3q3.bSthUA9"])
    print(type(resdict))

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
    product_id = data.get('product-id')
    timeframe = data.get('timeframe')
    year = data.get('year')  # New field for Year
    quarter = data.get('quarter')  # New field for Quarter
    month = data.get('month')  # New field for Month

    # Generate time series data based on the timeframe
    if timeframe == 'Daily':
        labels = [f'Day {i+1}' for i in range(31)]
    elif timeframe == 'Monthly':
        labels = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    data = [random.randint(100, 500) for _ in labels]  # Random data for illustration

    return jsonify({'labels': labels, 'data': data})


if __name__ == '__main__':
    app.run(debug=True,port=8080)