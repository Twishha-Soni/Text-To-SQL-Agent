import csv
import os
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extras import execute_values #type: ignore
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).parent.parent / 'data'

CONN_PARAMS: dict[str, Any] = {
    'host': os.getenv('POSTGRES_HOST', 'postgres'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD')
}

def clean_value(value: str | None):
    if value is None or value == "":
        return None
    return value

def load_csv(conn: Any, csv_path: Path, table: str, columns: list[str], batch_size: int = 5000):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows: list[Any] = []
        total = 0
        with conn.cursor() as cur:
            insert_sql = f"""
                INSERT INTO {table} ({", ".join(columns)})
                VALUES %s
                ON CONFLICT DO NOTHING
            """
            for row in reader:
                rows.append(tuple(clean_value(row[col]) for col in columns))
                if len(rows) >= batch_size:
                    execute_values(cur, insert_sql, rows)
                    total += len(rows)
                    rows = []
            if rows:
                execute_values(cur, insert_sql, rows)
                total += len(rows)
        conn.commit()
    print(f"  loaded {total} rows into {table}")


def main():
    conn: Any = psycopg2.connect(**CONN_PARAMS)

    # order matters - hence parent before children
    load_csv(
        conn, DATA_DIR / 'olist_customers_dataset.csv', 'customers', 
        ["customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"]
    )
    load_csv(
        conn, DATA_DIR / 'olist_products_dataset.csv', 'products', 
        ["product_id", "product_category_name", "product_name_length", "product_description_length", "product_photos_qty", "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]
    )
    load_csv(
        conn, DATA_DIR / 'olist_orders_dataset.csv', 'orders', 
        ["order_id", "customer_id", "order_status", "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]
    )
    load_csv(
        conn, DATA_DIR / 'olist_order_items_dataset.csv', 'order_items', 
        ["order_id", "order_item_id", "product_id", "seller_id", "shipping_limit_date", "price", "freight_value"]
    )
    load_csv(
        conn, DATA_DIR / 'olist_order_payments_dataset.csv', 'order_payments', 
        ["order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"]
    )

    conn.close()
    print('Done')



if __name__ == '__main__':
    main()