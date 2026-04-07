from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

# ISSUE-1 FIX: Proper DB config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ISSUE-4 FIX: Removed warehouse_id from Product
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    sku = db.Column(db.String, unique=True, nullable=False)  # ISSUE-2 FIX
    price = db.Column(db.Float, nullable=False)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    warehouse_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

@app.route('/api/products', methods=['POST'])
def create_product():

    # ISSUE-1: Content-Type validation
    if not request.is_json:
        return jsonify({"error": "Send JSON data"}), 415

    data = request.get_json()

    if not data:
        return jsonify({"error": "Empty request body"}), 400

    # ISSUE-8: Handle required fields properly
    required = ['name', 'sku', 'price']
    for field in required:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    # ISSUE-5: Validate initial_quantity
    try:
        initial_quantity = int(data.get('initial_quantity', 0))
        if initial_quantity < 0:
            return jsonify({"error": "Quantity cannot be negative"}), 400
    except:
        return jsonify({"error": "Invalid quantity"}), 400

    try:
        # Create product
        product = Product(
            name=data['name'],
            sku=data['sku'],
            price=data['price']
        )
        db.session.add(product)

        # ISSUE-3 FIX: use flush instead of commit
        db.session.flush()

        # ISSUE-8 FIX: Only create inventory if warehouse_id exists
        if data.get('warehouse_id') is not None:
            inventory = Inventory(
                product_id=product.id,
                warehouse_id=data['warehouse_id'],
                quantity=initial_quantity
            )
            db.session.add(inventory)

        # Single commit → atomic transaction
        db.session.commit()

    # ISSUE-7 FIX: specific error handling
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "SKU already exists"}), 400

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

    # ISSUE-6 FIX: Proper response + status code
    return jsonify({
        "message": "Product created",
        "product_id": product.id
    }), 201


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)