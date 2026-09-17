import os
from dotenv import load_dotenv
from app.db.connect import vo_client, qdrant_db_client

load_dotenv()

VOYAGE_MODEL = os.getenv('VOYAGE_MODEL')
TOP_K = 3


def embed_query(text: str) -> list[float]:
    result = vo_client().embed([text], model=VOYAGE_MODEL, input_type='query')
    return result.embeddings[0]

def search_collection(collection_name: str, query_vector: list[float], top_k: int = TOP_K) -> list[str]:
    hits = qdrant_db_client().query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k
    ).points

    return [hit.payload['text'] for hit in hits]

def retrieve_context(question: str) -> dict:
    query_vector = embed_query(question)
    schema_context = search_collection('schema_docs', query_vector)
    rules_context = search_collection('business_rules_docs', query_vector)

    return {
        'schema_context': schema_context,
        'rules_context': rules_context
    }