from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone,timedelta
from sqlalchemy import func

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def get_low_stock_alerts(company_id):
    try:
        # 1. Define 'Recent' timeframe (30 days)
        recent_threshold_date = datetime.now(timezone.utc) - timedelta(days=30)

        # 2. Subquery: Identify products with recent sales for this company
        # This satisfies the "Only alert for products with recent sales activity" rule
        recently_sold_subquery = db.session.query(order_items.product_id) \
            .join(orders, order_items.order_id == orders.id) \
            .filter(orders.company_id == company_id) \
            .filter(orders.created_at >= recent_threshold_date) \
            .distinct().subquery()

        # 3. Main Query: Join Inventory, Products, Warehouses, and Suppliers
        # We filter by company_id through the warehouse link
        query = db.session.query(
            inventory.product_id,
            products.name.label('product_name'),
            products.sku,
            inventory.warehouse_id,
            warehouses.name.label('warehouse_name'),
            inventory.quantity.label('current_stock'),
            products.min_stock_level.label('threshold'), # Assuming this field exists
            suppliers.id.label('supplier_id'),
            suppliers.name.label('supplier_name'),
            suppliers.contact_info.label('supplier_contact')
        ).join(products, inventory.product_id == products.id) \
         .join(warehouses, inventory.warehouse_id == warehouses.id) \
         .outerjoin(supplier_products, products.id == supplier_products.product_id) \
         .outerjoin(suppliers, supplier_products.supplier_id == suppliers.id) \
         .filter(warehouses.company_id == company_id) \
         .filter(inventory.product_id.in_(recently_sold_subquery)) \
         .filter(inventory.quantity <= products.min_stock_level)

        results = query.all()

        alerts = []
        for row in results:
            # 4. Logic for 'Days Until Stockout'
            # Calculate avg daily sales over 30 days to project remaining time
            total_sold = db.session.query(func.sum(order_items.quantity)) \
                .join(orders) \
                .filter(order_items.product_id == row.product_id) \
                .filter(orders.created_at >= recent_threshold_date).scalar() or 0
            
            avg_daily_sales = total_sold / 30
            days_left = int(row.current_stock / avg_daily_sales) if avg_daily_sales > 0 else 999

            alerts.append({
                "product_id": row.product_id,
                "product_name": row.product_name,
                "sku": row.sku,
                "warehouse_id": row.warehouse_id,
                "warehouse_name": row.warehouse_name,
                "current_stock": row.current_stock,
                "threshold": row.threshold,
                "days_until_stockout": days_left,
                "supplier": {
                    "id": row.supplier_id,
                    "name": row.supplier_name,
                    "contact_email": row.supplier_contact # Assuming email is in contact_info
                }
            })

        return jsonify({
            "alerts": alerts,
            "total_alerts": len(alerts)
        }), 200

    except Exception as e:
        # Edge Case: Database connection issues or internal logic errors
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)