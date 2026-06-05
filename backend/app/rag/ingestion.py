import uuid
from pathlib import Path

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import settings
from app.llm.embeddings import NIMEmbeddings

CHUNK_SIZE = 512
CHUNK_OVERLAP = 64
VECTOR_SIZE = 1024  # nvidia/nv-embedqa-e5-v5 output dimension


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


async def ensure_collection(client: AsyncQdrantClient, collection: str):
    """Create collection if it does not exist."""
    existing = await client.get_collections()
    names = [c.name for c in existing.collections]
    if collection not in names:
        await client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


async def ingest_file(path: Path, collection: str = settings.qdrant_collection):
    """Chunk, embed, and upsert a single file into Qdrant."""
    embeddings = NIMEmbeddings()
    client = AsyncQdrantClient(url=settings.qdrant_url)

    await ensure_collection(client, collection)

    text = path.read_text(encoding="utf-8")
    chunks = chunk_text(text)

    if not chunks:
        print(f"  Skipped {path.name} — no content after chunking")
        return

    print(f"  Embedding {len(chunks)} chunks from {path.name}...")
    vectors = await embeddings.embed(chunks)

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vectors[i],
            payload={
                "text": chunks[i],
                "source": str(path),
                "filename": path.name,
                "chunk_index": i,
            },
        )
        for i in range(len(chunks))
    ]

    await client.upsert(collection_name=collection, points=points)
    print(f"  ✓ Ingested {len(points)} chunks from {path.name}")
    await client.close()


async def ingest_directory(folder: Path, collection: str = settings.qdrant_collection):
    """Ingest all supported files in a directory recursively."""
    extensions = ["*.txt", "*.md"]
    files = []
    for ext in extensions:
        files.extend(folder.glob(f"**/{ext}"))

    if not files:
        print(f"No supported files found in {folder}")
        return

    for file in files:
        await ingest_file(file, collection)

    print(f"\nDone — ingested {len(files)} file(s) into collection '{collection}'")
