from flask import Flask, render_template, request, jsonify
from psql_query import *
import random
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/repeated_purchases')
def repeated_purchases():
    cities = ['新北', '新社', '高門', '鄰環', '昌路', '苗栗', '長門', '大里', '高雄', '南投', '際富', '中村', '埔門', '螺鎮', '村新', '時村', '鄉高', '新都', '西路', '鮮超', '傳門', '鎮美', '馬公', '苑門', '大學', '永康', '鄉南', '里新', '仙門', '林超', '成門', '圍魚', '療門', '吉村', '學門', '岐超', '生路', '康超', '鄉後', '華門', '村盛', '池門', '中壢', '山門', '埔榮', '專前', '零售', '會門', '安里', '好超', '寶門', '巢鄉', '福門', '林縣', '東路', '嘉義', '第一', '里環', '青超', '台中', '集鎮', '玉田', '上鄉', '村南', '鄉新', '冠門', '路舊', '宜蘭', '仁門', '第二', '訓門', '上村', '美村', '豊里', '青門', '洲門', '泰門', '中門', '藥門', '金門', '洋門', '鎮環', '綜合', '斗六', '產品', '鄰新', '花蓮', '縣新', '購門', '興里', '昌門', '花門', '運門', '竹北', '欣超', '新竹', '朴子', '廣門', '美門', '降門', '村村', '德門', '果菜', '多摩', '臺南', '鄉中', '冠超', '鎮元', '台南', '樂村', '堂村', '鎮新', '大門', '份門', '文山', '燕村', '豐原', '豐里', '勝門', '大超', '心門', '里西', '太平', '園門', '山村', '臺中', '鳳山', '後村', '南環', '河鎮', '園超', '民超', '樹門', '境門', '台東', '楊梅', '林門', '內埔', '二段', '八德', '嵐門', '寮門', '平鎮', '民生', '豐門', '禮門', '村米', '彰化', '學都', '鎮中', '里美', '督門', '基隆', '新營', '慶門', '尾門', '海門', '屏東', '祥門', '台北', '山路', '桃園', '軒門', '南興', '公有', '街新', '鎮西', '會超', '太保', '興門', '大成', '梅鎮', '雅村', '路新']
    # products = ["VivoBook Pro 15", "ROG Zephyrus S17"]

    timeframes = ["Monthly", "Quarterly"]
    # New data for the dropdowns
    years = []
    quarters = []
    months = []

    return render_template('repeated_purchases.html', cities=cities, timeframes=timeframes, years=years, quarters=quarters, months=months)

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
            geojson_data = query_monthly(int(year),quarter[1],[months.index(month)+1,product_id])
        case 'Quarterly':
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


@app.route('/update_map_net_sc', methods=['POST'])
def update_map_net_sc():
    data = request.json
    print("Received data:", data)  # This line prints the received data to the console
    customer = data.get('customer')
    timeframe = data.get('timeframe')
    year = data.get('year')  # New field for Year
    quarter = data.get('quarter')  # New field for Quarter
    month = data.get('month')  # New field for Month
    selected_supplier_id = data.get('supplier_id')

    # Fetch GeoJSON
    url = 'https://api.maptiler.com/data/d3cd5f06-97f4-4333-9444-b62dd7f16f6c/features.json?key=uIMFZoCyLmKWTvmPj2JG'
    response = requests.get(url)
    geojson_data = response.json()

    suppliers_data = []
    customers_data = []

    for feature in geojson_data['features']:
        supplier = feature['properties']['Supplier']
        customer_id = feature['properties']['Customer ID']

        if supplier != "NA" and (selected_supplier_id == "All" or supplier == selected_supplier_id):
            suppliers_data.append(feature)
        elif customer_id != "NA":
            feature['properties']['Customer ID']=customer
            customers_data.append(feature)
            #print(customers_data)
    # Prepare and return the response data
    response_data = {
        'status': 'success',
        'suppliers': suppliers_data,
        'customers': customers_data
    }
    #print(response_data)
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
    resdict = {
        "nodes": 
        [
            {"id": "eBRIejoRT3q3.bSthUA9", "type": ["User"] ,"element_id": "8217280"}, 
            {"datetime": "2012-06-15 22:34:00.000", "id": "39218011", "parent_ord_num": "RM1206150031411", "type": ["ParentOrder"], "element_id": "8217279"}, 
            {"ship_method": "倉出", "id": "RS1206150047841", "type": ["Order"], "element_id": "8217278"}, 
            {"name": "Delonghi 迪朗奇多功能磨豆機 KG40", "id": "7320052", "type": ["Product"], "element_id": "9761"}, 
            {"name": "新各界企業有限公司", "id": "505", "type": ["Supplier"], "element_id": "13"}, 
            {"datetime": "2012-06-15 22:34:00.000", "id": "39218011", "parent_ord_num": "RM1206150031412", "type": ["ParentOrder"], "element_id": "8217282"}, 
            {"ship_method": "倉出", "id": "RS1206150047842", "type": ["Order"], "element_id": "8217281"}, 
            {"name": "迪朗奇義式濃縮半自動咖啡機 EC155", "id": "7320016", "type": ["Product"], "element_id": "9760"}
        ], 
        "relationships": 
        [
            {"type": "ORDERED", "nodes": ["8217280", "8217279"], "element_id": "9760"}, 
            {"type": "INCLUDE", "nodes": ["8217279", "8217278"], "element_id": "9760"}, 
            {"type": "CONTAIN", "nodes": ["8217278", "9761"], "element_id": "9760"}, 
            {"type": "PRODUCES", "nodes": ["9761", "13"], "element_id": "9760"}, 
            {"type": "ORDERED", "nodes": ["8217280", "8217282"], "element_id": "9760"}, 
            {"type": "INCLUDE", "nodes": ["8217282", "8217281"], "element_id": "9760"}, 
            {"type": "CONTAIN", "nodes": ["8217281", "9760"], "element_id": "9760"}, 
            {"type": "PRODUCES", "nodes": ["9760", "13"], "element_id": "9760"}
        ]
    }

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
            "group": node["type"][0],
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
    app.run(debug=True)