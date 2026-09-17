CREATE TABLE customers (
    customer_id VARCHAR(32) PRIMARY KEY,
    customer_unique_id VARCHAR(32) NOT NULL,
    customer_zip_code_prefix VARCHAR(5),
    customer_city VARCHAR(100),
    customer_state VARCHAR(2)
);

CREATE INDEX idx__customers_unique_id ON customers(customer_unique_id);

CREATE TABLE products (
    product_id VARCHAR(32) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_name_length INT,
    product_description_length INT,
    product_photos_qty INT,
    product_weight_g INT,
    product_length_cm INT,
    product_height_cm INT,
    product_width_cm INT
);

CREATE TABLE orders (
    order_id VARCHAR(32) PRIMARY KEY,
    customer_id VARCHAR(32) NOT NULL,
    order_status VARCHAR(20) NOT NULL CHECK (
        order_status IN ('created', 'approved', 'invoiced', 'processing', 'shipped', 'delivered', 'canceled', 'unavailable')
    ),
    order_purchase_timestamp TIMESTAMP NOT NULL,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_order_status ON orders(order_status);

CREATE TABLE order_items (
    order_id VARCHAR(32) NOT NULL,
    order_item_id INT NOT NULL,
    product_id VARCHAR(32) NOT NULL,
    seller_id VARCHAR(32) NOT NULL,
    shipping_limit_date TIMESTAMP NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    freight_value DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (order_id, order_item_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE INDEX idx_order_items_product_id ON order_items(product_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);

CREATE TABLE order_payments (
    order_id VARCHAR(32) NOT NULL,
    payment_sequential INT NOT NULL,
    payment_type VARCHAR(20) NOT NULL CHECK (
        payment_type IN ('credit_card', 'boleto', 'voucher', 'debit_card', 'not_defined')
    ),
    payment_installments INT NOT NULL,
    payment_value DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (order_id, payment_sequential),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE INDEX idx_order_payments_order_id ON order_payments(order_id);