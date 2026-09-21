import os

from qdrant_client import QdrantClient
import voyageai


CONN_PARAMS = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD')
}

def vo_client():
    return voyageai.Client(api_key=os.getenv('VOYAGE_API_KEY'))

def qdrant_db_client():
    return QdrantClient(url=os.getenv('QDRANT_URL', 'http://localhost:6333'))