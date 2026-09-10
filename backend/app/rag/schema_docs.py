SCHEMA_DOCS = [
    {
        "id": "customers",
        "text": (
            "Table: customers. Columns: customer_id (per-order anonymized ID, "
            "NOT unique per person), customer_unique_id (the real repeat-buyer "
            "identity — use this to count distinct customers), "
            "customer_zip_code_prefix, customer_city, customer_state."
        ),
    },
    {
        "id": "products",
        "text": (
            "Table: products. Columns: product_id, product_category_name "
            "(in Portuguese), product_weight_g, product_length_cm, "
            "product_height_cm, product_width_cm, product_photos_qty."
        ),
    },
    {
        "id": "orders",
        "text": (
            "Table: orders. Columns: order_id, customer_id (FK to customers), "
            "order_status (one of: delivered, invoiced, shipped, processing, "
            "unavailable, canceled, created, approved), "
            "order_purchase_timestamp, order_approved_at (nullable), "
            "order_delivered_carrier_date (nullable), "
            "order_delivered_customer_date (nullable — NULL means not yet "
            "delivered), order_estimated_delivery_date."
        ),
    },
    {
        "id": "order_items",
        "text": (
            "Table: order_items. Columns: order_id (FK), order_item_id "
            "(sequence number within the order, not globally unique), "
            "product_id (FK), seller_id (no sellers table exists), price "
            "(item price only), freight_value (shipping cost, separate from "
            "price). Primary key is (order_id, order_item_id)."
        ),
    },
    {
        "id": "order_payments",
        "text": (
            "Table: order_payments. Columns: order_id (FK), "
            "payment_sequential (an order can have MULTIPLE payment rows — "
            "split/installment payments), payment_type (credit_card, boleto, "
            "voucher, debit_card, not_defined), payment_installments, "
            "payment_value. Sum payment_value grouped by order_id to get "
            "total paid per order."
        ),
    },
]