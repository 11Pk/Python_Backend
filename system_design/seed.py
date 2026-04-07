# Updated imports to match your new plural class names
from third import app, db, products, inventory, warehouses, companies, orders, order_items, suppliers, supplier_products
from datetime import datetime, timezone, timedelta

with app.app_context():
    # 1. Create a Company (using the plural class name 'companies')
    comp = companies(name="TechLogistics Corp")
    db.session.add(comp)
    db.session.commit() 

    # 2. Create a Warehouse (using 'warehouses')
    wh = warehouses(name="Main Hub", company_id=comp.id)
    db.session.add(wh)
    
    # 3. Create a Product (using 'products')
    prod = products(name="Widget A", sku="WID-001", price=25.0)
    prod.min_stock_level = 20 
    db.session.add(prod)
    db.session.flush()

    # 4. Add Inventory (using 'inventory')
    inv = inventory(product_id=prod.id, warehouse_id=wh.id, quantity=5)
    db.session.add(inv)

    # 5. Create a Recent Order (using 'orders' and 'order_items')
    order = orders(company_id=comp.id, customer_name="Test Buyer", created_at=datetime.now(timezone.utc))
    db.session.add(order)
    db.session.flush()

    item = order_items(order_id=order.id, product_id=prod.id, quantity=2, price=25.0)
    db.session.add(item)

    # 6. Add Supplier Info (using 'suppliers' and 'supplier_products')
    sup = suppliers(name="Supplier Corp", contact_info="orders@supplier.com")
    db.session.add(sup)
    db.session.flush()

    sup_prod = supplier_products(supplier_id=sup.id, product_id=prod.id, cost_price=15.0)
    db.session.add(sup_prod)

    db.session.commit()
    print("Database seeded successfully!")