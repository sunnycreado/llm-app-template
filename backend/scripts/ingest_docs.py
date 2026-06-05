"""
Ingests documents into Qdrant for RAG.

Usage:
    python backend/scripts/ingest_docs.py
    python backend/scripts/ingest_docs.py --path ./my-docs --collection my-collection

Supported file types: .txt, .md
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.ingestion import ingest_directory


async def main(folder: Path, collection: str):
    if not folder.exists():
        print(f"Error: path '{folder}' does not exist.")
        sys.exit(1)

    if not folder.is_dir():
        print(f"Error: '{folder}' is not a directory.")
        sys.exit(1)

    print(f"Ingesting documents from: {folder}")
    print(f"Target collection: {collection}\n")

    await ingest_directory(folder, collection)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents into Qdrant.")
    parser.add_argument("--path", type=Path, default=Path("./docs"), help="Folder to ingest")
    parser.add_argument("--collection", type=str, default=None, help="Qdrant collection name")
    args = parser.parse_args()

    from app.config import settings
    collection = args.collection or settings.qdrant_collection

    asyncio.run(main(args.path, collection))
