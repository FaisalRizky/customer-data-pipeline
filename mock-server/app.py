from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'customers.json')

def load_customers():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/customers', methods=['GET'])
def get_customers():
    try:
        customers = load_customers()
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": "Failed to load customers data"}), 500
    
    # Pagination
    try:
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)
        
        if page < 1: page = 1
        if limit < 1: limit = 10
        if limit > 100: limit = 100
    except (ValueError, TypeError):
        page = 1
        limit = 10

    total = len(customers)
    start = (page - 1) * limit
    end = start + limit
    
    paginated_data = customers[start:end] if start < total else []
    
    return jsonify({
        "data": paginated_data,
        "total": total,
        "page": page,
        "limit": limit
    }), 200

@app.route('/api/customers/<id>', methods=['GET'])
def get_customer(id):
    try:
        customers = load_customers()
        customer = next((c for c in customers if c['customer_id'] == id), None)
        
        if customer:
            return jsonify(customer), 200
        else:
            return jsonify({"error": "Customer not found"}), 404
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
