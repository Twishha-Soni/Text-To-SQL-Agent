BUSINESS_RULES_DOCS = [
    {
        "id": "on_time_delivery",
        "text": (
            "An order is considered on-time if order_delivered_customer_date "
            "is less than or equal to order_estimated_delivery_date. Only "
            "orders with order_status = 'delivered' should be included in "
            "delivery-time or on-time-rate calculations — do not rely on "
            "NULL timestamps to implicitly filter."
        ),
    },
    {
        "id": "unique_customers",
        "text": (
            "To count unique or distinct customers, always use "
            "customer_unique_id, never customer_id. customer_id is "
            "generated per order and does not identify a real person "
            "across multiple orders."
        ),
    },
    {
        "id": "revenue_definition",
        "text": (
            "Revenue is typically calculated as SUM(price) from "
            "order_items, excluding freight_value, and typically excludes "
            "orders with order_status IN ('canceled', 'unavailable'). "
            "State explicitly whether freight is included when reporting revenue."
        ),
    },
    {
        "id": "payment_totals",
        "text": (
            "An order can have multiple rows in order_payments due to "
            "installment or split payments. Always GROUP BY order_id and "
            "SUM(payment_value) when computing what a customer paid for "
            "a single order — do not assume one row per order."
        ),
    },
]