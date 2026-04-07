CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,  -- Company name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP --Company creation timestamp
);

CREATE TABLE warehouses (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL,  --Referencing the company that owns the warehouse
    name VARCHAR(255),      -- Warehouse name
    location TEXT,         --warehouse location details
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- Warehouse creation timestamp
    FOREIGN KEY (company_id) REFERENCES companies(id)  
);
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,   --Product name
    sku VARCHAR(100) UNIQUE NOT NULL,  --Stock Keeping Unit
    price DECIMAL(10,2) NOT NULL,   
    is_bundle BOOLEAN DEFAULT FALSE,  --is it a bundle or not
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--This tracks how much quantity of each product is available in each warehouse. 
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,     --Referencing a product
    warehouse_id INT NOT NULL,    --Refrencing a warehouse
    quantity INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (product_id, warehouse_id),

    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
);

CREATE TABLE inventory_logs (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,   --Referencing a product
    warehouse_id INT NOT NULL,  --Referencing a warehouse
    change INT NOT NULL,        --how much the quantity changed
    new_quantity INT NOT NULL,
    reason VARCHAR(255), -- sale, restock, adjustment
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
);

CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_info TEXT
);

CREATE TABLE supplier_products (
    id SERIAL PRIMARY KEY,
    supplier_id INT NOT NULL,  
    product_id INT NOT NULL,  --Referencing a product that the supplier provides
    cost_price DECIMAL(10,2),  --The price at which the supplier sells the product

    UNIQUE (supplier_id, product_id),

    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
--Self Referencing structure to show that a product can be a bundle of other products.
CREATE TABLE product_bundles (
    id SERIAL PRIMARY KEY,
    bundle_id INT NOT NULL,  
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,

    FOREIGN KEY (bundle_id) REFERENCES products(id),
    FOREIGN KEY (product_id) REFERENCES products(id),

    UNIQUE (bundle_id, product_id)
);

--Customer Orders
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL,             --Referencing the company that the order belongs to
    customer_name VARCHAR(255) NOT NULL,  --Customer name
    status VARCHAR(50) DEFAULT 'pending',  --Order Status
    total_amount DECIMAL(10,2),             --Total order amount
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,      --Referencing the order that this item belongs to
    product_id INT NOT NULL,     --Referencing the product that was ordered
    quantity INT NOT NULL,       --Quantity of the product ordered
    price DECIMAL(10,2),           --Price at the time of order (can be different from current product price)
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);