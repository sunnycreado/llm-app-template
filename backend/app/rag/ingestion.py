from pathlib import Path
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from app.config import settings
from app.llm.embeddings import NIMEmbeddings


CHUNK_SIZE = 512
CHUNK_OVERLAP = 64


def chunk_text(text: str) -> list[str]:
    chunks, start = [], 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


async def ingest_file(path: Path, collection: str = settings.qdrant_collection):
    embeddings = NIMEmbeddings()
    client = AsyncQdrantClient(url=settings.qdrant_url)

    # Ensure collection exists
    existing = [c.name for c in await client.get_collections().then(lambda r: r.collections)]
    if collection not in existing:
        await client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )

    text = path.read_text(encoding="utf-8")
    chunks = chunk_text(text)
    vectors = await embeddings.embed(chunks)

    points = [
        PointStruct(
            id=i,
            vector=vectors[i],
            payload={"text": chunks[i], "source": str(path)},
        )
        for i in range(len(chunks))
    ]

    await client.upsert(collection_name=collection, points=points)
    print(f"Ingested {len(points)} chunks from {path.name}")
