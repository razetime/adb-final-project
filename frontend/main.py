from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('repeated_purchases.html')

@app.route('/get_data')
def get_data():
    # Placeholder function to fetch data
    # Replace with your actual data fetching logic
    data = {'example': 'data'}
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)