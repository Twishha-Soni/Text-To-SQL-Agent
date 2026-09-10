import os
from typing import Any
import uuid

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
import voyageai

from rag.business_rules_docs import BUSINESS_RULES_DOCS
from rag.schema_docs import SCHEMA_DOCS

load_dotenv()

VOYAGE_MODEL = os.getenv('VOYAGE_MODEL')
EMBED_DIM: Any = os.getenv('EMBEDDING_DIMENSION')

vo_client = voyageai.Client(api_key=os.getenv('VOYAGE_API_KEY')) # type: ignore
qdrant = QdrantClient(url=os.getenv('QDRANT_URL', 'http://localhost:6333'))


def embed_texts(texts: list[str]) -> list[list[float]]:
    result = vo_client.embed(texts, model=VOYAGE_MODEL, input_type='document')
    return result.embeddings

def ingest_collection(collection_name: str, docs: list[dict]):
    qdrant.recreate_collection(
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

    qdrant.upsert(collection_name=collection_name, points=points)
    print(f"  ingested {len(points)} docs into '{collection_name}'")

def main():
    ingest_collection('schema_docs', SCHEMA_DOCS)
    ingest_collection('business_rules_docs', BUSINESS_RULES_DOCS)
    print("Done.")

if __name__ == "__main__":
    main()