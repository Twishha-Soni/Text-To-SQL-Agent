import os
from typing import Any
import uuid

from dotenv import load_dotenv
from qdrant_client.models import Distance, PointStruct, VectorParams

from backend.app.service.sub_agent_1.rag.business_rules_docs import BUSINESS_RULES_DOCS
from backend.app.service.sub_agent_1.rag.schema_docs import SCHEMA_DOCS
from app.database.connect import vo_client, qdrant_db_client

load_dotenv()

VOYAGE_MODEL = os.getenv('VOYAGE_MODEL')
EMBED_DIM: Any = os.getenv('EMBEDDING_DIMENSION')


def embed_texts(texts: list[str]) -> list[list[float]]:
    result = vo_client().embed(texts, model=VOYAGE_MODEL, input_type='document')
    return result.embeddings

def ingest_collection(collection_name: str, docs: list[dict]):
    qdrant_db_client().recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE)
    )

    texts: list[str] = [d['text'] for d in docs]
    vectors = embed_texts(texts)

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                'doc_id': doc['id'],
                'text': doc['text'],
                
            }
        )
        for doc, vector in zip(docs, vectors)
    ]

    qdrant_db_client().upsert(collection_name=collection_name, points=points)
    print(f"  ingested {len(points)} docs into '{collection_name}'")

def main():
    ingest_collection('schema_docs', SCHEMA_DOCS)
    ingest_collection('business_rules_docs', BUSINESS_RULES_DOCS)
    print("Done.")

if __name__ == "__main__":
    main()