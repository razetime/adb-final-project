from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/repeated_purchases')
def repeated_purchases():
    cities = ["Kaohsiung", "New Taipei", "Taichung", "Tainan", "Taipei", "Taoyuan", "Chiayi", "Hsinchu", "Keelung", "Changhua", "Douliu", "Hualien", "Magong", "Miaoli", "Nantou", "Pingtung", "Puzi", "Taibao", "Taitung", "Toufen", "Yilan", "Yuanlin", "Zhubei"]
    suppliers = ["Asus", "Acer"]
    products = ["VivoBook Pro 15", "ROG Zephyrus S17"]
    timeframes = ["Monthly", "Quarterly", "Yearly"]

    return render_template('repeated_purchases.html', cities=cities, suppliers=suppliers, products=products, timeframes=timeframes)

@app.route('/get_products', methods=['POST'])
def get_products():
    supplier = request.json.get('supplier')
    products = []
    if supplier == "Asus":
        products = ["VivoBook Pro 15", "ROG Zephyrus S17"]
    elif supplier == "Acer":
        products = ["Swift Go 14", "Predator Helios 16"]
    return jsonify(products=products)

@app.route('/supplier_customer_relationships')
def supplier_customer_relationships():
    suppliers = ["Asus", "Acer"]
    return render_template('supplier_customer_relationships.html', suppliers=suppliers)

@app.route('/time_series_analysis')
def time_series_analysis():
    suppliers = ["Asus", "Acer"]
    products = ["VivoBook Pro 15", "ROG Zephyrus S17"]
    timeframes = ["Daily", "Monthly", "Quarterly", "Yearly"]

    return render_template('time_series_analysis.html', suppliers=suppliers, products=products, timeframes=timeframes)

@app.route('/update_map_repeated_purchases', methods=['POST'])
def update_map_repeated_purchases():
    data = request.json
    print("Received data:", data)  # This line prints the received data to the console
    city = data.get('city')
    supplier = data.get('supplier')
    product = data.get('product')
    timeframe = data.get('timeframe')

    # Process the data and prepare the response
    # This is where you'll implement the logic to update the map
    # For now, we'll just return the received data
    response_data = {
        'status': 'success',
        'received': data
    }
    return jsonify(response_data)

@app.route('/update_map_net_sc', methods=['POST'])
def update_map_net_sc():
    data = request.json
    print("Received data:", data)  # This line prints the received data to the console
    customer = data.get('customer')
    supplier = data.get('supplier')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    # Process the data and prepare the response
    # This is where you'll implement the logic to update the map
    # For now, we'll just return the received data
    response_data = {
        'status': 'success',
        'received': data
    }
    return jsonify(response_data)

@app.route('/get_network_data', methods=['POST'])
def get_network_data():
    data = request.json
    customer = data.get('customer')
    supplier = data.get('supplier')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    # Generate nodes and links based on the supplier
    # For now, this is just a simple example
    nodes = [{"id": supplier}]
    links = []

    # Example: Generate random nodes and links
    for i in range(1, 5):  # Change 5 to the desired number of nodes
        product_name = f"Product{i}"
        nodes.append({"id": product_name})
        links.append({"source": supplier, "target": product_name, "value": random.randint(10, 100)})

    return jsonify({"nodes": nodes, "links": links})

@app.route('/get_time_series_data', methods=['POST'])
def get_time_series_data():
    data = request.json
    print("Received data:", data)
    supplier = data.get('supplier')
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