from flask import Flask, render_template, request, jsonify
import random
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/repeated_purchases')
def repeated_purchases():
    cities = ["Kaohsiung", "New Taipei", "Taichung", "Tainan", "Taipei", "Taoyuan", "Chiayi", "Hsinchu", "Keelung", "Changhua", "Douliu", "Hualien", "Magong", "Miaoli", "Nantou", "Pingtung", "Puzi", "Taibao", "Taitung", "Toufen", "Yilan", "Yuanlin", "Zhubei"]
    products = []
    timeframes = ["Monthly", "Quarterly", "Yearly"]
    # New data for the dropdowns
    years = []
    quarters = []
    months = []

    return render_template('repeated_purchases.html', cities=cities, products=products, timeframes=timeframes, years=years, quarters=quarters, months=months)

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
    suppliers = ["All", "Asus", "Acer"]
    products = []
    timeframes = ["Daily", "Monthly", "Quarterly", "Yearly"]

    return render_template('time_series_analysis.html', suppliers=suppliers, products=products, timeframes=timeframes)

@app.route('/update_map_repeated_purchases', methods=['POST'])
def update_map_repeated_purchases():
    data = request.json
    print("Received data:", data)  # This line prints the received data to the console
    city = data.get('city')
    supplier_id = data.get('supplier_id')  # New field for Supplier ID
    product = data.get('product')
    timeframe = data.get('timeframe')
    year = data.get('year')  # New field for Year
    quarter = data.get('quarter')  # New field for Quarter
    month = data.get('month')  # New field for Month

    # Fetch GeoJSON
    url = 'https://api.maptiler.com/data/09e09097-be00-42f9-ae5e-af6db6815443/features.json?key=uIMFZoCyLmKWTvmPj2JG'
    response = requests.get(url)
    geojson_data = response.json()

    # Process GeoJSON
    processed_data = []
    for feature in geojson_data['features']:
        district = feature['properties']['District']
        repeated_purchases = feature['properties']['Repeated Purchases']
        coordinates = feature['geometry']['coordinates']

        processed_data.append({
            'district': district,
            'repeated_purchases': repeated_purchases,
            'coordinates': coordinates
        })

    # Calculate min and max repeated purchases
    min_purchases = min(int(feature['properties']['Repeated Purchases']) for feature in geojson_data['features'])
    max_purchases = max(int(feature['properties']['Repeated Purchases']) for feature in geojson_data['features'])

    # Prepare and return the response data
    response_data = {
        'status': 'success',
        'received': data,  # Includes the data received from the AJAX request
        'processed': processed_data,  # The processed GeoJSON data
        'min_purchases': min_purchases,  # Minimum repeated purchases value
        'max_purchases': max_purchases   # Maximum repeated purchases value
    }
    return jsonify(response_data)


@app.route('/update_map_net_sc', methods=['POST'])
def update_map_net_sc():
    data = request.json
    print("Received data:", data)  # This line prints the received data to the console
    customer = data.get('customer')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
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
            print(customers_data)
    # Prepare and return the response data
    response_data = {
        'status': 'success',
        'suppliers': suppliers_data,
        'customers': customers_data
    }
    print(response_data)
    return jsonify(response_data)

@app.route('/get_network_data', methods=['POST'])
def get_network_data():
    data = request.json
    customer = data.get('customer')
    supplier_id = data.get('supplier_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    # Sample data resembling the output of a Neo4J query
    # resdict = {
    #     'nodes': [
    #         {'sub_ord': 'RS1201200001022', 'id': 'RM1201200000625', 
    #         'del_adr': '彰化縣社頭鄉崙雅村員集路一段800號', 'user': 'uNgJ6jJKw3pXIV569_pT_oQ-', 
    #         'type': frozenset({'Order'}), 'element_id': '2854406'}, 
    #         {'seller': '1012', 'name': 'CASIO 光動能輕薄型數位錶-金/39mm', 'id': '7290239', 
    #         'type': frozenset({'Product'}), 'element_id': '36277'}, 
    #         {'sub_ord': 'RS1201190021195', 'id': 'RM1201190013732', 
    #         'del_adr': '台中市西屯區天水西街22號', 'user': 'Qo03MTjI1ws2wPVBgfrJvyQ-', 
    #         'type': frozenset({'Order'}), 'element_id': '2437236'}, 
    #         {'sub_ord': 'RS1201170012941', 'id': 'RM1201170008562', 
    #         'del_adr': '桃園縣中壢市普義路217巷17號10樓', 'user': 'K875ScIYgwvIPD4MjmT0Tw--', 
    #         'type': frozenset({'Order'}), 'element_id': '1711970'}, 
    #         {'sub_ord': 'RS1201230004980', 'id': 'RM1201230003591', 
    #         'del_adr': '台北市萬華區北市萬大路423巷45弄4號1樓', 'user': 'oUgXSdUS4n9ecf8saA--', 
    #         'type': frozenset({'Order'}), 'element_id': '2246465'}, 
    #         {'seller': '1012', 'name': 'CASIO 光動能輕薄型數位錶-39mm', 'id': '7290497', 
    #         'type': frozenset({'Product'}), 'element_id': '36289'}, 
    #         {'sub_ord': 'RS1201210000631', 'id': 'RM1201210000452', 
    #         'del_adr': '台中市西區府後街1號6F-1', 'user': 'I6Txu80lg30t6aYbnEE-', 
    #         'type': frozenset({'Order'}), 'element_id': '1500088'}, 
    #         {'sub_ord': 'RS1201230021314', 'id': 'RM1201230014899', 
    #         'del_adr': '彰化縣彰化市長順街40-2號', 'user': 'E5qLm9Og9QENDKDaG7VfSLA-', 
    #         'type': frozenset({'Order'}), 'element_id': '1079963'}
    #     ],
    #     'relationships': [
    #         {'type': 'PRODUCT', 'nodes': ['2854406', '36277'], 'element_id': '1079963'}, 
    #         {'type': 'PRODUCT', 'nodes': ['2437236', '36277'], 'element_id': '1079963'}, 
    #         {'type': 'PRODUCT', 'nodes': ['1711970', '36277'], 'element_id': '1079963'}, 
    #         {'type': 'PRODUCT', 'nodes': ['2246465', '36289'], 'element_id': '1079963'}, 
    #         {'type': 'PRODUCT', 'nodes': ['1500088', '36289'], 'element_id': '1079963'}, 
    #         {'type': 'PRODUCT', 'nodes': ['1079963', '36289'], 'element_id': '1079963'}
    #     ]
    # }
    # Generate nodes and links based on the supplier
    # For now, this is just a simple example
    nodes = [{"id": supplier_id}]
    links = []

    # Example: Generate random nodes and links
    for i in range(1, 5):  # Change 5 to the desired number of nodes
        product_name = f"Product{i}"
        nodes.append({"id": product_name})
        links.append({"source": supplier_id, "target": product_name, "value": random.randint(10, 100)})
    # Assuming resdict is already defined or received from another source
    #nodes, links = process_data_for_graph(resdict)

    return jsonify({"nodes": nodes, "links": links})

# #Function that will process the data coming from Neo4J
# def process_data_for_graph(resdict):
#     # Extract nodes
#     nodes = resdict["nodes"]

#     # Extract relationships
#     links = []
#     for relation in resdict["relationships"]:
#         link = {
#             "source": relation["nodes"][0],  # Assuming first element is the source
#             "target": relation["nodes"][1],  # Assuming second element is the target
#             "type": relation["type"],        # Type of relationship
#             "value": random.randint(10, 100) # You can customize this value
#         }
#         links.append(link)

#     return nodes, links

@app.route('/get_time_series_data', methods=['POST'])
def get_time_series_data():
    data = request.json
    print("Received data:", data)
    supplier_id = data.get('supplier_id')
    product = data.get('product')
    timeframe = data.get('timeframe')

    # Generate time series data based on the timeframe
    if timeframe == 'Daily':
        labels = [f'Day {i+1}' for i in range(31)]
    elif timeframe == 'Monthly':
        labels = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    elif timeframe == 'Quarterly':
        labels = [f'Q{i+1}' for i in range(12)]
    elif timeframe == 'Yearly':
        labels = [f'Year {2000+i}' for i in range(12)]
    
    data = [random.randint(100, 500) for _ in labels]  # Random data for illustration

    return jsonify({'labels': labels, 'data': data})


if __name__ == '__main__':
    app.run(debug=True)